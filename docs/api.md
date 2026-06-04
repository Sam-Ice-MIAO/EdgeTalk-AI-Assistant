# API 使用说明

## 目标

为 EdgeTalk 增加 FastAPI 接口，使本地语音助手可以通过 HTTP API 调用。

## 启动方式

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000

## `/voice-chat`

语音问答接口，支持上传音频文件。

示例：

```bash
curl -X POST http://127.0.0.1:8000/voice-chat \
  -F "file=@audio/test.m4a"

## `/rag-chat`

本地知识库问答接口。

该接口会先从 `data/knowledge/` 中检索与用户问题相关的文本块，再将检索结果作为上下文传给本地 LLM 生成回答。

### 请求示例

```bash
curl -X POST http://127.0.0.1:8000/rag-chat \
  -H "Content-Type: application/json" \
  -d '{"text":"EdgeTalk 当前实现了哪些功能？","top_k":2,"min_score":0.08}'

返回内容包括：用户问题、本地 LLM 回复，检索到的知识库文本块，每个文本块的来源、编号和相似度分数
