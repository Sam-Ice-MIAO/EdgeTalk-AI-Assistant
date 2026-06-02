# CLI 使用说明

## 1. 运行方式

### 使用默认音频

```bash
python main.py
```

默认读取配置文件中的音频路径，例如：

```text
audio/test.m4a
```

### 指定音频文件

```bash
python main.py --input audio/test.m4a
```

用于测试不同的本地音频文件。

### 录音模式

```bash
python main.py --record --duration 8
```

尝试录音 8 秒，并保存为：

```text
audio/record.wav
```

## 2. 参数说明

| 参数           | 作用          |
| ------------ | ----------- |
| `--input`    | 指定输入音频文件    |
| `--record`   | 启用录音输入      |
| `--duration` | 设置录音时长，单位为秒 |

## 3. 推荐用法

当前最稳定的方式是：

```bash
python main.py --input audio/test.m4a
```

完整流程：

```text
Audio → ASR → Local LLM → TTS → Audio
```

## 4. 说明

录音模式目前是实验功能。由于项目运行在 WSL 环境中，麦克风输入可能不稳定。

如果录音失败，建议先使用 Windows 录音机录制音频，再通过 `--input` 参数运行。


