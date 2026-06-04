from datetime import datetime
from pathlib import Path

from config.settings import (
    ASR_MODEL_SIZE,
    AUDIO_OUTPUT_PATH,
    LLM_MODEL_PATH,
)

from src.asr.whisper_asr import WhisperASR
from src.llm.local_llm import LocalLLM
from src.tts.windows_tts import WindowsTTS


class EdgeTalkPipeline:
    def __init__(self):
        self.asr = None
        self.llm = None
        self.tts = None

    def get_asr(self):
        if self.asr is None:
            print("正在加载 ASR 模型...")
            self.asr = WhisperASR(model_size=ASR_MODEL_SIZE)
            print("ASR 模型加载完成")
        return self.asr

    def get_llm(self):
        if self.llm is None:
            print("正在加载本地 LLM 模型...")
            self.llm = LocalLLM(model_path=LLM_MODEL_PATH)
            print("本地 LLM 模型加载完成")
        return self.llm

    def get_tts(self):
        if self.tts is None:
            self.tts = WindowsTTS()
        return self.tts

    def generate_reply(self, user_text: str, context=None) -> str:
        if not user_text.strip():
            return ""

        llm = self.get_llm()
        reply = llm.generate(user_text, context=context)

        return reply

    def run_audio_pipeline(self, audio_path: str, output_audio: str = None):
        audio_file = Path(audio_path)

        if not audio_file.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        asr = self.get_asr()
        llm = self.get_llm()
        tts = self.get_tts()

        user_text = asr.transcribe(str(audio_file))

        if not user_text:
            return {
                "user_text": "",
                "reply": "",
                "output_audio": None,
                "message": "ASR 没有识别到有效文本"
            }

        reply = llm.generate(user_text)

        if not reply:
            return {
                "user_text": user_text,
                "reply": "",
                "output_audio": None,
                "message": "LLM 没有生成有效回复"
            }

        if output_audio is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_audio = f"audio/reply_{timestamp}.wav"

        tts.synthesize(reply, output_audio)

        return {
            "user_text": user_text,
            "reply": reply,
            "output_audio": output_audio,
            "message": "success"
        }
