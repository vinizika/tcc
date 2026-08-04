from pydantic import BaseModel


class ErrorResponse(BaseModel):

    success: bool

    error: str

    message: str