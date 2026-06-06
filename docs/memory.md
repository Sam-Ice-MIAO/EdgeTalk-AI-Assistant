# 对话记忆模块

## 目标

为 EdgeTalk 增加基础对话记录能力，将用户输入和助手回复保存到本地 SQLite 数据库中。

## 当前实现

现阶段使用 SQLite 保存对话消息。

数据表为 `messages`，主要字段包括：

| 字段 | 说明 |
|---|---|
| `session_id` | 会话 ID |
| `role` | 消息角色，user 或 assistant |
| `content` | 消息内容 |
| `created_at` | 创建时间 |

## 当前能力

已支持：

- 保存用户消息；
- 保存助手回复；
- 按 `session_id` 查询最近对话记录。

