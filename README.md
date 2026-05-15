# EdgeTalk-AI-Assistant
在边缘设备上运行的端到端的语音交互助手
基于Jetson Orin Nano Super(8GB)+量化大模型+RAG知识检索
# 项目愿景
构建一个**完全离线、隐私优先**的智能语音助手，能够在8GB内存的边缘设备上流畅运行7B参数大模型，实现实时语音识别(ASR)→大语言模型推理(LLM)→语音合成(TTS)的全链路交互。
# 项目结构
EdgeTalk-AI-Assistant/
```
├── examples/               # 学习示例与模块验证
│   └── csv_sales_processor/  # Python模块化设计练习
├── src/                    # 核心源代码
│   ├── asr/               # 语音识别 (faster-whisper)
│   ├── llm/               # 大模型推理 (llama.cpp)
│   ├── tts/               # 语音合成 (Piper TTS)
│   └── rag/               # 知识检索 (LangChain+ChromaDB)
├── tests/                  # 单元测试
├── docs/                   # 技术文档
└── benchmarks/            # 性能测试数据
```
## 技术栈
| 模块 | 当前方案 | 状态 |
|---|---|---|
| 开发环境 | WSL / Ubuntu 22.04 | 已完成 |
| 语言 | Python 3.x | 已完成 |
| ASR | faster-whisper | 已跑通 |
| LLM | llama-cpp-python + GGUF | 待实现 |
| TTS | pyttsx3 / Piper TTS | 待实现 |
| RAG | ChromaDB / FAISS | 计划中 |
| 部署 | Jetson Orin Nano | 计划中 |
 
