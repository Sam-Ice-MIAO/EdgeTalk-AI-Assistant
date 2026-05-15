# 本地 LLM 推理测试记录

## 目标

验证本地大模型推理流程：

Text → Local LLM → Reply

本阶段只关注 LLM 模块，不涉及 ASR 和 TTS 串联。

## 实现方式

使用 llama-cpp-python 加载 GGUF 量化模型，在 CPU 上完成本地推理。

## 模型选择

第一版选择小参数量 GGUF 模型，优先保证可运行性，而不是追求回答质量。

## 核心参数

- model_path：本地模型文件路径
- n_ctx：上下文长度
- n_threads：CPU 推理线程数
- max_tokens：最大生成长度
- temperature：生成随机性
- stop：控制模型停止生成的位置

## 结果

成功完成文本输入到本地模型回复。

