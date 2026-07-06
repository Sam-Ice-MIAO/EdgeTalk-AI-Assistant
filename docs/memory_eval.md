# Memory 多轮对话测试记录

## 1. 测试目标

验证 EdgeTalk 是否能够通过 session_id 保存多轮对话记录，并区分不同会话。

## 2. 测试接口

- POST /agent-chat
- GET /memory/{session_id}

## 3. 测试场景

### 场景一：E03 报警排查

session_id：factory_line
测试问题：
1.E03报警是什么意思
2.那我第一步应该检查什么
3.如果接线正常下一步查什么
4.更换传感器要确认什么
测试结论：
系统可以保存用户问题，可以保存助手回答，可以通过memory/factory_line查询历史记录当前memory主要用于保存记录，尚未充分参与后续回答生成
### 场景二每日点检咨询

session_id
inspection
测试问题：每日点检需要检查哪些项目
测试结论：inspection和 factory_line的记录可以分开保存；
不同 session_id 之间实现了基础会话隔离。

