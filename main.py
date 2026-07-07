import argparse
from pathlib import Path

from src.asr.whisper_asr import WhisperASR
from src.pipeline import EdgeTalkPipeline
from src.agent.agent_core import AgentCore
from src.tts.windows_tts import WindowsTTS


def parse_args():
    parser = argparse.ArgumentParser(
        description="EdgeTalk industrial voice assistant"
    )

    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Text input question",
    )

    parser.add_argument(
        "--audio",
        type=str,
        default=None,
        help="Audio input file path",
    )

    parser.add_argument(
        "--session_id",
        type=str,
        default="default",
        help="Conversation session id",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="audio/reply.wav",
        help="TTS output audio path",
    )

    parser.add_argument(
        "--asr_model",
        type=str,
        default="small",
        help="Whisper ASR model size: tiny, base, small",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.text and not args.audio:
        print("请提供 --text 或 --audio")
        print('示例：python main.py --text "E03 报警是什么意思？"')
        print("示例：python main.py --audio audio/e03_test.m4a")
        return

    if args.audio:
        audio_path = Path(args.audio)

        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在：{audio_path}")

        print("正在进行 ASR 语音识别...")
        asr = WhisperASR(model_size=args.asr_model)
        user_text = asr.transcribe(str(audio_path)).strip()
    else:
        user_text = args.text.strip()

    print("\n用户输入：")
    print(user_text)

    print("\n正在加载 Pipeline 和 Agent...")
    pipeline = EdgeTalkPipeline()
    agent = AgentCore(pipeline=pipeline)

    print("\n正在执行 Agent + RAG + LLM + Memory...")
    result = agent.run(
        user_text=user_text,
        session_id=args.session_id,
    )

    answer = result.get("answer", "")

    print("\n工具调用：")
    print(result.get("tool_used"))

    print("\n助手回答：")
    print(answer)

    print("\n正在生成 TTS 语音...")
    tts = WindowsTTS()
    tts.synthesize(
        text=answer,
        output_audio=args.output,
    )

    print("\n完整链路执行完成")
    print(f"session_id: {args.session_id}")
    print(f"TTS 输出文件: {args.output}")


if __name__ == "__main__":
    main()
