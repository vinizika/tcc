from app.ai.whisper.model import model


class WhisperTranscriber:

    @staticmethod
    def transcribe(audio_path: str):

        segments, _ = model.transcribe(audio_path)

        text = ""

        for segment in segments:
            text += segment.text + " "

        return text.strip()