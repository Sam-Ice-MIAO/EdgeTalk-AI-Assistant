# 项目模块化重构

## 目标

将前面已经跑通的 ASR、LLM、TTS 测试脚本整理为可复用模块，并通过 main.py 实现统一调用。

## 重构前

项目中主要是测试脚本：

- src/asr_test.py
- src/llm_test.py
- src/tts_test.py
- src/pipeline_test.py

这些脚本可以验证功能，但不适合作为长期维护的项目结构。

## 重构后

将项目拆分为三个核心模块：

- src/asr/whisper_asr.py：负责 Audio → Text
- src/llm/local_llm.py：负责 Text → Reply
- src/tts/windows_tts.py：负责 Reply → Audio

并使用 main.py 串联完整流程。

