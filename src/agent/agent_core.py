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

    def _industrial_anchor_keywords(self):
        return [
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
            "传送带",
            "电机",
            "气压",
            "气缸",
            "点检",
            "巡检",
            "维修",
            "更换",
            "sop",
            "安全",
            "断电",
            "防护",
            "气源",
        ]

    def _contains_industrial_context(
        self,
        text: str,
    ) -> bool:
        lowered = text.lower()

        return any(
            word in lowered
            for word in self._industrial_anchor_keywords()
        )

    def _is_followup(
        self,
        text: str,
    ) -> bool:
        lowered = text.lower().strip()

        followup_keywords = [
            "那",
            "这个",
            "它",
            "然后",
            "接下来",
            "第一步",
            "下一步",
            "再然后",
            "怎么办",
            "怎么处理",
            "还需要",
            "还要",
        ]

        return any(
            word in lowered
            for word in followup_keywords
        )

    def _load_recent_history(
        self,
        session_id: str,
        limit: int = 8,
    ):
        try:
            messages = self.memory.get_recent_messages(
                session_id=session_id,
                limit=limit,
            )

            if not isinstance(messages, list):
                return []

            print(
                f"[Memory] Loaded {len(messages)} messages "
                f"for session={session_id}"
            )

            return messages

        except Exception as exc:
            print(
                f"[Memory] Load failed: {exc}"
            )
            return []
    def _history_to_text(
        self,
        messages,
    ) -> str:
        parts = []

        for item in messages:
            if not isinstance(
                item,
                dict,
            ):
                continue

            role = item.get(
                "role",
                "",
            )

            content = item.get(
                "content",
                "",
            )

            if content:
                parts.append(
                    f"{role}: {content}"
                )

        return "\n".join(parts)

    def _find_recent_industrial_anchor(
        self,
        messages,
    ):
        for item in reversed(messages):
            if not isinstance(
                item,
                dict,
            ):
                continue

            if item.get("role") != "user":
                continue

            content = item.get(
                "content",
                "",
            )

            if (
                content
                and self._contains_industrial_context(
                    content
                )
            ):
                return content

        return None

    def _build_retrieval_query(
        self,
        user_text: str,
        history,
    ):
        if not self._is_followup(
            user_text
        ):
            return user_text, False

        anchor = (
            self._find_recent_industrial_anchor(
                history
            )
        )

        if not anchor:
            return user_text, False

        rewritten_query = (
            f"{anchor}\n"
            f"当前追问：{user_text}"
        )

        return rewritten_query, True

    def select_tool(
        self,
        user_text: str,
        history_text: str = "",
    ) -> str:
        text = user_text.lower()

        realtime_keywords = [
            "天气",
            "气温",
            "今天几度",
            "明天几度",
            "股票",
            "股价",
            "汇率",
            "新闻",
            "航班",
            "路况",
            "实时",
            "最新消息",
        ]

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

        industrial_keywords = (
            self._industrial_anchor_keywords()
            + [
                "检查",
                "检查项目",
                "步骤",
                "准备",
                "之前",
                "注意",
                "注意什么",
                "注意事项",
                "需要注意",
            ]
        )

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

        if any(
            word in text
            for word in realtime_keywords
        ):
            return "realtime_guard"

        if any(
            word in text
            for word in list_keywords
        ):
            return "list_knowledge_files"

        if any(
            word in text
            for word in status_keywords
        ):
            return "get_project_status"

        if any(
            word in text
            for word in industrial_keywords
        ):
            return "search_knowledge"

        if (
            self._is_followup(user_text)
            and self._contains_industrial_context(
                history_text
            )
        ):
            return "search_knowledge"

        if any(
            word in text
            for word in project_keywords
        ):
            return "get_project_status"

        return "chat"

    def _build_context_from_tool_result(
        self,
        tool_name: str,
        tool_result,
    ) -> str:
        if not isinstance(
            tool_result,
            dict,
        ):
            return str(
                tool_result or ""
            )

        if tool_name == "list_knowledge_files":
            files = tool_result.get(
                "files",
                [],
            )

            if isinstance(
                files,
                list,
            ):
                return "\n".join(
                    str(item)
                    for item in files
                )

            return str(files)

        if tool_name == "search_knowledge":
            results = tool_result.get(
                "results",
                [],
            )

            if not isinstance(
                results,
                list,
            ):
                return ""

            context_parts = []

            for item in results:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                text = item.get(
                    "text",
                    "",
                )

                if text:
                    context_parts.append(
                        text
                    )

            return "\n\n".join(
                context_parts
            )

        if tool_name == "get_project_status":
            return str(
                tool_result.get(
                    "status",
                    tool_result.get(
                        "message",
                        "",
                    ),
                )
            )

        return ""

    def _generate_reply(
        self,
        user_text: str,
        context: str = "",
    ) -> str:
        if self.llm is not None:
            try:
                return self.llm.generate(
                    user_text=user_text,
                    context=(
                        context
                        if context
                        else None
                    ),
                )

            except Exception as exc:
                print(
                    f"LocalLLM generate failed: {exc}"
                )

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
                return (
                    self.pipeline.generate_reply(
                        user_text=user_text,
                        context=context,
                    )
                )

            except TypeError:
                try:
                    return (
                        self.pipeline.generate_reply(
                            prompt
                        )
                    )

                except TypeError:
                    return (
                        self.pipeline.generate_reply(
                            user_text
                        )
                    )

        if context:
            short_context = (
                context.strip()[:600]
            )

            return (
                "根据知识库检索结果，"
                "相关内容如下：\n\n"
                + short_context
            )

        return (
            "当前未加载本地 LLM，"
            "但 Agent、RAG 和 Memory "
            "功能可以正常使用。"
        )

    def _return_with_memory(
        self,
        session_id: str,
        user_text: str,
        response: dict,
    ) -> dict:
        answer = response.get(
            "answer",
            "",
        )

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
        history = (
            self._load_recent_history(
                session_id
            )
        )

        history_text = (
            self._history_to_text(
                history
            )
        )

        tool_name = self.select_tool(
            user_text,
            history_text=history_text,
        )

        if tool_name == "realtime_guard":
            answer = (
                "这个问题需要实时外部数据支持。"
                "当前 EdgeTalk Pro 运行的是"
                "本地离线模型，尚未接入天气、"
                "新闻、股票等实时数据 API，"
                "因此我不能可靠地给出当前结果。"
            )

            response = {
                "input": user_text,
                "tool_used": "realtime_guard",
                "tool_result": {},
                "answer": answer,
                "session_id": session_id,
                "guardrail_triggered": True,
                "guardrail_reason": (
                    "realtime_data_required"
                ),
            }

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        if tool_name == "chat":
            llm_user_text = user_text

            if (
                self._is_followup(user_text)
                and history_text
            ):
                llm_user_text = (
                    "结合下面最近的对话，"
                    "回答当前追问。\n\n"
                    f"{history_text}\n\n"
                    f"当前追问：{user_text}"
                )

            answer = self._generate_reply(
                user_text=llm_user_text,
            )

            response = {
                "input": user_text,
                "tool_used": "chat",
                "tool_result": {},
                "answer": answer,
                "session_id": session_id,
                "followup_rewritten": False,
            }

            return self._return_with_memory(
                session_id=session_id,
                user_text=user_text,
                response=response,
            )

        if tool_name == "list_knowledge_files":
            try:
                tool_result = (
                    list_knowledge_files(
                        knowledge_dir=(
                            self.knowledge_dir
                        )
                    )
                )

            except TypeError:
                tool_result = (
                    list_knowledge_files(
                        self.knowledge_dir
                    )
                )

            if not isinstance(
                tool_result,
                dict,
            ):
                tool_result = {
                    "success": True,
                    "files": tool_result,
                }

            context = (
                self._build_context_from_tool_result(
                    tool_name,
                    tool_result,
                )
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

        if tool_name == "get_project_status":
            tool_result = (
                get_project_status()
            )

            if not isinstance(
                tool_result,
                dict,
            ):
                tool_result = {
                    "success": True,
                    "status": tool_result,
                }

            context = (
                self._build_context_from_tool_result(
                    tool_name,
                    tool_result,
                )
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

        if tool_name == "search_knowledge":
            (
                retrieval_query,
                followup_rewritten,
            ) = self._build_retrieval_query(
                user_text,
                history,
            )

            try:
                tool_result = (
                    search_knowledge(
                        query=retrieval_query,
                        knowledge_dir=(
                            self.knowledge_dir
                        ),
                        retriever_type=(
                            "embedding"
                        ),
                    )
                )

            except TypeError:
                try:
                    tool_result = (
                        search_knowledge(
                            retrieval_query,
                            knowledge_dir=(
                                self.knowledge_dir
                            ),
                            retriever_type=(
                                "embedding"
                            ),
                        )
                    )

                except TypeError:
                    tool_result = (
                        search_knowledge(
                            retrieval_query
                        )
                    )

            if not isinstance(
                tool_result,
                dict,
            ):
                tool_result = {
                    "success": bool(
                        tool_result
                    ),
                    "results": (
                        tool_result or []
                    ),
                }

            context = (
                self._build_context_from_tool_result(
                    tool_name,
                    tool_result,
                )
            )

            llm_user_text = user_text

            if context:
                answer = self._generate_reply(
                    user_text=llm_user_text,
                    context=context,
                )

            else:
                answer = (
                    "当前工业知识库中没有检索到"
                    "足够相关的资料。"
                    "建议补充设备型号、故障码或"
                    "具体维护问题后再试。"
                )

            response = {
                "input": user_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "answer": answer,
                "session_id": session_id,
                "retrieval_query": (
                    retrieval_query
                ),
                "followup_rewritten": (
                    followup_rewritten
                ),
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
