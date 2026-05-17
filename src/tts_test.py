import subprocess
from pathlib import Path


def escape_powershell_string(text: str) -> str:
    """处理 PowerShell 单引号转义"""
    return text.replace("'", "''")


def split_text(text: str):
    """把长文本拆成短句，减少 TTS 卡顿和吞字"""
    separators = ["。", "！", "？", "；"]
    sentences = []
    current = ""

    for char in text:
        current += char
        if char in separators:
            sentences.append(current.strip())
            current = ""

    if current.strip():
        sentences.append(current.strip())

    return sentences


def main():
    text = "你好，我是一个本地运行的语音助手。现在正在测试文字转语音功能。"

    output_dir = Path("audio")
    output_dir.mkdir(exist_ok=True)

    output_path = (output_dir / "reply.wav").resolve()

    win_output_path = subprocess.check_output(
        ["wslpath", "-w", str(output_path)],
        text=True
    ).strip()

    sentences = split_text(text)

    speak_commands = ""
    for sentence in sentences:
        if sentence:
            safe_sentence = escape_powershell_string(sentence)
            speak_commands += f"$speaker.Speak('{safe_sentence}')\n"

    ps_script = f"""
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.Rate = -1
$speaker.Volume = 100
$speaker.SetOutputToWaveFile('{escape_powershell_string(win_output_path)}')
{speak_commands}
$speaker.Dispose()
"""

    script_path = (output_dir / "tts_temp.ps1").resolve()
    script_path.write_text(ps_script, encoding="utf-8-sig")

    win_script_path = subprocess.check_output(
        ["wslpath", "-w", str(script_path)],
        text=True
    ).strip()

    print("输入文本：", text)
    print("拆分后句子：")
    for idx, sentence in enumerate(sentences, start=1):
        print(f"{idx}. {sentence}")

    print("正在调用 Windows 本地 TTS...")
    print("输出文件：", output_path)

    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            win_script_path,
        ],
        check=True
    )

    script_path.unlink(missing_ok=True)

    print("TTS 语音文件生成完成：", output_path)


if __name__ == "__main__":
    main()

