# EdgeTalk v0.1 Architecture

## 1. 项目目标

EdgeTalk 是一个本地运行的语音助手原型，当前 v0.1 版本目标是跑通最小语音交互闭环：
Audio → ASR → Local LLM → TTS → Audio
## 2. 系统流程
audio/test.m4a
    ↓
ASR 模块：faster-whisper
    ↓
用户文本 user_text
    ↓
LLM 模块：llama-cpp-python + GGUF
    ↓
助手回复 reply
    ↓
TTS 模块：Windows System.Speech
    ↓
audio/reply.wav
## 3. 模块说明
# ASR
文件：src/asr/whisper_asr.py
作用：Audio → Text
当前使用faster-whisper tiny模型，在CPU上完成中文语音识别
# LLM
文件：src/llm/local_llm.py
作用：Text → Reply
当前使用llama-cpp-python加载本地GGUF量化模型完成回复生成
# TTS
文件：src/tts/windows_tts.py
作用：Reply → Audio
当前在WSL中通过powershell.exe调用Windows System。Speech生成wav文件
## 4. 当前限制
·现阶段输入的是固定音频文件，不是实时录音；
·ASR使用的是tiny模型，识别能力有限；
·LLM在CPU上推理速度较慢；
·TTS使用Windows System。Speech，适合原型验证，不是最终部署方案；
·现阶段还未加入多轮对话、RAG部署和Jetson部署
## 5. 后续计划
·增加录音输入
·支持多轮对话
·加入RAG知识库问答
·测量各模块耗时
·尝试部署到Jetson

