# 耗时统计

## 目标

为 EdgeTalk 的 ASR、LLM、TTS 三个模块加入耗时统计，用于分析系统瓶颈。

## 实现方式

使用 `time.perf_counter()` 和 `contextmanager` 实现简单计时器，并在 `main.py` 中分别统计：

- ASR 耗时2.17秒
- LLM 耗时5.37秒
- TTS 耗时2.48秒
- 总流程耗时10.03秒

## 当前观察

当前系统在 CPU 环境下运行，本地 LLM 推理通常是主要耗时来源。

