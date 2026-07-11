from src.agent.tools import (
    list_knowledge_files,
    search_knowledge,
    get_project_status,
)
from src.memory.memory_factory import get_memory


class AgentCore:
    def __init__(
        self,
        pipeline=None,
        knowledge_dir: str = "data/knowledge/industrial",
    ):
        self.pipeline = pipeline
        self.knowledge_dir = knowledge_dir
        self.memory = get_memory()

    def select_tool(self, user_text: str) -> str:
        text = user_text.lower()

        list_keywords = [
            "有哪些文件",
            "知识库文件",
            "文档列表",
            "有哪些资料",
            "列出文件",
        ]

        status_keywords = [
            "项目状态",
            "当前状态",
            "做到哪",
            "当前能力",
            "进度",
        ]

        industrial_keywords = [
            "e01",
            "e02",
            "e03",
            "e04",
            "e05",
            "报警",
            "故障",
            "异常",
            "温度传感器",
            "光电传感器",
            "传感器",
            "感器",
            "床感器",
            "传送带",
            "电机",
            "气压",
            "气缸",
            "点检",
            "巡检",
            "检查",
            "检查项目",
            "维修",
            "更换",
            "更",
            "sop",
            "步骤",
            "准备",
            "之前",
            "注意",
            "注意什么",
            "注意事项",
            "需要注意",
            "安全",
            "断电",
            "防护",
            "气源",
        ]

        project_keywords = [
            "edgetalk",
            "项目",
            "系统",
            "功能",
            "模块",
            "fastapi",
            "rag",
            "agent",
            "memory",
            "embedding",
        ]

        if any(word in text for word in list_keywords):
            return "list_knowledge_files"

        if any(word in text for word in status_keywords):
            return "get_project_status"

        if any(word in text for word in industrial_keywords):
            return "search_knowledge"

        if any(word in text for word in project_keywords):
            return "get_project_status"

        return "chat"

    def _build_context_from_tool_result(self, tool_name: str, tool_result: dict) -> str:
        if tool_name == "list_knowledge_files":
            files = tool_result.get("files", [])
            return "\n".join(f"- {file}" for file in files)

        if tool_name == "search_knowledge":
            results = tool_result.get("results", [])
            return "\n\n".join(item.get("text", "") for item in results)

        if tool_name == "get_project_status":
            return tool_result.get("status", "")

        return ""

    def _generate_reply(self, user_text: str, context: str = "") -> str:
        if self.pipeline is None:
            if context:
                short_context = context.strip()[:600]
                return "根据知识库检索结果，相关内容如下：\n" + short_context

            return (
                "当前轻量模式未加载完整 LLM Pipeline，"
                "但 Agent、RAG 和 Memory 功能可以正常测试。"
            )

        prompt = f"""
你是 EdgeTalk 工业设备维护助手，请基于资料回答用户问题。

【用户问题】
{user_text}

【相关资料】
{context}

【回答要求】
1. 回答要简洁、准确；
2. 优先基于资料回答；
3. 如果资料不足，请说明资料不足；
4. 不要编造资料中没有的信息。
"""

        try:
            return self.pipeline.generate_reply(
                user_text=user_text,
                context=context,
            )
        except TypeError:
            try:
                return self.pipeline.generate_reply(prompt)
            except TypeError:
                return self.pipeline.generate_reply(user_text)

    def _return_with_memory(
        self,
        session_id: str,
        user_text: str,
        response: dict,
    ) -> dict:
        answer = response.get("answer", "")

        try:
            self.memory.save_message(
                session_id=session_id,
                role="user",
                content=user_text,
            )

            self.memory.save_message(
                session_id=session_id,
                role="assistant",
                content=answer,
            )
        except Exception:
            pass

        response["session_id"] = session_id
        return response

    def run(self, user_text: str, session_id: str = "default") -> dict:
        if not user_text.strip():
            response = {
                "input": user_text,
                "tool_used": "none",
                "tool_result": {},
                "answer": "输入内容不能为空。",
            }
            return self._return_with_memory(session_id, user_text, response)

        tool_name = self.select_tool(user_text)

        if tool_name == "chat":
            answer = self._generate_reply(
                user_text=user_text,
                context="",
            )

            response = {
                "input": user_text,
                "tool_used": "chat",
                "tool_result": {},
                "answer": answer,
            }

            return self._return_with_memory(session_id, user_text, response)

        if tool_name == "list_knowledge_files":
            tool_result = list_knowledge_files(
                knowledge_dir=self.knowledge_dir,
            )

            context = self._build_context_from_tool_result(
                tool_name=tool_name,
                tool_result=tool_result,
            )

            answer = self._generate_reply(
                user_text=user_text,
                context=context,
            )

            response = {
                "input": user_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "answer": answer,
            }

            return self._return_with_memory(session_id, user_text, response)

        if tool_name == "search_knowledge":
            tool_result = search_knowledge(
                query=user_text,
                knowledge_dir=self.knowledge_dir,
                top_k=1,
                min_score=0.30,
                retriever_type="embedding",
            )

            if not tool_result.get("results"):
                response = {
                    "input": user_text,
                    "tool_used": tool_name,
                    "tool_result": tool_result,
                    "answer": "知识库中没有检索到足够相关的内容。",
                }

                return self._return_with_memory(session_id, user_text, response)

            context = self._build_context_from_tool_result(
                tool_name=tool_name,
                tool_result=tool_result,
            )

            answer = self._generate_reply(
                user_text=user_text,
                context=context,
            )

            response = {
                "input": user_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "answer": answer,
            }

            return self._return_with_memory(session_id, user_text, response)

        if tool_name == "get_project_status":
            tool_result = get_project_status()

            context = self._build_context_from_tool_result(
                tool_name=tool_name,
                tool_result=tool_result,
            )

            answer = self._generate_reply(
                user_text=user_text,
                context=context,
            )

            response = {
                "input": user_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "answer": answer,
            }

            return self._return_with_memory(session_id, user_text, response)

        response = {
            "input": user_text,
            "tool_used": "unknown",
            "tool_result": {},
            "answer": "暂时无法判断应该使用哪个工具。",
        }

        return self._return_with_memory(session_id, user_text, response)
