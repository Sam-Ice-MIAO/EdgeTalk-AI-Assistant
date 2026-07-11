# Pipeline 设计说明

## 目标

将 EdgeTalk 的核心 AI 能力从 API 层中拆出来，封装为统一的 Pipeline。

## 当前设计

- `src/api/app.py`：负责 FastAPI 接口；
- `src/pipeline.py`：负责统一调用 ASR、LLM、TTS；
- `src/asr/`：语音识别模块；
- `src/llm/`：本地 LLM 推理模块；
- `src/tts/`：语音合成模块。

## 设计价值

这样可以避免把所有业务逻辑都写在 API 文件里。后续增加 `/voice-chat`、`/rag-chat` 或 Agent 能力时，可以继续复用 Pipeline。
