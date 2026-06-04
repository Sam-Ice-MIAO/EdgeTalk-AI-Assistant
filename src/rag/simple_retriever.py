from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.rag.document_loader import load_and_split_documents


class SimpleRetriever:
    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir
        self.chunks = load_and_split_documents(knowledge_dir)

        if not self.chunks:
            raise ValueError(f"知识库为空: {knowledge_dir}")

        self.texts = [chunk["text"] for chunk in self.chunks]

        self.vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 4)
        )

        self.matrix = self.vectorizer.fit_transform(self.texts)

    def retrieve(self, query: str, top_k: int = 2, min_score: float = 0.08):

        if not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]

        ranked_indices = scores.argsort()[::-1]

        results = []

        for idx in ranked_indices:
            score = float(scores[idx])

            if score < min_score:
                continue

            results.append({
                "score": score,
                "source": self.chunks[idx]["source"],
                "chunk_id": self.chunks[idx]["chunk_id"],
                "text": self.chunks[idx]["text"]
            })

            if len(results) >= top_k:
                break

        return results
