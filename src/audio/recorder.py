import sounddevice as sd
from sounddevice import PortAudioError
from scipy.io.wavfile import write
from pathlib import Path


def record_audio(
    output_path: str = "audio/record.wav",
    duration: int = 5,
    sample_rate: int = 16000
):
    output = Path(output_path)
    output.parent.mkdir(exist_ok=True)

    print(f"开始录音，时长 {duration} 秒...")

    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        write(str(output), sample_rate, audio)

        print(f"录音完成，文件保存到: {output}")

        return str(output)

    except PortAudioError as e:
        print("录音失败：当前 WSL 环境没有检测到可用的麦克风输入设备。")
        print("错误信息:", e)
        print("建议：先使用 Windows 录音机录制音频，再复制到 audio/ 目录中进行测试。")

        return None


def list_audio_devices():
    print(sd.query_devices())
    print("默认设备:", sd.default.device)
