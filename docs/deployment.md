# EdgeTalk Pro Deployment

## 1. Deployment Overview

EdgeTalk Pro 支持两种主要运行方式：

```text
Development
→ FastAPI + Vite

Production Demo
→ Docker Compose + Nginx + FastAPI
```

当前推荐的 PoC 展示与交付方式为：

```text
Docker Compose Production Deployment
```

生产环境入口：

```text
http://localhost:8080
```

---

## 2. Requirements

推荐环境：

```text
Linux / WSL2
Python 3.11
Docker
docker-compose
Node.js 22+（仅开发环境需要）
```

当前项目开发过程中主要使用：

```text
Python 3.11
Node.js 22
```

---

## 3. Local Model

EdgeTalk Pro 使用本地 GGUF 模型：

```text
models/qwen1.5b.gguf
```

模型文件不会提交到 Git 仓库。

启动前确认：

```bash
ls -lh models/qwen1.5b.gguf
```

模型需要存在于：

```text
models/
```

目录中。

---

## 4. Embedding Model

Industrial RAG 使用：

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Embedding 模型通过 Hugging Face Cache 复用。

默认宿主机 Cache：

```text
~/.cache/huggingface
```

Docker 中挂载至：

```text
/root/.cache/huggingface
```

---

## 5. Development Environment

### Backend

进入项目：

```bash
cd ~/projects/EdgeTalk-AI-Assistant
```

激活 Python 3.11 环境：

```bash
source .venv311/bin/activate
```

启动 FastAPI：

```bash
python -m uvicorn src.api.app:app \
  --host 0.0.0.0 \
  --port 8000
```

访问：

```text
http://localhost:8000
```

API Docs：

```text
http://localhost:8000/docs
```

---

### Frontend

打开另一个终端：

```bash
cd ~/projects/EdgeTalk-AI-Assistant/frontend
```

首次运行：

```bash
npm install
```

启动：

```bash
npm run dev
```

访问：

```text
http://localhost:5173
```

开发环境 API：

```text
http://127.0.0.1:8000
```

---

## 6. Production Docker Architecture

生产环境采用：

```text
React
+
Nginx
+
FastAPI
+
Local LLM
+
Embedding RAG
+
SQLite Memory
```

整体链路：

```text
Browser
   ↓
localhost:8080
   ↓
Nginx
   ├── React Static Files
   │
   └── /api/*
          ↓
      FastAPI :8000
          ↓
      Agent / RAG / LLM
```

Docker Compose 文件：

```text
docker-compose.pro.yml
```

主要 Dockerfile：

```text
docker/Dockerfile.api
frontend/Dockerfile.prod
```

---

## 7. Production Configuration

前端生产环境：

```text
frontend/.env.production
```

配置：

```text
VITE_API_BASE_URL=/api
```

因此浏览器不会直接访问：

```text
localhost:8000
```

而是通过：

```text
localhost:8080/api/*
```

由 Nginx 转发至 FastAPI。

---

## 8. Nginx Reverse Proxy

生产环境 Nginx 负责：

```text
/
→ React Static Files

/api/*
→ FastAPI
```

核心代理关系：

```text
Browser
↓
http://localhost:8080/api/agent-chat
↓
Nginx
↓
http://api:8000/agent-chat
```

其中：

```text
api
```

是 Docker Compose 内部的 Service Name。

---

## 9. Docker Volumes

Production Compose 使用 Volume 将模型和运行时数据保存在宿主机。

主要映射：

```text
./models
→ /app/models

./data
→ /app/data

./eval
→ /app/eval

./reports
→ /app/reports

~/.cache/huggingface
→ /root/.cache/huggingface
```

这样可以保证：

```text
代码
→ Docker Image

模型
→ Host Volume

知识库 / Memory / Evaluation
→ Host Volume
```

避免将大模型和运行时数据直接写入 Docker Image。

---

## 10. Hugging Face Offline Mode

EdgeTalk Pro 的生产容器默认使用本地 Embedding Cache。

Compose 中配置：

```text
HF_HOME=/root/.cache/huggingface
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
HF_HUB_DISABLE_TELEMETRY=1
```

作用：

```text
SentenceTransformer
↓
直接读取本地 Hugging Face Cache
↓
避免运行时访问外部 Hugging Face Hub
```

因此生产环境启动前，应确保 Embedding 模型已经存在于本地 Cache 中。

可以检查：

```bash
find ~/.cache/huggingface \
  -maxdepth 4 \
  -type d \
  | grep -i "paraphrase-multilingual"
```

---

## 11. One-command Startup

进入项目：

```bash
cd ~/projects/EdgeTalk-AI-Assistant
```

执行：

```bash
./scripts/start_pro.sh
```

启动脚本会依次完成：

```text
Docker Environment Check
        ↓
API / Web Container Start
        ↓
FastAPI Health Check
        ↓
Wait Until Healthy
        ↓
RAG Warm-up
        ↓
EdgeTalk Pro Ready
```

脚本最终会输出：

```text
Web:
http://localhost:8080

FastAPI:
http://localhost:8000

FastAPI Docs:
http://localhost:8000/docs
```

---

## 12. Service Status

查看：

```bash
docker-compose \
  -f docker-compose.pro.yml \
  ps
```

正常状态：

```text
edgetalk-pro-api    Up (healthy)
edgetalk-pro-web    Up
```

注意：

```text
Container Up
```

并不代表：

```text
AI Service Ready
```

FastAPI 加载本地模型需要一定时间，因此应以：

```text
Up (healthy)
```

作为 API 可以接受请求的判断标准。

---

## 13. Health Check

直接访问 FastAPI：

```bash
curl -s \
"http://127.0.0.1:8000/health" \
| python -m json.tool --no-ensure-ascii
```

正常组件状态应包括：

```text
api: ready
rag: ready
retriever: embedding
agent: ready
llm: ready
memory: sqlite
```

---

### Nginx Proxy Health

```bash
curl -s \
"http://127.0.0.1:8080/api/health" \
| python -m json.tool --no-ensure-ascii
```

如果同样返回正常状态，则说明：

```text
Nginx
↓
FastAPI
```

代理链路正常。

---

## 14. Production Web

浏览器访问：

```text
http://localhost:8080
```

主要页面：

```text
AI Assistant
Knowledge Base
PoC Evaluation
System Status
```

生产环境不使用：

```text
localhost:5173
```

`5173` 仅用于 Vite 开发环境。

---

## 15. Smoke Test

Docker API Container 内可以运行完整 Smoke Test：

```bash
docker-compose \
  -f docker-compose.pro.yml \
  exec api \
  python scripts/smoke_test.py
```

当前 Smoke Test 主要验证：

```text
Health API
Industrial RAG
Multi-turn RAG
Realtime Guardrail
Local LLM Chat
Evaluation API
PoC Report API
```

验收目标：

```text
Passed: 7/7
Smoke Test: PASS
```

---

## 16. PoC Evaluation

Docker 容器内运行：

```bash
docker-compose \
  -f docker-compose.pro.yml \
  exec api \
  python eval/run_eval.py
```

当前确定性测试基线：

```text
Total: 12
Passed: 12
Failed: 0
Acceptance: PASS
```

Evaluation 结果写入：

```text
eval/results/latest.json
```

由于 `eval` 目录使用 Volume，该结果会同步保存至宿主机。

---

## 17. PoC Report

生成报告：

```bash
docker-compose \
  -f docker-compose.pro.yml \
  exec api \
  python scripts/generate_poc_report.py
```

输出：

```text
reports/latest_poc_report.md
```

`reports` 目录通过 Volume 与宿主机同步。

Web 页面同时支持：

```text
PoC Report Preview
PoC Report Download
```

---

## 18. SQLite Persistence

默认 Production Memory Backend：

```text
SQLite
```

数据库：

```text
data/memory/edgetalk.db
```

由于：

```text
./data
→ /app/data
```

使用 Volume 挂载，因此：

```text
Container Stop
Container Remove
Container Restart
```

不会删除 SQLite 中已有的 Session Memory。

---

## 19. Stop EdgeTalk Pro

执行：

```bash
./scripts/stop_pro.sh
```

查看：

```bash
docker-compose \
  -f docker-compose.pro.yml \
  ps
```

停止后不应再有运行中的：

```text
edgetalk-pro-api
edgetalk-pro-web
```

---

## 20. Restart

重新启动：

```bash
./scripts/start_pro.sh
```

等待：

```text
EdgeTalk Pro is ready.
```

再访问：

```text
http://localhost:8080
```

---

## 21. Logs

查看 API 日志：

```bash
docker-compose \
  -f docker-compose.pro.yml \
  logs --tail=100 api
```

持续查看：

```bash
docker logs \
  -f \
  edgetalk-pro-api
```

查看 Web：

```bash
docker-compose \
  -f docker-compose.pro.yml \
  logs --tail=100 web
```

---

## 22. Resource Usage

查看容器资源：

```bash
docker stats \
  --no-stream \
  edgetalk-pro-api \
  edgetalk-pro-web
```

主要关注：

```text
CPU
Memory
Network I/O
```

当前项目定位为本地 PoC，因此未对 Docker Image Size 和运行资源进行生产级深度优化。

---

## 23. MySQL Extension

项目代码层仍保留 MySQL Memory Backend：

```text
src/memory/mysql_memory.py
src/memory/memory_factory.py
```

当前 EdgeTalk Pro Production Compose 默认使用：

```text
SQLite
```

MySQL 可作为后续企业数据库集成扩展。

---

## 24. Voice Extension

完整语音链路可在本地开发环境中独立运行：

```text
Audio
↓
ASR
↓
Agent
↓
RAG / Local LLM
↓
Memory
↓
TTS
```

当前 Production Docker Web 版本主要交付文本交互能力，ASR / TTS 不作为默认 Docker 服务启动。

---

## 25. Deployment Boundary

当前部署方案定位为：

```text
Local / Single-machine AI PoC
```

适用于：

- 本地 Demo
- 售前 PoC
- 工业 AI 方案展示
- 功能验证
- Evaluation 与验收演示
