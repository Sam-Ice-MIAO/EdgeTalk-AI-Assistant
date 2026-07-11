# Memory API 使用说明

## 1. 功能目标

Memory API 用于让 EdgeTalk 支持按照 `session_id` 保存和查询多轮对话记录。

在工业设备维护场景中，`session_id` 可以表示一条产线、一台设备、一次故障排查任务或一次测试会话。

例如：

```text
factory_line_01
```

可以表示 1 号产线的一次故障排查记录。

---

## 2. session_id 的作用

`session_id` 用于区分不同会话，避免不同用户、不同设备或不同故障排查记录混在一起。

例如：

```text
factory_line_01：E03 报警排查
factory_line_02：每日点检咨询
```

这样系统可以分别保存和查询它们的历史对话。

---

## 3. 数据存储方式

当前使用 SQLite 保存会话记录。

数据库路径：

```text
data/memory/edgetalk.db
```

主要保存字段：

| 字段         | 说明               |
| ---------- | ---------------- |
| session_id | 会话 ID            |
| role       | user 或 assistant |
| content    | 对话内容             |
| created_at | 创建时间             |

数据库文件不提交到 GitHub，应在 `.gitignore` 中排除：

```gitignore
data/memory/*.db
```

---

## 4. 接口一：Agent 对话接口

### 请求方式

```text
POST /agent-chat
```

### 请求示例

```bash
curl -X POST "http://127.0.0.1:8000/agent-chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"factory_line_01","text":"E03 报警是什么意思？"}'
```

### 参数说明

| 参数         | 说明                   |
| ---------- | -------------------- |
| session_id | 会话 ID，不传时默认为 default |
| text       | 用户问题                 |

该接口会完成两件事：

1. 调用 Agent 回答问题；
2. 将用户问题和助手回答保存到 Memory 中。

---

## 5. 接口二：查询会话记忆

### 请求方式

```text
GET /memory/{session_id}
```

### 请求示例

```bash
curl "http://127.0.0.1:8000/memory/factory_line_01"
```

### 返回内容

接口会返回该 `session_id` 下保存的历史消息，包括用户问题、助手回答和创建时间。

---

## 6. Day4 测试结果

Day4 测试中，完成了以下验证：

1. `/health` 可以正常访问；
2. `/agent-chat` 可以接收 `session_id`；
3. 用户问题和助手回答可以写入 SQLite；
4. `/memory/{session_id}` 可以查询历史记录；
5. `factory_line_01` 和 `factory_line_02` 的记录可以分开保存。

说明当前 Memory API 已经具备基础会话保存和查询能力。

---

## 7. 当前限制

当前版本仍有以下限制：

1. Memory 主要用于保存和查询历史记录；
2. 当前还没有充分利用历史对话辅助后续回答；
3. 同一个 `session_id` 多次测试后，历史记录会持续累积；
4. 当前没有提供清空某个 session 的接口；
5. 当前使用 SQLite，适合本地 Demo，云上版本可迁移到 MySQL、PostgreSQL 或 RDS。

---

