from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from app.schemas.voice import VoiceResponse
from app.services.voice_service import VoiceService

router = APIRouter(
    prefix="/voice",
    tags=["Voice"]
)


@router.post(
    "/",
    response_model=VoiceResponse
)
def transcribe_audio(
    audio: UploadFile = File(...)
):

    text = VoiceService.transcribe(audio)

    return VoiceResponse(
        transcription=text
    )