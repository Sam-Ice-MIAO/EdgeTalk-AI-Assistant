from src.rag.simple_retriever import SimpleRetriever


def main():
    retriever = SimpleRetriever(knowledge_dir="data/knowledge/industrial")

    questions = [
        "E03 报警是什么意思？",
        "更换温度传感器前需要做哪些准备？",
        "每日点检需要检查哪些项目？",
        "维修设备前需要做哪些安全操作？",
    ]

    for question in questions:
        print("=" * 80)
        print("问题：", question)

        results = retriever.retrieve(
            query=question,
            top_k=1,
            min_score=0.10
        )

        if not results:
            print("未检索到相关内容")
            continue

        for item in results:
            print("-" * 80)
            print("来源：", item["source"])
            print("分数：", round(item["score"], 4))
            print("内容：", item["text"][:200])


if __name__ == "__main__":
    main()
