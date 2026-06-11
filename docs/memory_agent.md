# Agent Memory 接入说明

## 1. 目标

本阶段将 SQLite Memory 接入 AgentCore，使 EdgeTalk 能够按照 session_id 保存用户与助手的对话记录。

## 2. 当前实现

当前使用 SQLite 作为本地轻量级会话存储，数据库路径为：

```text
data/memory/edgetalk.db
核心表位 messages,字段包括：id,session_id,role,content,created_at

## 3. 当前能力
当前的 Memory 能力包括：1.保存多轮对话；2.按 session_id 区分不同会话；3.查询最近若干条历史消息

## 4. 当前限制
现阶段版本只是保存对话记录，尚未深度参与 LLM 推理，后续可以将最近几轮对话拼接到 prompt 中，用于支持更自然的多轮故障排查
