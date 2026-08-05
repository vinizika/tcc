# app/models/whisper_model.py

from faster_whisper import WhisperModel

print("Carregando Faster Whisper...")

whisper_model = WhisperModel(
    model_size_or_path="base",
    device="cpu",
    compute_type="int8"
)

print("Whisper carregado.")