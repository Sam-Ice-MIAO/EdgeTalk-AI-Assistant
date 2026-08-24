import os
import time
import json
from pathlib import Path

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import LLM_MODEL_PATH

from src.agent.agent_core import AgentCore
from src.rag.simple_retriever import SimpleRetriever
from src.rag.embedding_retriever import EmbeddingRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_RESULT_PATH = (
    PROJECT_ROOT
    / "eval"
    / "results"
    / "latest.json"
)

app = FastAPI(
    title="EdgeTalk Pro API",
    description=(
        "Industrial maintenance AI assistant "
        "with RAG, Agent, Local LLM and Memory"
    ),
    version="pro-0.2",
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


def create_local_llm():
    configured_path = os.getenv(
        "LLM_MODEL_PATH",
        LLM_MODEL_PATH,
    )

    model_path = Path(configured_path)

    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path

    if not model_path.exists():
        print(
            f"Local LLM model not found: {model_path}"
        )
        return None, "model_missing", None

    try:
        # 延迟导入：
        # Docker 轻量镜像没有 llama-cpp-python 时
        # FastAPI 仍然可以启动
        from src.llm.local_llm import LocalLLM

        llm = LocalLLM(
            model_path=str(model_path),
            n_ctx=2048,
            n_threads=6,
        )

        print(
            f"Local LLM loaded: {model_path.name}"
        )

        return (
            llm,
            "ready",
            model_path.name,
        )

    except Exception as exc:
        print(
            f"Local LLM load failed: {exc}"
        )

        return None, "error", None


local_llm, llm_status, llm_model_name = (
    create_local_llm()
)


agent = AgentCore(
    pipeline=None,
    llm=local_llm,
)


_retriever_cache = {}


class ChatRequest(BaseModel):
    text: str


class RagChatRequest(BaseModel):
    text: str
    top_k: int = 1
    min_score: float = 0.08
    retriever_type: str = "embedding"
    knowledge_dir: str = (
        "data/knowledge/industrial"
    )


class AgentChatRequest(BaseModel):
    text: str
    session_id: str = "default"


@app.middleware("http")
async def add_process_time_header(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (
        time.perf_counter() - start_time
    )

    response.headers["X-Process-Time"] = str(
        round(process_time, 4)
    )

    print(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"time={process_time:.4f}s"
    )

    return response


def get_retriever(
    retriever_type: str,
    knowledge_dir: str,
):
    retriever_type = (
        retriever_type.lower().strip()
    )

    cache_key = (
        f"{retriever_type}:{knowledge_dir}"
    )

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
            detail=(
                "retriever_type must be "
                "'embedding' or 'tfidf'"
            ),
        )

    _retriever_cache[cache_key] = retriever

    return retriever


def normalize_sources(results):
    sources = []

    if not isinstance(results, list):
        return sources

    for item in results:
        if not isinstance(item, dict):
            continue

        source_path = item.get(
            "source",
            "",
        )

        sources.append(
            {
                "file": (
                    Path(source_path).name
                    if source_path
                    else ""
                ),
                "source": source_path,
                "chunk_id": item.get(
                    "chunk_id"
                ),
                "text": item.get(
                    "text",
                    "",
                ),
                "score": item.get(
                    "score"
                ),
                "raw_score": item.get(
                    "raw_score"
                ),
                "boost": item.get(
                    "boost"
                ),
            }
        )

    return sources
def load_memory_messages(
    session_id: str,
):
    memory = agent.memory

    try:
        return memory.get_recent_messages(
            session_id=session_id,
            limit=100,
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to load memory: {exc}"
        )


@app.get("/")
def root():
    return {
        "service": "EdgeTalk Pro API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    memory_backend = os.getenv(
        "MEMORY_BACKEND",
        "sqlite",
    ).lower()

    return {
        "success": True,
        "status": "healthy",
        "service": "EdgeTalk Pro API",
        "version": "pro-0.2",
        "mode": "rag-agent-local-llm",
        "components": {
            "api": "ready",
            "rag": "ready",
            "retriever": "embedding",
            "agent": "ready",
            "llm": llm_status,
            "memory": memory_backend,
        },
        "model": llm_model_name,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    if local_llm is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Local LLM is not available."
            ),
        )

    start_time = time.perf_counter()

    try:
        answer = local_llm.generate(
            user_text=request.text,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM generation failed: {exc}",
        )

    latency_ms = round(
        (
            time.perf_counter()
            - start_time
        )
        * 1000,
        2,
    )

    return {
        "success": True,
        "answer": answer,
        "model": llm_model_name,
        "latency_ms": latency_ms,
    }


@app.post("/rag-chat")
def rag_chat(request: RagChatRequest):
    start_time = time.perf_counter()

    retriever = get_retriever(
        request.retriever_type,
        request.knowledge_dir,
    )

    results = retriever.retrieve(
        request.text,
        top_k=request.top_k,
        min_score=request.min_score,
    )

    latency_ms = round(
        (
            time.perf_counter()
            - start_time
        )
        * 1000,
        2,
    )

    sources = normalize_sources(
        results
    )

    return {
        "success": True,
        "query": request.text,
        "retriever_type": (
            request.retriever_type
        ),
        "min_score": request.min_score,
        "sources": sources,
        "latency_ms": latency_ms,
    }


@app.post("/agent-chat")
def agent_chat(request: AgentChatRequest):
    start_time = time.perf_counter()

    try:
        result = agent.run(
            request.text,
            session_id=request.session_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {exc}",
        )

    latency_ms = round(
        (
            time.perf_counter()
            - start_time
        )
        * 1000,
        2,
    )

    tool_result = (
        result.get("tool_result")
        or {}
    )

    if isinstance(tool_result, dict):
        retriever_type = (
            tool_result.get(
                "retriever_type"
            )
        )

        results = tool_result.get(
            "results",
            [],
        )
    else:
        retriever_type = None
        results = []

    sources = normalize_sources(
        results
    )

    return {
        "success": True,
        "answer": result.get(
            "answer",
            "",
        ),
        "session_id": result.get(
            "session_id",
            request.session_id,
        ),
        "tool_used": result.get(
            "tool_used"
        ),
        "retriever_type": retriever_type,
        "sources": sources,
        "retrieval_query": result.get(
            "retrieval_query"
        ),
        "followup_rewritten": result.get(
            "followup_rewritten",
            False,
        ),
        "guardrail_triggered": result.get(
            "guardrail_triggered",
            False,
        ),
        "guardrail_reason": result.get(
            "guardrail_reason"
        ),
        "latency_ms": latency_ms,
    }


@app.get("/memory/{session_id}")
def get_memory(session_id: str):
    try:
        messages = load_memory_messages(
            session_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Memory query failed: {exc}",
        )

    if messages is None:
        messages = []

    return {
        "session_id": session_id,
        "count": len(messages),
        "messages": messages,
    }
@app.get("/evaluation/latest")
def get_latest_evaluation():
    if not EVALUATION_RESULT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Evaluation result not found. "
                "Run python eval/run_eval.py first."
            ),
        )

    try:
        with open(
            EVALUATION_RESULT_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            result = json.load(
                file
            )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load "
                f"evaluation result: {exc}"
            ),
        )
