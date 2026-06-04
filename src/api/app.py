from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config.settings import LLM_MODEL_PATH
from src.llm.local_llm import LocalLLM


app = FastAPI(
    title="EdgeTalk API",
    description="Local AI assistant API for EdgeTalk",
    version="1.0.0"
)


llm = None


class ChatRequest(BaseModel):
    text: str


def get_llm():

    global llm

    if llm is None:
        print("正在加载本地 LLM 模型...")
        llm = LocalLLM(model_path=LLM_MODEL_PATH)
        print("本地 LLM 模型加载完成")

    return llm


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
        model = get_llm()
        reply = model.generate(request.text)

        return {
            "input": request.text,
            "reply": reply
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
