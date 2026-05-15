from faster_whisper import WhisperModel
model=WhisperModel("tiny",device="cpu",compute_type="int8")
segments,info=model.transcribe("audio/test.m4a",language="zh")
print("检测语言：",info.language)
print("语言概率：",info.language_probability)
print("\n识别结果：")
for segment in segments:
	print(segment.text)
