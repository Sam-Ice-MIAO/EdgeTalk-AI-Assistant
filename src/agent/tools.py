from pathlib import Path

from src.rag.simple_retriever import SimpleRetriever
from src.rag.embedding_retriever import EmbeddingRetriever


_retriever_cache = {}


def list_knowledge_files(knowledge_dir: str = "data/knowledge/industrial"):
    knowledge_path = Path(knowledge_dir)

    if not knowledge_path.exists():
        return {
            "success": False,
            "message": f"知识库目录不存在：{knowledge_dir}",
            "files": [],
        }

    files = [file.name for file in knowledge_path.glob("*.txt")]

    return {
        "success": True,
        "message": f"共找到 {len(files)} 个知识库文件",
        "files": files,
    }


def _get_retriever(retriever_type: str, knowledge_dir: str):
    retriever_type = retriever_type.lower().strip()
    cache_key = f"{retriever_type}:{knowledge_dir}"

    if cache_key in _retriever_cache:
        return _retriever_cache[cache_key]

    if retriever_type == "embedding":
        retriever = EmbeddingRetriever(knowledge_dir=knowledge_dir)
    elif retriever_type == "tfidf":
        retriever = SimpleRetriever(knowledge_dir=knowledge_dir)
    else:
        raise ValueError("retriever_type must be 'embedding' or 'tfidf'")

    _retriever_cache[cache_key] = retriever
    return retriever


def search_knowledge(
    query: str,
    knowledge_dir: str = "data/knowledge/industrial",
    top_k: int = 1,
    min_score: float = 0.30,
    retriever_type: str = "embedding",
):
    if not query.strip():
        return {
            "success": False,
            "message": "查询内容不能为空",
            "retriever_type": retriever_type,
            "results": [],
        }

    retriever_type = retriever_type.lower().strip()

    try:
        retriever = _get_retriever(
            retriever_type=retriever_type,
            knowledge_dir=knowledge_dir,
        )

        min_score_used = 0.30 if retriever_type == "embedding" else min_score

        results = retriever.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score_used,
        )

        return {
            "success": bool(results),
            "message": f"检索到 {len(results)} 条相关内容" if results else "未检索到相关内容",
            "retriever_type": retriever_type,
            "min_score_used": min_score_used,
            "results": results,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"知识库检索失败：{e}",
            "retriever_type": retriever_type,
            "results": [],
        }


def get_project_status():
    return {
        "success": True,
        "status": (
            "EdgeTalk 当前已支持工业知识库问答、Embedding 语义检索、"
            "Agent 工具调用、SQLite Memory 会话记忆和 FastAPI 接口。"
        ),
    }
