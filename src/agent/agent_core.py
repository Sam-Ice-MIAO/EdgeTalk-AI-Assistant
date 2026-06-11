import re

from src.agent.tools import (
    list_knowledge_files,
    search_knowledge,
    get_project_status,
)
from src.memory.sqlite_memory import SQLiteMemory


class AgentCore:
    def __init__(
        self,
        pipeline=None,
        knowledge_dir: str = "data/knowledge/industrial",
    ):
        self.pipeline = pipeline
        self.knowledge_dir = knowledge_dir
        self.memory = SQLiteMemory()

    def select_tool(self, user_text: str) -> str:
        """Select a tool based on simple rule-based intent detection."""

        # 1. 查看知识库文件
        if any(word in user_text for word in ["哪些文档", "知识库文件", "文档列表", "有哪些资料"]):
            return "list_knowledge_files"

        # 2. 查看项目状态
        if any(word in user_text for word in ["项目状态", "当前状态", "做到哪", "当前能力"]):
            return "get_project_status"

        # 3. 工业设备维护知识库查询
        industrial_keywords = [
            "E01", "E02", "E03", "E04", "E05",
            "报警", "故障", "异常",
            "温度传感器", "光电传感器", "传感器",
            "传送带", "电机", "气压", "气缸",
            "点检", "巡检", "检查", "维修", "更换",
            "SOP", "安全", "断电", "防护", "气源",
        ]

        if any(word in user_text for word in industrial_keywords):
            return "search_knowledge"

        # 4. 项目相关知识库查询
        project_keywords = [
            "EdgeTalk", "功能", "后续计划",
            "RAG", "ASR", "LLM", "TTS",
            "接口", "Memory", "Agent",
        ]

        if any(word in user_text for word in project_keywords):
            return "search_knowledge"

        # 5. 默认普通聊天
        return "chat"

    def build_context(self, tool_name: str, tool_result: dict) -> str:
        """Build context text from tool result."""

        if tool_name == "list_knowledge_files":
            files = tool_result.get("files", [])
            return "知识库文件列表：\n" + "\n".join(
                [f"- {file}" for file in files]
            )

        if tool_name == "search_knowledge":
            results = tool_result.get("results", [])
            return "\n\n".join(
                [item.get("text", "") for item in results]
            )

        if tool_name == "get_project_status":
            return tool_result.get("status", "")

        return ""

    def _generate_reply(self, user_text: str, context: str = "") -> str:
        """
        Generate answer with pipeline.

        This method is compatible with different pipeline.generate_reply signatures:
        1. generate_reply(user_text=user_text, context=context)
        2. generate_reply(prompt)
        3. generate_reply(user_text)
        """

        if self.pipeline is None:
            if context:
                return (
                    "当前未接入 LLM Pipeline，以下为知识库检索到的相关内容：\n\n"
                    + context
                )
            return "当前未接入 LLM Pipeline，无法生成大模型回答。"

        prompt = f"""
你是 EdgeTalk 工业设备维护助手，请基于知识库资料回答用户问题。

【用户问题】
{user_text}

【知识库资料】
{context}

回答要求：
1. 优先依据知识库资料回答。
2. 如果资料不足，请说明“知识库资料不足，无法确认”。
3. 不要编造不存在的维修步骤。
4. 回答要简洁、清晰，适合现场维护人员阅读。
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
        """Save user input and assistant answer, then return response."""

        answer = response.get("answer", "")

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

        response["session_id"] = session_id
        return response

    def run(
        self,
        user_text: str,
        session_id: str = "default",
    ) -> dict:
        """Run AgentCore with session memory."""

        if not user_text.strip():
            response = {
                "input": user_text,
                "tool_used": "none",
                "tool_result": {},
                "answer": "输入内容不能为空。",
            }
            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

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

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        if tool_name == "list_knowledge_files":
            tool_result = list_knowledge_files(self.knowledge_dir)
            files = tool_result.get("files", [])

            answer = "知识库中共有以下文档：\n" + "\n".join(
                [f"- {file}" for file in files]
            )

            response = {
                "input": user_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "answer": answer,
            }

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        if tool_name == "search_knowledge":
            tool_result = search_knowledge(
                query=user_text,
                knowledge_dir=self.knowledge_dir,
                top_k=2,
                min_score=0.08,
            )

            if not tool_result.get("results"):
                response = {
                    "input": user_text,
                    "tool_used": tool_name,
                    "tool_result": tool_result,
                    "answer": "知识库中没有检索到足够相关的内容。",
                }

                return self._return_with_memory(
                    session_id=session_id,
                    user_text=user_text,
                    response=response,
                )

            context = self.build_context(tool_name, tool_result)

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

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        if tool_name == "get_project_status":
            tool_result = get_project_status()
            context = self.build_context(tool_name, tool_result)

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

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        response = {
            "input": user_text,
            "tool_used": "unknown",
            "tool_result": {},
            "answer": "暂时无法判断应该使用哪个工具。",
        }

        return self._return_with_memory(
            session_id=session_id,
            user_text=user_text,
            response=response,
        )
