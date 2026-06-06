from src.agent.tools import (
    list_knowledge_files,
    search_knowledge,
    get_project_status,
)


class AgentCore:
    def __init__(self, pipeline, knowledge_dir: str = "data/knowledge"):
        self.pipeline = pipeline
        self.knowledge_dir = knowledge_dir

    def select_tool(self, user_text: str) -> str:
        if any(word in user_text for word in ["哪些文档", "知识库文件", "文档列表", "有哪些资料"]):
            return "list_knowledge_files"

        if any(word in user_text for word in ["项目状态", "当前状态", "做到哪", "当前能力"]):
            return "get_project_status"

        if any(word in user_text for word in ["EdgeTalk", "功能", "后续计划", "RAG", "ASR", "LLM", "TTS", "接口"]):
            return "search_knowledge"

        return "chat"

    def build_context(self, tool_name: str, tool_result: dict) -> str:
        if tool_name == "list_knowledge_files":
            files = tool_result.get("files", [])
            return "知识库文件列表：\n" + "\n".join([f"- {file}" for file in files])

        if tool_name == "search_knowledge":
            results = tool_result.get("results", [])
            return "\n\n".join([item["text"] for item in results])

        if tool_name == "get_project_status":
            return tool_result.get("status", "")

        return ""

    def run(self, user_text: str) -> dict:
        if not user_text.strip():
            return {
                "input": user_text,
                "tool_used": "none",
                "tool_result": {},
                "answer": "输入内容不能为空。"
            }

        tool_name = self.select_tool(user_text)

        if tool_name == "chat":
            answer = self.pipeline.generate_reply(user_text)
            return {
                "input": user_text,
                "tool_used": "chat",
                "tool_result": {},
                "answer": answer
            }

        if tool_name == "list_knowledge_files":
            tool_result = list_knowledge_files(self.knowledge_dir)

        elif tool_name == "search_knowledge":
            tool_result = search_knowledge(
                query=user_text,
                knowledge_dir=self.knowledge_dir,
                top_k=2,
                min_score=0.08
            )

            if not tool_result.get("results"):
                return {
                    "input": user_text,
                    "tool_used": tool_name,
                    "tool_result": tool_result,
                    "answer": "知识库中没有检索到足够相关的内容。"
                }

        elif tool_name == "get_project_status":
            tool_result = get_project_status()

        else:
            tool_result = {}

        context = self.build_context(tool_name, tool_result)

        answer = self.pipeline.generate_reply(
            user_text=user_text,
            context=context
        )

        return {
            "input": user_text,
            "tool_used": tool_name,
            "tool_result": tool_result,
            "answer": answer
        }
