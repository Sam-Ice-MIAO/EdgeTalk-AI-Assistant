# ASR + LLM + TTS 全链路测试

## 目标

将前面已经跑通的三个模块串联起来：

Audio → ASR → LLM → TTS → Audio

## 实现流程

1. 使用 faster-whisper 将 audio/test.m4a 转成文本；
2. 将 ASR 识别文本输入本地 GGUF 大模型；
3. 使用 llama-cpp-python 生成中文回复；
4. 通过 Windows System.Speech 将回复转成 reply.wav。

## 当前结果

成功完成从语音输入到语音输出的最小闭环。

## 当前限制

- ASR 使用 Whisper tiny，识别效果有限；
- LLM 在 CPU 上推理速度较慢；
- TTS 使用 Windows System.Speech，适合原型验证，但不是最终部署方案；
- 当前还不是实时录音，只是基于固定音频文件测试。

## 收获

本阶段完成了语音助手最核心的 Pipeline。相比单独调用模型，全链路集成更能暴露模块之间的路径、格式、延迟和稳定性问题。
