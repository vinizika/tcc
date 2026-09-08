from app.exceptions.base_exception import BaseAppException


class UnsupportedAudioException(BaseAppException):
    """
    Upload que não aparenta ser um áudio de formato suportado.

    Recusar antes de gravar em disco: um arquivo que não é áudio só ocuparia
    espaço até a transcrição falhar.
    """

    def __init__(self, message: str):

        super().__init__(message, status_code=415)


class AudioTooLargeException(BaseAppException):
    """
    Upload acima do teto de `MAX_AUDIO_UPLOAD_MB`.

    O relato de um tutor é curto; um arquivo grande é engano ou abuso, e
    aceitá-lo deixaria o disco do backend à mercê do cliente.
    """

    def __init__(self, message: str):

        super().__init__(message, status_code=413)


class EmptyAudioException(BaseAppException):
    """Upload sem conteúdo: não há o que transcrever."""

    def __init__(self, message: str):

        super().__init__(message, status_code=422)
