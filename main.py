import argparse
from pathlib import Path

from config.settings import (
    ASR_MODEL_SIZE,
    AUDIO_INPUT_PATH,
    AUDIO_OUTPUT_PATH,
    LLM_MODEL_PATH,
)

from src.asr.whisper_asr import WhisperASR
from src.llm.local_llm import LocalLLM
from src.tts.windows_tts import WindowsTTS
from src.utils.timer import timer


def parse_args():
    parser = argparse.ArgumentParser(description="EdgeTalk local voice assistant")

    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input audio file"
    )

    parser.add_argument(
        "--record",
        action="store_true",
        help="Record audio from microphone"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Recording duration in seconds"
    )

    return parser.parse_args()


def main():
    print("====== EdgeTalk v1.0 启动 ======")

    args = parse_args()

    if args.record:
        from src.audio.recorder import record_audio

        audio_path = record_audio(
            output_path="audio/record.wav",
            duration=args.duration
        )

        if not audio_path:
            print("录音失败，程序结束。")
            print("建议先使用固定音频文件模式：")
            print("python main.py --input audio/test.m4a")
            return
    else:
        audio_path = args.input if args.input else AUDIO_INPUT_PATH

    if not Path(audio_path).exists():
        print(f"音频文件不存在: {audio_path}")
        return

    if not Path(LLM_MODEL_PATH).exists():
        print(f"模型文件不存在: {LLM_MODEL_PATH}")
        return

    try:
        with timer("总流程"):
            print("\n[1/3] ASR：正在识别语音...")
            with timer("ASR"):
                asr = WhisperASR(model_size=ASR_MODEL_SIZE)
                user_text = asr.transcribe(audio_path)

            if not user_text:
                print("ASR 没有识别到有效文本，程序结束。")
                return

            print("\n[2/3] LLM：正在生成回复...")
            with timer("LLM"):
                llm = LocalLLM(model_path=LLM_MODEL_PATH)
                reply = llm.generate(user_text)

            if not reply:
                print("LLM 没有生成有效回复，程序结束。")
                return

            print("\n[3/3] TTS：正在生成语音...")
            with timer("TTS"):
                tts = WindowsTTS()
                tts.synthesize(reply, AUDIO_OUTPUT_PATH)

            print("\n====== EdgeTalk v1.0 运行完成 ======")
            print("输入音频:", audio_path)
            print("用户语音识别结果:", user_text)
            print("助手回复:", reply)
            print("输出音频:", AUDIO_OUTPUT_PATH)

    except Exception as e:
        print("程序运行失败:", e)


if __name__ == "__main__":
    main()
