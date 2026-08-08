import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File

from app.schemas.voice import VoiceResponse
from app.services.voice_service import VoiceService


router = APIRouter(
    prefix="/voice",
    tags=["Voice"]
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@router.post(
    "/",
    response_model=VoiceResponse
)
def transcribe_audio(
    audio: UploadFile = File(...)
):

    file_path = UPLOAD_FOLDER / audio.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    text, language, duration = VoiceService.transcribe(file_path)

    return VoiceResponse(
        transcription=text,
        language=language,
        duration=duration
    )