"""
Transcrição de áudio (trilho B1).

O arquivo enviado pelo tutor é entrada não confiável: o nome vem do cliente e
o tamanho, sem limite, fica à mercê dele. Por isso a rota grava sempre com um
nome gerado no servidor, dentro de `uploads/`, com teto de bytes, e apaga o
arquivo depois — em sucesso ou erro (evidencias/backlog.md#b-32).
"""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.core.logger import setup_logger
from app.exceptions.voice_exception import (
    AudioTooLargeException,
    EmptyAudioException,
    UnsupportedAudioException,
)
from app.schemas.voice import VoiceResponse
from app.services.voice_service import VoiceService


logger = setup_logger("VoiceAPI")

router = APIRouter(
    prefix="/voice",
    tags=["Voice"]
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Tamanho de cada bloco lido do upload ao gravar em disco.
CHUNK_SIZE = 1024 * 1024

# Extensões de áudio aceitas. O faster-whisper decodifica via PyAV/ffmpeg,
# que abre todos estes formatos.
ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".ogg",
    ".oga",
    ".opus",
    ".mp3",
    ".m4a",
    ".mp4",
    ".aac",
    ".webm",
    ".flac",
}

# Quando o nome do cliente não traz extensão útil, o tipo declarado no upload
# decide a extensão do arquivo gerado pelo servidor.
CONTENT_TYPE_TO_EXTENSION = {
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/wave": ".wav",
    "audio/vnd.wave": ".wav",
    "audio/ogg": ".ogg",
    "audio/opus": ".opus",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/aac": ".aac",
    "audio/webm": ".webm",
    "audio/flac": ".flac",
    "audio/x-flac": ".flac",
}


def _resolve_extension(audio: UploadFile) -> str:
    """
    Decide a extensão do arquivo temporário — nunca o nome do cliente.

    Só `Path(...).suffix` é lido do nome enviado, e `suffix` de um caminho
    com componentes de diretório é inofensivo (`Path("../x").suffix == ""`).
    """

    suffix = Path(audio.filename or "").suffix.lower()

    if suffix in ALLOWED_AUDIO_EXTENSIONS:
        return suffix

    mapped = CONTENT_TYPE_TO_EXTENSION.get((audio.content_type or "").lower())

    if mapped:
        return mapped

    raise UnsupportedAudioException(
        "Formato de áudio não suportado. Envie um arquivo "
        + ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
        + "."
    )


def _save_within_limit(
    audio: UploadFile,
    destination: Path,
    max_bytes: int,
) -> None:
    """
    Grava o upload em `destination` em blocos, abortando se passar do teto.

    Interromper durante a escrita pode deixar um arquivo parcial; quem chama
    é responsável por removê-lo no `finally`.
    """

    size = 0

    with open(destination, "wb") as buffer:

        while chunk := audio.file.read(CHUNK_SIZE):

            size += len(chunk)

            if size > max_bytes:
                raise AudioTooLargeException(
                    "Áudio acima do limite de "
                    f"{max_bytes // (1024 * 1024)} MB."
                )

            buffer.write(chunk)

    if size == 0:
        raise EmptyAudioException("O arquivo de áudio está vazio.")


@router.post(
    "/",
    response_model=VoiceResponse
)
def transcribe_audio(
    audio: UploadFile = File(...)
):

    extension = _resolve_extension(audio)
    max_bytes = settings.MAX_AUDIO_UPLOAD_MB * 1024 * 1024

    destination = UPLOAD_FOLDER / f"{uuid4().hex}{extension}"

    try:

        _save_within_limit(audio, destination, max_bytes)

        text, language, duration = VoiceService.transcribe(destination)

    finally:

        destination.unlink(missing_ok=True)

    return VoiceResponse(
        transcription=text,
        language=language,
        duration=duration,
    )
