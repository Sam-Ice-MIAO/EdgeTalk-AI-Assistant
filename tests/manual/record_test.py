from src.audio.recorder import record_audio , list_audio_devices

print("当前音频设备：")
list_audio_devices()
audio_path=record_audio("audio/record.wav", duration=8)
if audio_path:
    print("录音测试成功:", audio_path)
else:
    print("录音测试失败，当前环境暂时使用固定音频文件输入。")
