from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.rag.simple_retriever import SimpleRetriever
from src.rag.embedding_retriever import EmbeddingRetriever
from src.agent.agent_core import AgentCore


app = FastAPI(
    title="EdgeTalk API",
    description="Lightweight API for EdgeTalk RAG and Agent testing",
    version="3.1.0",
)

# 第八周轻量模式：不加载完整 Pipeline，避免 ASR / TTS / LLM 依赖影响 RAG 测试
pipeline = None
agent = AgentCore(pipeline=None)

# 简单缓存，避免每次请求都重新加载 embedding 模型
_retriever_cache = {}


class ChatRequest(BaseModel):
    text: str


class RagChatRequest(BaseModel):
    text: str
    top_k: int = 1
    min_score: float = 0.08
    retriever_type: str = "embedding"
    knowledge_dir: str = "data/knowledge/industrial"


class AgentChatRequest(BaseModel):
    text: str
    session_id: str = "default"


def get_retriever(retriever_type: str, knowledge_dir: str):
    """
    根据 retriever_type 获取检索器。
    embedding：语义检索
    tfidf：关键词检索 baseline
    """
    retriever_type = retriever_type.lower().strip()
    cache_key = f"{retriever_type}:{knowledge_dir}"

    if cache_key in _retriever_cache:
        return _retriever_cache[cache_key]

    if retriever_type == "embedding":
        retriever = EmbeddingRetriever(
            knowledge_dir=knowledge_dir,
        )
    elif retriever_type == "tfidf":
        retriever = SimpleRetriever(
            knowledge_dir=knowledge_dir,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="retriever_type must be 'embedding' or 'tfidf'",
        )

    _retriever_cache[cache_key] = retriever
    return retriever


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "EdgeTalk API",
        "version": "3.1.0",
        "mode": "lightweight-rag-agent",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    return {
        "input": request.text,
        "reply": "当前是轻量 API 模式，未加载完整 LLM Pipeline。请使用 /rag-chat 或 /agent-chat 测试 RAG 和 Agent 功能。",
    }


@app.post("/rag-chat")
def rag_chat(request: RagChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    retriever_type = request.retriever_type.lower().strip()

    try:
        retriever = get_retriever(
            retriever_type=retriever_type,
            knowledge_dir=request.knowledge_dir,
        )

        if retriever_type == "embedding":
            min_score_used = 0.30
        else:
            min_score_used = request.min_score

        results = retriever.retrieve(
            query=request.text,
            top_k=request.top_k,
            min_score=min_score_used,
        )

        if not results:
            return {
                "input": request.text,
                "retriever_type": retriever_type,
                "min_score_used": min_score_used,
                "reply": "知识库中没有检索到足够相关的内容。",
                "retrieved": [],
            }

        context = "\n\n".join(item["text"] for item in results)

        # 当前轻量模式不调用 LLM，只返回精简后的知识库片段
        reply = "根据知识库检索结果，相关内容如下：\n" + context[:600]

        return {
            "input": request.text,
            "retriever_type": retriever_type,
            "min_score_used": min_score_used,
            "reply": reply,
            "retrieved": results,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent-chat")
def agent_chat(request: AgentChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    try:
        result = agent.run(
            user_text=request.text,
            session_id=request.session_id,
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{session_id}")
def get_memory(session_id: str, limit: int = 20):
    messages = agent.memory.get_recent_messages(
        session_id=session_id,
        limit=limit,
    )

    return {
        "session_id": session_id,
        "count": len(messages),
        "messages": messages,
    }
