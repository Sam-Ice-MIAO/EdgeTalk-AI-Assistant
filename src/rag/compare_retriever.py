from src.rag.simple_retriever import SimpleRetriever
from src.rag.embedding_retriever import EmbeddingRetriever


TEST_CASES = [
    {
        "question": "E03 报警是什么意思？",
        "expected": "fault_codes.txt",
    },
    {
        "question": "更换温度传感器前需要做哪些准备？",
        "expected": "maintenance_sop.txt",
    },
    {
        "question": "每日点检需要检查哪些项目？",
        "expected": "inspection_checklist.txt",
    },
    {
        "question": "维修设备前需要做哪些安全操作？",
        "expected": "safety_rules.txt",
    },
]


def get_top_source(results):
    if not results:
        return "无结果"
    return results[0]["source"]


def is_hit(results, expected):
    if not results:
        return False
    return expected in results[0]["source"]


def main():
    tfidf = SimpleRetriever(knowledge_dir="data/knowledge/industrial")
    embedding = EmbeddingRetriever(knowledge_dir="data/knowledge/industrial")

    tfidf_hits = 0
    embedding_hits = 0

    for case in TEST_CASES:
        question = case["question"]
        expected = case["expected"]

        tfidf_results = tfidf.retrieve(
            query=question,
            top_k=1,
            min_score=0.08,
        )

        embedding_results = embedding.retrieve(
            query=question,
            top_k=1,
            min_score=0.30,
        )

        tfidf_hit = is_hit(tfidf_results, expected)
        embedding_hit = is_hit(embedding_results, expected)

        if tfidf_hit:
            tfidf_hits += 1

        if embedding_hit:
            embedding_hits += 1

        print("=" * 80)
        print("问题：", question)
        print("预期：", expected)
        print("TF-IDF Top1：", get_top_source(tfidf_results), "命中：", tfidf_hit)
        print("Embedding Top1：", get_top_source(embedding_results), "命中：", embedding_hit)

    total = len(TEST_CASES)

    print("=" * 80)
    print(f"TF-IDF Top1 命中率：{tfidf_hits}/{total}")
    print(f"Embedding Top1 命中率：{embedding_hits}/{total}")


if __name__ == "__main__":
    main()
