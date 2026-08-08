from pathlib import Path

from app.ai.whisper.model import model
from app.core.logger import setup_logger

logger = setup_logger("WhisperTranscriber")


class WhisperTranscriber:

    @staticmethod
    def transcribe(audio_path: str) -> str:

        logger.info(f"Transcrevendo {audio_path}")

        segments, info = model.transcribe(
            audio_path,
            language="pt",
            task="transcribe",
            beam_size=5,
            vad_filter=True
        )

        text = ""

        for segment in segments:
            text += segment.text + " "

        logger.info("Transcrição concluída")

        return text.strip()