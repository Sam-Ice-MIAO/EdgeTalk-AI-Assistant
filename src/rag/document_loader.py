from pathlib import Path


def split_text_by_headings(text: str):
    lines = text.splitlines()
    chunks = []
    current = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#") and current:
            chunks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        chunks.append("\n".join(current).strip())

    chunks = [chunk for chunk in chunks if chunk]

    if chunks:
        return chunks

    return [part.strip() for part in text.split("\n\n") if part.strip()]


def split_long_text(text: str, chunk_size: int = 500, overlap: int = 50):
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

        if start >= len(text):
            break

    return chunks


def load_and_split_documents(
    knowledge_dir: str = "data/knowledge/industrial",
    chunk_size: int = 500,
    overlap: int = 50,
):
    knowledge_path = Path(knowledge_dir)

    if not knowledge_path.exists():
        raise FileNotFoundError(f"知识库目录不存在：{knowledge_dir}")

    all_chunks = []

    txt_files = sorted(knowledge_path.glob("*.txt"))

    for file_path in txt_files:
        text = file_path.read_text(encoding="utf-8")

        heading_chunks = split_text_by_headings(text)

        chunk_id = 0

        for heading_chunk in heading_chunks:
            sub_chunks = split_long_text(
                heading_chunk,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            for sub_chunk in sub_chunks:
                all_chunks.append(
                    {
                        "source": str(file_path),
                        "chunk_id": chunk_id,
                        "text": sub_chunk,
                    }
                )
                chunk_id += 1

    return all_chunks
