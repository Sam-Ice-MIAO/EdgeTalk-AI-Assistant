# EdgeTalk-AI-Assistant Architecture

## 1. 项目概述

EdgeTalk-AI-Assistant 是一个面向工业设备维护场景的本地化 AI 助手 PoC Demo。

项目目标是验证企业知识库问答在工业设备维护场景中的可行性，支持故障码查询、维修 SOP 查询、点检规范查询、安全规范问答和多轮维护对话。

项目核心能力包括：

- 工业知识库管理
- RAG 检索增强问答
- Agent 工具路由
- 本地 LLM 推理
- SQLite / MySQL 会话记忆
- FastAPI 接口服务
- ASR 语音输入
- TTS 语音输出
- Docker / Docker Compose 部署验证

---

## 2. 整体架构

项目整体链路如下：

```text
用户输入
  ├── 文本输入
  └── 音频输入
        ↓
ASR 语音识别
        ↓
Agent 工具路由
        ↓
RAG 知识库检索
        ↓
本地 LLM 生成回答
        ↓
Memory 保存会话
        ↓
文本回答 / TTS 语音输出
```

API 服务链路如下：

```text
Client / curl / 前端 / PoC 测试工具
        ↓
FastAPI
        ↓
/rag-chat      → RAG 检索问答
/agent-chat    → Agent 工具调用问答
/memory/{id}   → 会话记录查询
/health        → 服务健康检查
        ↓
SQLite / MySQL
```

---

## 3. 核心模块说明

### 3.1 ASR 模块

文件位置：

```text
src/asr/whisper_asr.py
```

作用：

- 将音频文件转换为文本；
- 为后续 Agent、RAG 和 LLM 提供文本输入；
- 当前基于 faster-whisper 实现。

当前方案：

- 使用 faster-whisper；
- 当前更适合使用 small 模型进行项目展示；
- tiny 模型速度更快，但中文识别稳定性较弱。

---

### 3.2 RAG 模块

文件位置：

```text
src/rag/
```

主要文件：

```text
document_loader.py
simple_retriever.py
embedding_retriever.py
```

作用：

- 加载工业设备维护知识库；
- 将文档切分为可检索片段；
- 支持 TF-IDF baseline 和 Embedding Retriever；
- 根据用户问题检索相关故障码、SOP、点检、安全规范内容。

知识库目录：

```text
data/knowledge/industrial/
```

当前优化：

- 使用 min_score 过滤低相关内容；
- 使用 top_k 控制返回片段数量；
- 对故障码类问题加入规则增强；
- 对不同知识来源加入 source boost；
- 优化文档切分，避免不同故障码内容混在同一 chunk 中。

---

### 3.3 Agent 模块

文件位置：

```text
src/agent/
```

主要文件：

```text
agent_core.py
tools.py
```

作用：

- 判断用户问题类型；
- 决定是否调用知识库检索工具；
- 将工具返回结果交给 LLM 生成回答；
- 将用户问题和助手回答写入 Memory。

当前工具包括：

```text
list_knowledge_files
search_knowledge
get_project_status
```

Agent 路由逻辑：

```text
故障码 / SOP / 点检 / 安全规范类问题
→ 调用 search_knowledge

普通问题
→ 直接走基础回答逻辑

项目状态相关问题
→ 调用 get_project_status
```

---

### 3.4 LLM 模块

文件位置：

```text
src/llm/local_llm.py
```

作用：

- 加载本地 GGUF 模型；
- 基于用户问题和 RAG context 生成回答；
- 支持本地化、离线化的问答能力。

当前方案：

```text
llama-cpp-python + GGUF
```

模型文件不上传 GitHub，需要用户自行放入：

```text
models/qwen1.5b.gguf
```

---

### 3.5 Memory 模块

文件位置：

```text
src/memory/
```

作用：

- 保存用户问题和助手回答；
- 支持根据 session_id 查询历史会话；
- 为多轮维护问答提供基础记忆能力。

当前支持两种后端：

| 后端 | 说明 |
|---|---|
| SQLite | 默认本地存储，适合本地 Demo 和轻量运行 |
| MySQL | 可选存储，适合模拟企业部署和云端数据库场景 |

后端切换方式：

```text
MEMORY_BACKEND=sqlite
MEMORY_BACKEND=mysql
```

---

### 3.6 TTS 模块

文件位置：

```text
src/tts/windows_tts.py
```

作用：

- 将 LLM 生成的文本回答转换为语音文件；
- 用于验证完整语音助手链路。

当前方案：

```text
Windows System.Speech
```

当前限制：

- 适合 Windows / WSL 开发环境；
- 不适合直接部署到 Jetson；
- 后续 Jetson 部署时需要替换为 Linux 可用 TTS 方案。

---

### 3.7 Pipeline 模块

文件位置：

```text
src/pipeline.py
```

作用：

- 编排 ASR、LLM、TTS 等模块；
- 支持文本输入和音频输入；
- 用于验证从输入到输出的完整链路。

典型链路：

```text
Audio
→ ASR
→ Text
→ Agent / RAG
→ LLM
→ Reply
→ TTS
→ Audio Output
```

---

### 3.8 API 模块

文件位置：

```text
src/api/app.py
```

作用：

- 使用 FastAPI 对外提供服务接口；
- 支持 RAG 问答、Agent 问答和 Memory 查询；
- 便于前端集成、PoC 测试和部署验证。

核心接口：

| 接口 | 作用 |
|---|---|
| GET /health | 服务健康检查 |
| POST /chat | 基础文本问答 |
| POST /rag-chat | RAG 检索增强问答 |
| POST /agent-chat | Agent 工具调用问答 |
| GET /memory/{session_id} | 查询会话历史 |

当前请求体字段以 `text` 为主，例如：

```json
{
  "text": "E03 报警是什么意思？",
  "retriever_type": "embedding"
}
```

---

## 4. 部署架构

### 4.1 本地运行

本地开发环境：

```text
Windows + WSL / Ubuntu
Python 3.11
venv 虚拟环境
```

适合验证：

- RAG
- Agent
- Memory
- FastAPI
- 本地 LLM
- ASR / TTS 完整链路

---

### 4.2 Docker 部署

Docker 主要用于验证轻量 API 服务部署。

```text
Dockerfile
requirements-api.txt
FastAPI
RAG / Agent / Memory
```

当前 Docker API 版本保持轻量，不强制加载完整 ASR / TTS / LLM 链路，以降低部署复杂度。

---

### 4.3 Docker Compose + MySQL

Docker Compose 用于验证：

```text
FastAPI 服务 + MySQL 数据库
```

主要目的：

- 验证 MySQLMemory；
- 模拟企业部署中的 API + 数据库结构；
- 为后续 PoC 测试和云端部署打基础。

---

### 4.4 Jetson 边缘部署计划

后续计划部署到 Jetson Orin Nano，验证边缘端工业 AI 助手运行效果。

需要重点处理：

- ARM 架构依赖适配；
- 本地 LLM 推理性能；
- ASR 模型速度；
- WindowsTTS 替换为 Linux TTS；
- 边缘端内存和响应时间测试。

---

## 5. 当前完成情况

| 模块 | 状态 |
|---|---|
| 工业知识库 | 已完成 |
| TF-IDF RAG | 已完成 |
| Embedding RAG | 已完成 |
| Agent 工具路由 | 已完成 |
| SQLite Memory | 已完成 |
| MySQL Memory | 已完成 |
| FastAPI API | 已完成 |
| Docker API 部署 | 已完成 |
| Docker Compose + MySQL | 已验证 |
| ASR / LLM / TTS 全链路 | 已跑通 |
| Jetson 部署 | 后续计划 |

---

## 6. 当前限制

当前项目仍属于 PoC Demo，主要限制包括：

1. 知识库规模较小，主要用于场景验证；
2. 前端页面暂未实现，当前主要通过命令行和 API 测试；
3. 实时麦克风输入暂未作为核心能力，当前以音频文件输入为主；
4. TTS 当前依赖 Windows System.Speech，后续 Jetson 部署需要替换；
5. Jetson 实机部署暂未完成；
6. RAG 评估仍以典型问题验证为主，后续可扩展为系统化 PoC 评测。

---

## 7. 架构价值

本项目架构的核心价值在于：

1. 从工业客户场景出发，而不是做泛用聊天机器人；
2. 通过 RAG 降低本地模型幻觉风险；
3. 通过 Agent 工具路由增强业务交互能力；
4. 通过 Memory 支持多轮维护问答；
5. 通过 FastAPI 提供可集成接口；
6. 通过 Docker 和 MySQL 验证企业部署可行性；
7. 为后续 Jetson 边缘部署和 PoC 评估工具预留扩展空间。
