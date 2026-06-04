from src.rag.document_loader import load_and_split_documents


def main():
    chunks = load_and_split_documents("data/knowledge")

    print(f"共加载 {len(chunks)} 个文本块")

    for chunk in chunks:
        print("来源:", chunk["source"])
        print("编号:", chunk["chunk_id"])
        print("内容:", chunk["text"])
        print("-" * 40)


if __name__ == "__main__":
    main()
