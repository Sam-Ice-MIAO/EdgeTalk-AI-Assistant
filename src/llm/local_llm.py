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

    def generate(self, user_text: str) -> str:
        prompt = (
            "你是一个本地运行的中文语音助手。"
            "请用简洁、自然的中文回答用户问题，回答不要太长。\n\n"
            f"用户：{user_text}\n"
            "助手："
        )

        output = self.llm(
            prompt,
            max_tokens=120,
            temperature=0.4,
            stop=["用户：", "\n用户："]
        )

        reply = output["choices"][0]["text"].strip()

        print("LLM回复:", reply)

        return reply
