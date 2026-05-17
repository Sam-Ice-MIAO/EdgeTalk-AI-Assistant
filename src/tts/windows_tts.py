import subprocess
from pathlib import Path


def escape_powershell_string(text: str) -> str:
    return text.replace("'", "''")


def split_text(text: str):
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


class WindowsTTS:
    def synthesize(self, text: str, output_audio: str):
        output_path = Path(output_audio).resolve()
        output_path.parent.mkdir(exist_ok=True)

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

        script_path = output_path.parent / "tts_temp.ps1"
        script_path.write_text(ps_script, encoding="utf-8-sig")

        win_script_path = subprocess.check_output(
            ["wslpath", "-w", str(script_path.resolve())],
            text=True
        ).strip()

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

        print("TTS语音文件已生成:", output_path)
