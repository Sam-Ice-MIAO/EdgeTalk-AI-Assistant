# Problems and Solutions

## 1. Hugging Face 模型下载失败

###问题
第一次运行 faster-whisper 时，需要从 Hugging Face 下载模型，但出现：
Connection reset by peer
LocalEntryNotFoundError
###原因
模型权重没有下载成功，不是代码逻辑错误
###解决办法
设置Hugging-Face镜像源，同时将Whisper模型从base改为tiny，降低下载和运行成本
export HF_ENDPOINT=https://hf-mirror.com
## 2. pyttsx3在WSL中初始化失败
###问题
使用pyttsx3的时候出现：ValueError: SetVoiceByName failed with unknown return code -1 for voice: gmw/en
###原因
pyttsx3在Linux、WSL下依赖eSpeak，当前环境中的voice配置不稳定
###解决办法
改为在 WSL 中通过 powershell.exe 调用 Windows 本地 System.Speech 生成 wav 文件。该方案仍然是本地离线 TTS，不依赖云端 API，适合原型阶段验证 Text → Audio 流程。
## 3. TTS长句合成中间卡顿
###问题
生成的语音文件前后正常，但是中间部分出现卡顿和丢失
###原因
长中文文本一次性合成时，Windows System.Speech可能出现吞字或者停顿异常
###解决办法
将长文本按中文标点拆成短句，逐句调用Speak合成到同一个wav文件中

