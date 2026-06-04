from src.rag.simple_retriever import SimpleRetriever


def main():
    retriever = SimpleRetriever("data/knowledge")

    query = "EdgeTalk 当前实现了哪些功能？"

    results = retriever.retrieve(
        query=query,
        top_k=2,
        min_score=0.08
    )

    print("问题:", query)
    print("检索结果:")

    if not results:
        print("没有检索到满足分数阈值的相关内容。")
        return

    for result in results:
        print("分数:", result["score"])
        print("来源:", result["source"])
        print("编号:", result["chunk_id"])
        print("内容:", result["text"])
        print("-" * 40)


if __name__ == "__main__":
    main()
