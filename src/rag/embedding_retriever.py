import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.document_loader import load_and_split_documents


class EmbeddingRetriever:
    def __init__(
        self,
        knowledge_dir: str = "data/knowledge/industrial",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        chunk_size: int = 200,
        overlap: int = 50,
    ):
        self.knowledge_dir = knowledge_dir
        self.model_name = model_name

        self.chunks = load_and_split_documents(
            knowledge_dir=self.knowledge_dir,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        self.texts = [chunk["text"] for chunk in self.chunks]

        self.model = SentenceTransformer(self.model_name)
        self.embeddings = self.model.encode(
            self.texts,
            normalize_embeddings=True,
        )

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.30):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )[0]

        scores = np.dot(self.embeddings, query_embedding)

        results = []

        for index, score in enumerate(scores):
            score = float(score)

            if score >= min_score:
                chunk = self.chunks[index]
                results.append({
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "score": score,
                    "text": chunk["text"],
                })

        results = sorted(
            results,
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]


if __name__ == "__main__":
    retriever = EmbeddingRetriever()

    questions = [
        "E03 报警是什么意思？",
        "更换温度传感器前需要做哪些准备？",
        "每日点检需要检查哪些项目？",
        "维修设备前需要做哪些安全操作？",
    ]

    for question in questions:
        print("=" * 80)
        print("问题：", question)

        results = retriever.retrieve(question, top_k=2)

        for item in results:
            print("-" * 80)
            print("来源：", item["source"])
            print("分数：", round(item["score"], 4))
            print("内容：", item["text"][:200])
