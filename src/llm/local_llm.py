from llama_cpp import Llama


class LocalLLM:
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: int = 6
    ):
        self.model_path = model_path
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False
        )

    def generate(self, user_text: str, context=None) -> str:

        if context:
            prompt = (
                "你是 EdgeTalk，一个本地运行的中文语音助手原型。"
                "请优先根据给定资料回答用户问题。"
                "如果资料中没有相关信息，请直接说明资料中没有答案，不要编造。"
                "回答要简洁、自然、不重复，最多 3 句话。\n\n"
                f"资料：\n{context}\n\n"
                f"用户：{user_text}\n"
                "助手："
            )
        else:
            prompt = (
                "你是 EdgeTalk，一个本地运行的中文语音助手原型。"
                "你目前主要具备本地文本问答能力，后续会继续接入语音交互和本地知识库问答。"
                "请用简洁、自然、不重复的中文回答用户问题。"
                "回答最多 3 句话，不要编造你不具备的功能。\n\n"
                f"用户：{user_text}\n"
                "助手："
            )

        output = self.llm(
            prompt,
            max_tokens=80,
            temperature=0.3,
            top_p=0.85,
            repeat_penalty=1.15,
            stop=["用户：", "\n用户：", "\n\n用户："]
        )

        reply = output["choices"][0]["text"].strip()

        print("LLM回复:", reply)

        return reply
