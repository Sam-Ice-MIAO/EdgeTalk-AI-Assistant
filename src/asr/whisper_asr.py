from faster_whisper import WhisperModel


class WhisperASR:
    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path: str) -> str:
        segments, info = self.model.transcribe(
            audio_path,
            language="zh"
        )

        texts = []
        for segment in segments:
            texts.append(segment.text.strip())

        result = " ".join(texts).strip()

        print("检测语言:", info.language)
        print("ASR识别结果:", result)

        return result
