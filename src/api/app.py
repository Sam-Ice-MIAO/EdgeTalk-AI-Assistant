from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
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
