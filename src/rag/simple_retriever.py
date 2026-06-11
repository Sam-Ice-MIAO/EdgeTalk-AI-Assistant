import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.rag.document_loader import load_and_split_documents


def source_boost(query: str, source: str) -> float:
    """Give small score boosts based on query intent and document type."""
    boost = 0.0

    if re.search(r"E\d{2}", query, re.IGNORECASE):
        if "fault_codes" in source:
            boost += 0.15

    if any(word in query for word in ["更换", "SOP", "步骤", "准备", "维修流程"]):
        if "maintenance_sop" in source:
            boost += 0.10

    if any(word in query for word in ["点检", "巡检", "检查项目"]):
        if "inspection_checklist" in source:
            boost += 0.10

    if any(word in query for word in ["安全", "断电", "防护", "气源", "危险"]):
        if "safety_rules" in source:
            boost += 0.10

    return boost


class SimpleRetriever:
    def __init__(
        self,
        knowledge_dir: str = "data/knowledge/industrial",
        chunk_size: int = 200,
        overlap: int = 50,
    ):
        self.knowledge_dir = knowledge_dir
        self.chunk_size = chunk_size
        self.overlap = overlap

        self.chunks = load_and_split_documents(
            knowledge_dir=self.knowledge_dir,
            chunk_size=self.chunk_size,
            overlap=self.overlap,
        )

        self.texts = [chunk["text"] for chunk in self.chunks]

        self.vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 4),
        )

        self.doc_vectors = self.vectorizer.fit_transform(self.texts)

    def retrieve(
        self,
        query: str,
        top_k: int = 2,
        min_score: float = 0.08,
    ):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]

        results = []

        for index, chunk in enumerate(self.chunks):
            raw_score = float(similarities[index])
            final_score = raw_score + source_boost(query, chunk["source"])

            if final_score >= min_score:
                results.append({
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "score": final_score,
                    "raw_score": raw_score,
                    "text": chunk["text"],
                })

        results = sorted(
            results,
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]
