import re
import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.document_loader import load_and_split_documents


def calculate_boost(query: str, source: str, text: str) -> float:
    query_lower = query.lower()
    source_lower = source.lower()
    text_lower = text.lower()

    boost = 0.0

    # 精确故障码匹配：例如问 E03，就优先匹配包含 E03 的 chunk
    code_match = re.search(r"e\d{2}", query_lower)

    if code_match:
        code = code_match.group()

        if code in text_lower:
            boost += 0.45
        elif "fault_codes" in source_lower:
            boost += 0.05
        else:
            boost -= 0.15

    # 维修 / 更换 / SOP 类问题
    sop_keywords = ["更换", "维修", "sop", "步骤", "准备", "检修"]
    if any(word in query_lower for word in sop_keywords):
        if "maintenance_sop" in source_lower:
            boost += 0.20

    # 点检 / 巡检类问题
    inspection_keywords = ["点检", "巡检", "检查项目", "每日", "每周"]
    if any(word in query_lower for word in inspection_keywords):
        if "inspection_checklist" in source_lower:
            boost += 0.20

    # 安全类问题
    safety_keywords = ["安全", "断电", "防护", "气源", "危险", "维修设备前"]
    if any(word in query_lower for word in safety_keywords):
        if "safety_rules" in source_lower:
            boost += 0.20

    return boost


class EmbeddingRetriever:
    def __init__(
        self,
        knowledge_dir: str = "data/knowledge/industrial",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        chunk_size: int = 500,
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

    def retrieve(self, query: str, top_k: int = 1, min_score: float = 0.30):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )[0]

        raw_scores = np.dot(self.embeddings, query_embedding)

        results = []

        for index, raw_score in enumerate(raw_scores):
            raw_score = float(raw_score)
            chunk = self.chunks[index]

            boost = calculate_boost(
                query=query,
                source=chunk["source"],
                text=chunk["text"],
            )

            final_score = raw_score + boost

            if final_score >= min_score:
                results.append({
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "score": final_score,
                    "raw_score": raw_score,
                    "boost": boost,
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

        results = retriever.retrieve(question, top_k=1)

        for item in results:
            print("-" * 80)
            print("来源：", item["source"])
            print("最终分数：", round(item["score"], 4))
            print("原始分数：", round(item["raw_score"], 4))
            print("boost：", round(item["boost"], 4))
            print("内容：", item["text"][:300])
