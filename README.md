# EdgeTalk-AI-Assistant

EdgeTalk-AI-Assistant 是一个面向工业设备维护场景的本地化 AI 助手原型，主要用于设备故障代码查询、维修 SOP 查询、巡检规范查询和安全规范问答。

项目围绕企业级 AI 应用 Demo 的交付思路设计，集成了 RAG 知识库检索、Agent 工具调用、会话记忆、FastAPI 服务、本地 LLM 推理、ASR 语音输入、TTS 语音输出以及 Docker 部署能力。后续计划部署到 Jetson Orin Nano 等边缘设备上，用于验证边缘端工业 AI 助手的可行性。

---

## 1. 项目定位

本项目模拟工业设备维护场景中的智能助手需求：

- 维修人员可以查询设备故障码含义；
- 可以根据维修 SOP 获取操作步骤；
- 可以查询每日点检项目和安全注意事项；
- 系统能够保留同一会话中的历史信息；
- 支持本地化部署，适合隐私敏感或网络受限的工业现场。

项目目标不是单纯实现聊天机器人，而是构建一个面向 ToB 场景的 AI 解决方案原型。

---

## 2. 核心功能

| 模块 | 功能说明 |
|---|---|
| 工业知识库 | 构建设备手册、故障码、维修 SOP、巡检规范、安全规范等本地知识文档 |
| RAG 检索 | 支持 TF-IDF baseline 与 Embedding Retriever，用于工业文档语义检索 |
| Agent 工具调用 | 根据用户问题自动选择知识库检索、项目状态查询或普通对话 |
| 本地 LLM | 基于 GGUF 模型进行本地问答生成 |
| Memory | 支持 SQLite 本地会话记忆，并扩展 MySQL 可选后端 |
| FastAPI | 提供 `/rag-chat`、`/agent-chat`、`/memory/{session_id}` 等接口 |
| ASR | 使用 faster-whisper 实现语音识别 |
| TTS | 使用 Windows System.Speech 实现语音合成 |
| Docker | 支持轻量 API 服务容器化部署 |
| Docker Compose | 支持 API + MySQL 一键启动 |

---

## 3. 技术栈

| 方向 | 技术 |
|---|---|
| 后端服务 | FastAPI, Uvicorn |
| RAG | TF-IDF, Sentence-Transformers Embedding |
| Agent | Python Tool Routing |
| LLM | llama-cpp-python, GGUF |
| ASR | faster-whisper |
| TTS | Windows System.Speech |
| Memory | SQLite, MySQL |
| 部署 | Docker, Docker Compose |
| 开发环境 | WSL / Ubuntu, Python 3.11 |

---

## 4. 项目结构

```text
EdgeTalk-AI-Assistant/
├── main.py
├── config/
│   └── settings.py
├── data/
│   └── knowledge/
│       └── industrial/
├── src/
│   ├── agent/
│   ├── api/
│   ├── asr/
│   ├── audio/
│   ├── llm/
│   ├── memory/
│   ├── rag/
│   ├── tts/
│   ├── utils/
│   └── pipeline.py
├── tests/
│   └── manual/
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── rag_eval.md
│   ├── problems_and_solutions.md
│   └── project_positioning.md
├── examples/
├── models/
│   └── README.md
├── audio/
│   └── README.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-api.txt
└── README.md
```

---

## 5. 快速开始

### 5.1 克隆项目

```bash
git clone https://github.com/你的用户名/EdgeTalk-AI-Assistant.git
cd EdgeTalk-AI-Assistant
```

### 5.2 创建虚拟环境

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 5.3 安装轻量 API 依赖

```bash
pip install -r requirements-api.txt
```

### 5.4 启动 FastAPI 服务

```bash
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

测试服务：

```bash
curl http://127.0.0.1:8000/health
```

---

## 6. API 示例

### 6.1 RAG 问答

```bash
curl -X POST "http://127.0.0.1:8000/rag-chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "E03 报警是什么意思？", "retriever_type": "embedding"}'
```

### 6.2 Agent 问答

```bash
curl -X POST "http://127.0.0.1:8000/agent-chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "更换传感器之前需要注意什么？", "session_id": "demo_session"}'
```

### 6.3 查询会话记忆

```bash
curl http://127.0.0.1:8000/memory/demo_session
```

---

## 7. Docker 部署

### 7.1 构建镜像

```bash
docker build -t edgetalk-api .
```

### 7.2 启动 API

```bash
docker run --rm -p 8000:8000 edgetalk-api
```

### 7.3 使用 Docker Compose 启动 API + MySQL

```bash
docker compose up --build
```

如果本机环境不支持 `docker compose`，可以使用：

```bash
docker-compose up --build
```

---

## 8. 本地 LLM 与语音链路

完整语音链路需要额外安装完整依赖：

```bash
pip install -r requirements.txt
```

模型文件不会上传到 GitHub，需要自行下载 GGUF 模型并放入：

```text
models/qwen1.5b.gguf
```

文本模式测试：

```bash
python main.py --text "E03 报警是什么意思？"
```

音频文件模式测试：

```bash
python main.py --audio audio/test.m4a
```

完整链路包括：

```text
语音输入 → ASR → Agent → RAG → LLM → Memory → TTS
```

---

## 9. 当前完成情况

| 能力 | 状态 |
|---|---|
| 工业知识库 | 已完成 |
| TF-IDF RAG | 已完成 |
| Embedding RAG | 已完成 |
| Agent 工具路由 | 已完成 |
| SQLite Memory | 已完成 |
| MySQL Memory | 已完成 |
| FastAPI 服务 | 已完成 |
| Docker 部署 | 已完成 |
| Docker Compose + MySQL | 已完成 |
| ASR / LLM / TTS 完整链路 | 已完成 |
| Jetson Orin Nano 部署 | 后续计划 |

---

## 10. 项目亮点

1. 面向工业设备维护场景，而不是泛用聊天机器人；
2. 结合 RAG、Agent、Memory，形成完整企业知识库问答链路；
3. 支持 SQLite 与 MySQL 两种记忆后端，兼顾本地 Demo 与云端部署思路；
4. 提供 FastAPI 接口和 Docker Compose 部署方式，便于后续 PoC 测试；
5. 支持 ASR 到 TTS 的完整语音助手链路，为后续边缘设备部署做准备。

---

## 11. 后续计划

- 部署到 Jetson Orin Nano，验证边缘端运行效果；
- 替换 Jetson 可用的 Linux TTS 方案；
- 增加 PoC 测试报告生成工具；
- 增加接口性能评估和成本估算能力；
- 结合工业场景扩展更多故障案例和维修流程。

