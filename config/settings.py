# config/settings.py

ASR_MODEL_SIZE = "tiny"

AUDIO_INPUT_PATH = "audio/test.m4a"
AUDIO_OUTPUT_PATH = "audio/reply.wav"

LLM_MODEL_PATH = "models/qwen1.5b.gguf"

LLM_N_CTX = 2048
LLM_N_THREADS = 6
LLM_MAX_TOKENS = 120
LLM_TEMPERATURE = 0.4
