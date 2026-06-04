from pathlib import Path


def load_text_files(knowledge_dir: str):
    knowledge_path = Path(knowledge_dir)

    if not knowledge_path.exists():
        raise FileNotFoundError(f"知识库目录不存在: {knowledge_dir}")

    documents = []

    for file_path in knowledge_path.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8").strip()

        if text:
            documents.append({
                "source": str(file_path),
                "text": text
            })

    return documents


def split_text(text: str, chunk_size: int = 200, overlap: int = 50):
    chunks = []
    text = text.strip()

    if not text:
        return chunks

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def load_and_split_documents(
    knowledge_dir: str,
    chunk_size: int = 200,
    overlap: int = 50
):
    documents = load_text_files(knowledge_dir)

    all_chunks = []

    for doc in documents:
        chunks = split_text(
            doc["text"],
            chunk_size=chunk_size,
            overlap=overlap
        )

        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": idx,
                "text": chunk
            })

    return all_chunks
