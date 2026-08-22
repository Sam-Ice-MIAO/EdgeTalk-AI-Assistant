import time
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from pathlib import Path
from src.rag.simple_retriever import SimpleRetriever
from src.rag.embedding_retriever import EmbeddingRetriever
from src.agent.agent_core import AgentCore


app = FastAPI(
    title="EdgeTalk API",
    description="Lightweight API for EdgeTalk RAG and Agent testing",
    version="3.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 第八 / 第九周轻量模式：不加载完整 Pipeline，避免 ASR / TTS / LLM 依赖影响 RAG 测试
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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = str(round(process_time, 4))

    print(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"time={process_time:.4f}s"
    )

    return response


def get_retriever(retriever_type: str, knowledge_dir: str):
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
def health():
    memory_backend = os.getenv("MEMORY_BACKEND", "sqlite").lower()

    return {
        "success": True,
        "status": "healthy",
        "service": "EdgeTalk Pro API",
        "version": "pro-0.1",
        "mode": "lightweight-rag-agent",
        "components": {
            "api": "ready",
            "rag": "ready",
            "retriever": "embedding",
            "agent": "ready",
            "memory": memory_backend
        }
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
    start_time = time.perf_counter()

    retriever = get_retriever(
        request.retriever_type,
        request.knowledge_dir
    )

    results = retriever.retrieve(
        request.text,
        top_k=request.top_k,
        min_score=request.min_score
    )

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2
    )

    sources = []

    for item in results:
        source_path = item.get("source", "")

        sources.append({
            "file": Path(source_path).name if source_path else "",
            "source": source_path,
            "chunk_id": item.get("chunk_id"),
            "text": item.get("text", ""),
            "score": item.get("score"),
            "raw_score": item.get("raw_score"),
            "boost": item.get("boost"),
        })

    return {
        "success": True,
        "query": request.text,
        "retriever_type": request.retriever_type,
        "min_score": request.min_score,
        "sources": sources,
        "latency_ms": latency_ms,
    }


@app.post("/agent-chat")
def agent_chat(request: AgentChatRequest):
    start_time = time.perf_counter()

    result = agent.run(
        request.text,
        session_id=request.session_id
    )

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2
    )

    tool_result = result.get("tool_result") or {}
    sources = []

    if isinstance(tool_result, dict):
        for item in tool_result.get("results", []):
            source_path = item.get("source", "")

            sources.append({
                "file": Path(source_path).name if source_path else "",
                "source": source_path,
                "chunk_id": item.get("chunk_id"),
                "text": item.get("text", ""),
                "score": item.get("score"),
                "raw_score": item.get("raw_score"),
                "boost": item.get("boost"),
            })

    return {
        "success": True,
        "answer": result.get("answer", ""),
        "session_id": result.get(
            "session_id",
            request.session_id
        ),
        "tool_used": result.get("tool_used"),
        "retriever_type": (
            tool_result.get("retriever_type")
            if isinstance(tool_result, dict)
            else None
        ),
        "sources": sources,
        "latency_ms": latency_ms,
    }

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
