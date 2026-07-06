# EdgeTalk 部署说明

## 1. 部署目标

本阶段完成 EdgeTalk 轻量 API 的 Docker 化验证，使项目可以从本地开发环境迁移到容器环境中运行。

当前 Docker 版本主要包含：

- FastAPI 接口
- Embedding RAG 检索
- Agent 工具调用
- SQLite Memory 会话记录
- 简单接口耗时统计

当前版本暂不包含完整 ASR、TTS、本地 LLM 语音链路，主要用于验证 RAG、Agent 和 Memory 的 API 服务能力。

---

## 2. 本地运行方式

进入项目目录：

```bash
cd ~/projects/EdgeTalk-AI-Assistant
source .venv311/bin/activate

启动FastAPI：
python -m uvicorn src.api.app:app --reload

测试健康接口：
curl http://127.0.0.1:8000/health

Docker创建：
在项目根目录执行：
docker build -t edgetalk-api:week9 .
构建成功后，会生成本地镜像：
edgetalk-api:week9

Docker运行：
docker run --rm -p 8000:8000 --name edgetalk-api edgetalk-api:week9

API测试
健康检查：
curl http://127.0.0.1:8000/health
RAG检索：
curl -X POST "http://127.0.0.1:8000/rag-chat" \
  -H "Content-Type: application/json" \
  -d '{"text":"E03 报警是什么意思？","retriever_type":"embedding","top_k":1}'
Agent对话：
curl -X POST "http://127.0.0.1:8000/agent-chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"docker_test","text":"每日点检需要检查哪些项目？"}'
Memory查询：
curl http://127.0.0.1:8000/memory/docker_test
接口耗时统计：
curl -i http://127.0.0.1:8000/health

## 3. 当前部署成果
当前已完成：

Dockerfile 编写；
requirements-api.txt 编写；
Docker 镜像构建；
Docker 容器运行；
/health 接口测试；
/rag-chat 接口测试；
/agent-chat 接口测试；
/memory 接口测试。
EdgeTalk 已经具备基础容器化部署能力，可以作为轻量级 AI API 服务运行。
