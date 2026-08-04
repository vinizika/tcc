from app.exceptions.base_exception import BaseAppException


class PipelineException(BaseAppException):

    def __init__(self, message: str):

        super().__init__(message, status_code=500)