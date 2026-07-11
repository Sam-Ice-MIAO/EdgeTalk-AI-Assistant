from llama_cpp import Llama


def main():
    llm = Llama(
        model_path="models/qwen1.5b.gguf",
        n_ctx=2048,
        n_threads=6,
        verbose=False
    )

    prompt = (
        "你是一个本地运行的中文语音助手。"
        "请用简洁、自然的中文回答用户问题。\n\n"
        "用户：请告诉我世界上有多少个人的名字叫刘斯蔓。\n"
        "助手："
    )

    output = llm(
        prompt,
        max_tokens=120,
        temperature=0.4,
        stop=["用户：", "\n用户：","</s>"]
    )

    reply = output["choices"][0]["text"].strip()

    print("用户输入：你好，请介绍一下你自己。")
    print("AI回复：", reply)


if __name__ == "__main__":
    main()
