from pathlib import Path

from faster_whisper import WhisperModel

from app.core.logger import setup_logger

logger = setup_logger("VoiceService")


class VoiceService:

    _model = None

    @classmethod
    def load_model(cls):

        if cls._model is None:

            logger.info("Carregando Faster Whisper...")

            cls._model = WhisperModel(
                "small",
                device="cpu",
                compute_type="int8"
            )

    @classmethod
    def transcribe(cls, file_path: Path):

        cls.load_model()

        logger.info(f"Iniciando transcrição: {file_path.name}")

        segments, info = cls._model.transcribe(
            str(file_path),
            language="pt",
            beam_size=5
        )

        text = ""

        for segment in segments:
            text += segment.text + " "

        logger.info(f"Idioma: {info.language}")
        logger.info(f"Confiança: {info.language_probability}")
        logger.info(f"Duração: {info.duration:.2f}s")

        logger.info("Transcrição finalizada")

        return (
            text.strip(),
            info.language,
            info.duration
        )