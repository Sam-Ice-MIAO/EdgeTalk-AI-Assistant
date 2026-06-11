from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.pipeline import EdgeTalkPipeline
from src.rag.simple_retriever import SimpleRetriever
from src.agent.agent_core import AgentCore


app = FastAPI(
    title="EdgeTalk API",
    description="Local AI assistant API for EdgeTalk",
    version="0.3.0"
)


pipeline = EdgeTalkPipeline()
agent = AgentCore(pipeline=pipeline)


class ChatRequest(BaseModel):
    text: str


class RagChatRequest(BaseModel):
    text: str
    top_k: int = 2
    min_score: float = 0.08
    knowledge_dir: str = "data/knowledge/industrial"


class AgentChatRequest(BaseModel):
    text: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "EdgeTalk API",
        "version": "3.0.0"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    try:
        reply = pipeline.generate_reply(request.text)

        return {
            "input": request.text,
            "reply": reply
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    upload_dir = Path("audio/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename).suffix if file.filename else ".m4a"
    input_path = upload_dir / f"input_{uuid4().hex}{suffix}"

    content = await file.read()
    input_path.write_bytes(content)

    try:
        result = pipeline.run_audio_pipeline(str(input_path))
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag-chat")
def rag_chat(request: RagChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    try:
        retriever = SimpleRetriever(request.knowledge_dir)

        results = retriever.retrieve(
            query=request.text,
            top_k=request.top_k,
            min_score=request.min_score
        )

        if not results:
            return {
                "input": request.text,
                "reply": "知识库中没有检索到足够相关的内容。",
                "retrieved": []
            }

        context = "\n\n".join([item["text"] for item in results])

        reply = pipeline.generate_reply(
            user_text=request.text,
            context=context
        )

        return {
            "input": request.text,
            "reply": reply,
            "retrieved": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent-chat")
def agent_chat(request: AgentChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    try:
        result = agent.run(request.text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}")
def get_audio(filename: str):
    audio_path = Path("audio") / filename

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        filename=filename
    )
