## 遇到的问题

尝试使用 sounddevice 在 WSL 中录音时，出现：

sounddevice.PortAudioError: Error querying device -1

## 原因分析

该错误说明 sounddevice 没有找到可用的默认输入设备。由于当前项目运行在 WSL 环境中，麦克风输入设备并不一定能被 Ubuntu 子系统直接识别。

## 解决策略

为了不阻塞主流程，当前项目保留固定音频文件输入作为稳定演示方式：

python main.py --input audio/test.m4a

录音输入模块作为尝试功能保留，后续可在原生 Windows Python、原生 Linux 或 Jetson 环境中继续测试。
