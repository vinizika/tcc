"""
O atendente (o modelo que classifica a urgência) não respondeu.

A regra do sistema é nunca trocar de modelo em silêncio (rodada 26 do João):
se o provedor escolhido falha e a troca não foi permitida pela configuração,
a requisição falha com 503 e diz qual provedor, qual modelo e por quê. O
código do erro separa as duas situações que pedem ação diferente de quem
opera o sistema.
"""

from app.exceptions.base_exception import BaseAppException


class AttendantUnavailableException(BaseAppException):

    code = "attendant_unavailable"

    def __init__(self, message: str, *, provider: str, model: str, reason: str = ""):
        super().__init__(message, status_code=503)
        self.details = {"provider": provider, "model": model, "reason": reason}


class QuotaExhaustedException(AttendantUnavailableException):
    """A cota do dia do provedor acabou: esperar a virada ou trocar de conta."""

    code = "quota_exhausted"
