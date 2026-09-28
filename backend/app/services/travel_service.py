from datetime import datetime, timezone
from fastapi import HTTPException
from app.clients.maps_client import route_estimate
from app.repositories.workflow_repository import get_workflow_repository
from app.services.referral_service import ReferralService, now_iso
from app.schemas.referral import ReferralResponse


class TravelService:
    @staticmethod
    def update(referral_id, data, principal):
        repo = get_workflow_repository()
        doc = repo.get_referral(referral_id)
        if not doc:
            raise HTTPException(404, "Encaminhamento não encontrado.")
        ReferralService._authorize(doc, principal)
        if principal.role != "tutor":
            raise HTTPException(403, "Somente o tutor pode compartilhar a localização.")
        if not data.consent:
            doc["location"] = None
        else:
            if doc["status"] != "on_the_way":
                raise HTTPException(409, "Confirme que está a caminho antes de compartilhar sua posição.")
            if data.latitude is None or data.longitude is None:
                raise HTTPException(422, "A localização precisa de latitude e longitude.")
            previous = doc.get("location")
            if previous and (datetime.now(timezone.utc) - datetime.fromisoformat(previous["updated_at"])).total_seconds() < 20:
                return ReferralResponse(**doc)
            clinic = repo.get_clinic(doc["clinic_id"])
            estimate = None
            # Never compute a real route to the fictional academic clinic.
            if clinic and clinic.get("source") != "demo":
                try:
                    estimate = route_estimate(data.latitude, data.longitude, clinic)
                except HTTPException:
                    pass
            doc["location"] = {"latitude": data.latitude, "longitude": data.longitude,
                "accuracy_m": data.accuracy_m, "updated_at": now_iso(), "estimate": estimate,
                "consented_at": previous.get("consented_at", now_iso()) if previous else now_iso()}
        doc["updated_at"] = now_iso()
        return ReferralResponse(**repo.replace_referral(doc))
