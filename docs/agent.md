# Agent 模块设计

## 1. 目标

为 EdgeTalk 增加轻量级 Agent 能力，使系统不仅能直接回答问题，还能根据用户问题调用本地工具。

## 2. Agent 是什么

在本项目中可以理解为 LLM +工具+调度逻辑， LLM 负责生成自然语言回答，工具执行具体操作，调度逻辑负责判断用户问题需要调用哪个工具

## 3.加入 Agent 的原因

普通/chat 接口只会把用户问题直接交给 LLM ，/rag-chat接口会先检索知识库，再让 LLM 基于资料回答
而 Agent 的目标是先判断任务类型-选择是否调用工具-拿到工具结果-再让 LLM 组织最终回答，Agent 更适合处理需要查资料、列文件和查询项目状态等任务

## 4.当前版本设计
 
规则路由+本地工具函数+LLM总结

## 5.第一版支持的工具

1.list_knowledge_files ：作用：列出data/knowledge 目录下的知识库文件
2.search_knowledge ：作用：调用已有的SimpleRetriever，在本地知识库中检索相关内容
3.get_projects_status：作用：返回 EdgeTalk 当前项目状态说明

## 6. AgentCore 调度逻辑

当前已实现 `AgentCore`，用于根据用户问题选择本地工具。

当前规则：

| 用户问题类型 | 使用工具 |
|---|---|
| 询问知识库文件 | `list_knowledge_files` |
| 询问 EdgeTalk 功能、计划、RAG、接口等 | `search_knowledge` |
| 询问项目状态 | `get_project_status` |
| 其他普通问题 | `chat` |

## 7. 接入 FastAPI

当前已将 AgentCore 接入 FastAPI，新增 `/agent-chat` 接口。

接口流程：

```text
用户问题
↓
/agent-chat
↓
AgentCore 判断工具
↓
调用本地工具
↓
工具结果作为上下文
↓
LocalLLM 生成最终回答
