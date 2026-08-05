from pathlib import Path

from app.models.whisper_model import whisper_model
from app.core.logger import setup_logger

logger = setup_logger("WhisperClient")


class WhisperClient:

    @staticmethod
    def transcribe(audio_path: Path):

        logger.info("Iniciando transcrição")

        segments, info = whisper_model.transcribe(
            str(audio_path),
            language="pt"
        )

        text = " ".join(
            segment.text
            for segment in segments
        )

        logger.info("Transcrição concluída")

        return text.strip()