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
        llm=None,
        knowledge_dir: str = "data/knowledge/industrial",
    ):
        self.pipeline = pipeline
        self.llm = llm
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
            "当前进度",
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
            "电",
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

    def _build_context_from_tool_result(
        self,
        tool_name: str,
        tool_result,
    ) -> str:
        if not isinstance(tool_result, dict):
            return str(tool_result or "")

        if tool_name == "list_knowledge_files":
            files = tool_result.get("files", [])

            if isinstance(files, list):
                return "\n".join(
                    str(item)
                    for item in files
                )

            return str(files)

        if tool_name == "search_knowledge":
            results = tool_result.get("results", [])

            if not isinstance(results, list):
                return ""

            context_parts = []

            for item in results:
                if not isinstance(item, dict):
                    continue

                text = item.get("text", "")

                if text:
                    context_parts.append(text)

            return "\n\n".join(context_parts)

        if tool_name == "get_project_status":
            return str(
                tool_result.get(
                    "status",
                    tool_result.get("message", ""),
                )
            )

        return ""

    def _generate_reply(
        self,
        user_text: str,
        context: str = "",
    ) -> str:
        # EdgeTalk Pro Web 模式
        # FastAPI 直接使用独立 LocalLLM
        if self.llm is not None:
            try:
                return self.llm.generate(
                    user_text=user_text,
                    context=context if context else None,
                )
            except Exception as exc:
                print(
                    f"LocalLLM generate failed: {exc}"
                )

        # 原完整语音 Pipeline 模式
        # 保留向后兼容
        if self.pipeline is not None:
            prompt = f"""
你是 EdgeTalk 工业设备维护助手，请基于资料回答用户问题。

【用户问题】
{user_text}

【相关资料】
{context}

【回答要求】
1. 回答简洁、准确；
2. 优先基于资料回答；
3. 如果资料不足，请明确说明；
4. 不要编造资料中没有的信息。
"""

            try:
                return self.pipeline.generate_reply(
                    user_text=user_text,
                    context=context,
                )
            except TypeError:
                try:
                    return self.pipeline.generate_reply(
                        prompt
                    )
                except TypeError:
                    return self.pipeline.generate_reply(
                        user_text
                    )

        # 没有任何 LLM 时保留轻量模式
        if context:
            short_context = context.strip()[:600]

            return (
                "根据知识库检索结果，相关内容如下：\n\n"
                + short_context
            )

        return (
            "当前未加载本地 LLM，"
            "但 Agent、RAG 和 Memory 功能可以正常使用。"
        )

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

        except Exception as exc:
            print(
                f"Memory save failed: {exc}"
            )

        return response

    def run(
        self,
        user_text: str,
        session_id: str = "default",
    ) -> dict:
        tool_name = self.select_tool(user_text)

        # 普通聊天
        if tool_name == "chat":
            answer = self._generate_reply(
                user_text=user_text,
            )

            response = {
                "input": user_text,
                "tool_used": "chat",
                "tool_result": {},
                "answer": answer,
                "session_id": session_id,
            }

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        # 查询知识库文件
        if tool_name == "list_knowledge_files":
            try:
                tool_result = list_knowledge_files(
                    knowledge_dir=self.knowledge_dir
                )
            except TypeError:
                tool_result = list_knowledge_files(
                    self.knowledge_dir
                )

            if not isinstance(tool_result, dict):
                tool_result = {
                    "success": True,
                    "files": tool_result,
                }

            context = self._build_context_from_tool_result(
                tool_name,
                tool_result,
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
                "session_id": session_id,
            }

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        # 查询项目状态
        if tool_name == "get_project_status":
            tool_result = get_project_status()

            if not isinstance(tool_result, dict):
                tool_result = {
                    "success": True,
                    "status": tool_result,
                }

            context = self._build_context_from_tool_result(
                tool_name,
                tool_result,
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
                "session_id": session_id,
            }

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        # 工业知识库 RAG
        if tool_name == "search_knowledge":
            try:
                tool_result = search_knowledge(
                    query=user_text,
                    knowledge_dir=self.knowledge_dir,
                    retriever_type="embedding",
                )
            except TypeError:
                try:
                    tool_result = search_knowledge(
                        user_text,
                        knowledge_dir=self.knowledge_dir,
                        retriever_type="embedding",
                    )
                except TypeError:
                    tool_result = search_knowledge(
                        user_text
                    )

            if not isinstance(tool_result, dict):
                tool_result = {
                    "success": bool(tool_result),
                    "results": tool_result or [],
                }

            context = self._build_context_from_tool_result(
                tool_name,
                tool_result,
            )

            if context:
                answer = self._generate_reply(
                    user_text=user_text,
                    context=context,
                )
            else:
                answer = (
                    "当前工业知识库中没有检索到足够相关的资料。"
                    "建议补充设备型号、故障码或具体维护问题后再试。"
                )

            response = {
                "input": user_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "answer": answer,
                "session_id": session_id,
            }

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        response = {
            "input": user_text,
            "tool_used": "unknown",
            "tool_result": {},
            "answer": "暂时无法处理该请求。",
            "session_id": session_id,
        }

        return self._return_with_memory(
            session_id=session_id,
            user_text=user_text,
            response=response,
        )
