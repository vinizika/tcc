"""
Transcrição de voz — a única implementação de Whisper do projeto.

Antes existiam três (`VoiceService`, `app/ai/whisper/`, `WhisperClient`), com
dois tamanhos de modelo e sem ninguém saber qual caminho rodava. As outras
duas eram órfãs e foram removidas (evidencias/backlog.md#b-13).

O modelo é carregado uma vez, na primeira transcrição, e reaproveitado. O
tamanho vem das settings para ficar registrado junto de qualquer medição de
qualidade.
"""

from pathlib import Path

from faster_whisper import WhisperModel

from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger("VoiceService")


class VoiceService:

    _model: WhisperModel | None = None

    @classmethod
    def load_model(cls) -> None:

        if cls._model is None:

            logger.info(
                f"Carregando Faster Whisper ({settings.WHISPER_MODEL_SIZE})..."
            )

            cls._model = WhisperModel(
                settings.WHISPER_MODEL_SIZE,
                device="cpu",
                compute_type="int8",
            )

    @classmethod
    def transcribe(cls, file_path: Path) -> tuple[str, str, float]:

        cls.load_model()

        logger.info(f"Iniciando transcrição: {file_path.name}")

        segments, info = cls._model.transcribe(
            str(file_path),
            language="pt",
            beam_size=5,
        )

        text = " ".join(segment.text.strip() for segment in segments)

        logger.info(
            f"Idioma: {info.language} "
            f"(prob. {info.language_probability:.2f}) · "
            f"duração {info.duration:.2f}s"
        )

        return text.strip(), info.language, info.duration
