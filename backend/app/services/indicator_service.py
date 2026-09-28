from datetime import datetime, timedelta, timezone

from app.schemas.referral import DashboardMetrics, ReferralResponse


class IndicatorService:
    @staticmethod
    def calculate(referrals: list[ReferralResponse]) -> DashboardMetrics:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        arrived_recent = 0
        for referral in referrals:
            if any(event.type == "arrived" and datetime.fromisoformat(event.created_at) >= cutoff for event in referral.events):
                arrived_recent += 1
        return DashboardMetrics(
            confirmed_on_the_way=sum(item.status == "on_the_way" for item in referrals),
            awaiting_review=sum(item.status in {"delivered", "viewed", "acknowledged"} for item in referrals),
            arrived_last_24h=arrived_recent,
            total_received=len(referrals),
            definitions={
                "confirmed_on_the_way": "Casos em que o tutor confirmou que iniciou o deslocamento.",
                "awaiting_review": "Encaminhamentos entregues, visualizados ou reconhecidos, ainda sem aceite/recusa.",
                "arrived_last_24h": "Pacientes cuja chegada física foi registrada pela clínica nas últimas 24 horas.",
                "total_received": "Todos os encaminhamentos já destinados à unidade, em qualquer status.",
            },
        )
