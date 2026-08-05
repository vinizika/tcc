import shutil

from pathlib import Path

from fastapi import UploadFile

from app.ai.whisper.transcriber import WhisperTranscriber


class VoiceService:

    UPLOAD_FOLDER = Path("uploads")

    UPLOAD_FOLDER.mkdir(exist_ok=True)


    @staticmethod
    def transcribe(audio: UploadFile):

        file_path = VoiceService.UPLOAD_FOLDER / audio.filename

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(audio.file, buffer)

        text = WhisperTranscriber.transcribe(
            str(file_path)
        )

        file_path.unlink()

        return text