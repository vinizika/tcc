from pydantic import BaseModel


class VoiceResponse(BaseModel):

    transcription: str