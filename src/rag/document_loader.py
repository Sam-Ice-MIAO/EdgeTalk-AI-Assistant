from pathlib import Path


def load_text_files(knowledge_dir: str):
    base_dir = Path(knowledge_dir)

    if not base_dir.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {knowledge_dir}")

    documents = []

    for file_path in base_dir.rglob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        documents.append({
            "source": str(file_path),
            "text": text
        })

    return documents


def split_text(text: str, chunk_size: int = 200, overlap: int = 50):
    chunks = []
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
    chunks = []

    for doc in documents:
        text_chunks = split_text(doc["text"], chunk_size, overlap)

        for index, chunk_text in enumerate(text_chunks):
            chunks.append({
                "source": doc["source"],
                "chunk_id": index,
                "text": chunk_text
            })

    return chunks
