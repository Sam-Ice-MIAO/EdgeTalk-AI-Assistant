from src.asr.whisper_asr import WhisperASR
from src.llm.local_llm import LocalLLM
from src.tts.windows_tts import WindowsTTS


from config.settings import (
    ASR_MODEL_SIZE,
    AUDIO_INPUT_PATH,
    AUDIO_OUTPUT_PATH,
    LLM_MODEL_PATH,
)


def main():
    print("====== EdgeTalk v1.0 启动 ======")

    asr = WhisperASR(model_size=ASR_MODEL_SIZE)
    llm = LocalLLM(model_path=LLM_MODEL_PATH)
    tts = WindowsTTS()

    print("\n[1/3] ASR：正在识别语音...")
    user_text = asr.transcribe(AUDIO_PATH)

    if not user_text:
        print("没有识别到有效文本，程序结束。")
        return

    print("\n[2/3] LLM：正在生成回复...")
    reply = llm.generate(user_text)

    if not reply:
        print("LLM没有生成有效回复，程序结束。")
        return

    print("\n[3/3] TTS：正在生成语音...")
    tts.synthesize(reply, AUDIO_OUTPUT_PATH)

    print("\n====== EdgeTalk v0.1 运行完成 ======")
    print("用户语音识别结果:", user_text)
    print("助手回复:", reply)
    print("输出音频:", OUTPUT_AUDIO)


if __name__ == "__main__":
    main()
