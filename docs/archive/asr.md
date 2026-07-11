# Day 2：ASR 模块测试记录

## 目标

验证本地语音识别流程是否可行：

Audio → Whisper → Text

本阶段只关注 ASR 模块，不涉及 LLM 和 TTS。

## 实现方式

使用 faster-whisper 加载 Whisper tiny 模型，在 CPU 上进行推理。

- 模型：Whisper tiny
- 设备：CPU
- 计算类型：int8
- 输入音频：audio/test.m4a
- 输出结果：中文文本

##遇到的问题
第一次运行时，模型需要从Hugging Face下载，但出现了网络中断，出现Connection reset by peer报错，说明模型权重没有成功下载。
解决：
设置了Hugging-Face镜像源：export HF_ENDPOINT=https://hf-mirror.com，将模型和从base改成了tiny，降低下载和运行成本，最终成功识别出中文语音。

## 核心代码

```python
from faster_whisper import WhisperModel

model = WhisperModel("tiny", device="cpu", compute_type="int8")

segments, info = model.transcribe("audio/test.m4a", language="zh")

print("检测语言:", info.language)
print("语言概率:", info.language_probability)

print("\n识别结果：")
for segment in segments:
    print(segment.text)
