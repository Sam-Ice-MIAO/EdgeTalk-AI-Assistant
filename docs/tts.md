# TTS 模块测试记录

## 目标

验证本地文本转语音流程：

Text → TTS → Audio

## 实现方式

最初尝试使用 pyttsx3，但在 WSL 环境下调用 eSpeak 出现 voice 配置错误。随后改为在 WSL 中通过 powershell.exe 调用 Windows 本地 System.Speech 生成 wav 文件。

## 遇到的问题

使用 pyttsx3 初始化时出现：

ValueError: SetVoiceByName failed with unknown return code -1 for voice: gmw/en

分析后判断，这是 WSL 环境下 eSpeak voice 配置问题，不是业务代码错误。

## 解决方案

改用 Windows System.Speech 作为临时 TTS 后端，通过 PowerShell 生成 audio/reply.wav。

后续发现长句合成时中间部分可能出现卡顿，因此进一步将长文本按中文标点拆成短句，再逐句合成，提高稳定性。

## 结果

成功生成 reply.wav，并能在 Windows 中播放。


