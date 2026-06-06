from pathlib import Path

from src.rag.simple_retriever import SimpleRetriever


def list_knowledge_files(knowledge_dir: str = "data/knowledge"):
    knowledge_path = Path(knowledge_dir)

    if not knowledge_path.exists():
        return {
            "success": False,
            "message": f"知识库目录不存在: {knowledge_dir}",
            "files": []
        }

    files = [
        file.name
        for file in knowledge_path.glob("*.txt")
    ]

    return {
        "success": True,
        "message": f"共找到 {len(files)} 个知识库文件",
        "files": files
    }


def search_knowledge(
    query: str,
    knowledge_dir: str = "data/knowledge",
    top_k: int = 2,
    min_score: float = 0.08
):
    if not query.strip():
        return {
            "success": False,
            "message": "查询内容不能为空",
            "results": []
        }

    retriever = SimpleRetriever(knowledge_dir)

    results = retriever.retrieve(
        query=query,
        top_k=top_k,
        min_score=min_score
    )

    return {
        "success": True,
        "message": f"检索到 {len(results)} 条相关内容",
        "results": results
    }


def get_project_status():
    return {
        "success": True,
        "status": (
            "EdgeTalk 当前已经支持本地文本问答、语音问答、"
            "FastAPI 接口调用和 RAG 本地知识库问答。"
            "目前正在加入轻量级 Agent 工具调用能力。"
        )
    }
