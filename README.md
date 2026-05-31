# EdgeTalk-AI-Assistant
在边缘设备上运行的端到端的语音交互助手
基于Jetson Orin Nano Super(8GB)+量化大模型+RAG知识检索
# 项目愿景
构建一个**完全离线、隐私优先**的智能语音助手，能够在8GB内存的边缘设备上流畅运行7B参数大模型，实现实时语音识别(ASR)→大语言模型推理(LLM)→语音合成(TTS)的全链路交互。
# 项目结构
```
EdgeTalk-AI-Assistant/
├── main.py
├── requirements.txt
├── src/
│   ├── asr/
│   │   └── whisper_asr.py
│   ├── llm/
│   │   └── local_llm.py
│   └── tts/
│       └── windows_tts.py
├── docs/
│   ├── architecture.md
│   └── problems_and_solutions.md
├── audio/
│   └── README.md
└── models/
    └── README.md
```
## 技术栈
| 模块 | 当前方案 | 状态 |
|---|---|---|
| 开发环境 | WSL / Ubuntu 22.04 | 已完成 |
| 语言 | Python 3.x | 已完成 |
| ASR | faster-whisper | 已跑通 |
| LLM | llama-cpp-python + GGUF | 已跑通 |
| TTS | Windows System.Speech | 已跑通 |
| Pipeline | Python main.py | 已跑通 |
| RAG | 待实现 | 计划中 |
| 部署 | 待实现 | 计划中 |
 
## v1.0运行方式
### 1.创建虚拟环境
python3 -m venv venv
source venv/bin/activate
### 2.安装依赖
pip install -r requirements.txt
### 3.准备模型文件
请自行下载GGUF模型文件，并放入：models/
然后在main.py中确认模型路径
### 4.准备测试音频
将测试音频放入：audio/test.m4a
### 5.运行
export HF_ENDPOINT=https://hf-mirror.com
python main.py
运行后会生成：audio/reply.wav
## 当前版本说明
v1.0版本主要验证本地语音助手的最小闭环，现阶段仍有限制，开发记录和下一步计划具体见docs/architecture.md
