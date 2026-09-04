from app.exceptions.base_exception import BaseAppException


class PipelineException(BaseAppException):

    def __init__(self, message: str):

        super().__init__(message, status_code=500)

class UnsupportedOptionException(BaseAppException):
    """
    Opcao pedida que ainda nao existe no pipeline.

    Falhar e melhor do que aceitar e ignorar: uma etapa ligada em silencio
    produziria uma linha de ablacao sem significado.
    """

    def __init__(self, message: str):

        super().__init__(message, status_code=400)
