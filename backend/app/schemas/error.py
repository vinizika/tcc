from pydantic import BaseModel


class ErrorResponse(BaseModel):

    success: bool

    error: str

    message: str

    # Quando o erro é do atendente (rodada 26 do João): "attendant_unavailable"
    # ou "quota_exhausted", e o provedor, o modelo e o motivo.
    code: str | None = None

    details: dict | None = None
