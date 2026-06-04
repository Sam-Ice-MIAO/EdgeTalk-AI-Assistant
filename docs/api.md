# API 使用说明

## 目标

为 EdgeTalk 增加 FastAPI 接口，使本地语音助手可以通过 HTTP API 调用。

## 启动方式

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
