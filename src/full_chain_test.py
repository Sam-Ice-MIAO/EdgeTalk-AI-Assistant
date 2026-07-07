import argparse
from pathlib import Path

from src.asr.whisper_asr import WhisperASR
from src.pipeline import EdgeTalkPipeline
from src.agent.agent_core import AgentCore
from src.tts.windows_tts import WindowsTTS


def main():
    parser = argparse.ArgumentParser(description="EdgeTalk full chain test")

    parser.add_argument("--text", type=str, default=None)
    parser.add_argument("--audio", type=str, default=None)
    parser.add_argument("--session_id", type=str, default="full_chain_test")
    parser.add_argument("--output", type=str, default="audio/full_chain_reply.wav")
    parser.add_argument("--asr_model", type=str, default="small")

    args = parser.parse_args()

    if not args.text and not args.audio:
        raise ValueError("请提供 --text 或 --audio")

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
    output_path = args.output
    tts = WindowsTTS()
    tts.synthesize(
        text=answer,
        output_audio=output_path,
    )

    print("\n完整链路测试完成")
    print(f"session_id: {args.session_id}")
    print(f"TTS 输出文件: {output_path}")


if __name__ == "__main__":
    main()
