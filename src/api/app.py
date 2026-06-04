from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.pipeline import EdgeTalkPipeline


app = FastAPI(
    title="EdgeTalk API",
    description="Local AI assistant API for EdgeTalk",
    version="1.0.0"
)


pipeline = EdgeTalkPipeline()


class ChatRequest(BaseModel):
    text: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "EdgeTalk API"
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
