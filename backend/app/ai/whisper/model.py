from faster_whisper import WhisperModel

from app.core.logger import setup_logger

logger = setup_logger("WhisperModel")

logger.info("Carregando Faster-Whisper...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

logger.info("Modelo carregado.")