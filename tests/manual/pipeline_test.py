import subprocess
from pathlib import Path

from faster_whisper import WhisperModel
from llama_cpp import Llama


AUDIO_PATH = "audio/test.m4a"
MODEL_PATH = "models/qwen1.5b.gguf"  
OUTPUT_AUDIO = "audio/reply.wav"


def transcribe_audio(audio_path: str) -> str:
    """
    ASR模块：音频 -> 文本
    使用 faster-whisper 识别中文语音。
    """
    print("正在加载 Whisper ASR 模型...")
    asr_model = WhisperModel("tiny", device="cpu", compute_type="int8")

    print("正在识别音频...")
    segments, info = asr_model.transcribe(audio_path, language="zh")

    texts = []
    for segment in segments:
        texts.append(segment.text.strip())

    result = " ".join(texts).strip()

    print("检测语言:", info.language)
    print("ASR识别结果:", result)

    return result


def generate_reply(user_text: str) -> str:
    """
    LLM模块：文本 -> 回复
    使用 llama-cpp-python 加载本地 GGUF 模型。
    """
    print("\n正在加载本地 LLM 模型...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=6,
        verbose=False
    )

    prompt = (
        "你是一个本地运行的中文语音助手。"
        "请用简洁、自然的中文回答用户问题，回答不要太长。\n\n"
        f"用户：{user_text}\n"
        "助手："
    )

    print("正在生成回复...")

    output = llm(
        prompt,
        max_tokens=120,
        temperature=0.4,
        stop=["用户：", "\n用户："]
    )

    reply = output["choices"][0]["text"].strip()

    print("LLM回复:", reply)

    return reply


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


def synthesize_speech(text: str, output_audio: str):
    """
    TTS模块：回复文本 -> wav语音文件
    在 WSL 中调用 Windows System.Speech 生成音频。
    """
    print("\n正在进行 TTS 语音合成...")

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


def main():
    print("====== EdgeTalk 全链路测试开始 ======\n")

    user_text = transcribe_audio(AUDIO_PATH)

    if not user_text:
        print("ASR没有识别到有效文本，流程结束。")
        return

    reply = generate_reply(user_text)

    if not reply:
        print("LLM没有生成有效回复，流程结束。")
        return

    synthesize_speech(reply, OUTPUT_AUDIO)

    print("\n====== 全链路测试完成 ======")
    print("输入音频:", AUDIO_PATH)
    print("输出语音:", OUTPUT_AUDIO)


if __name__ == "__main__":
    main()
