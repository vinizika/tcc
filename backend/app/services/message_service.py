from uuid import uuid4

from fastapi import HTTPException

from app.repositories.workflow_repository import get_workflow_repository
from app.schemas.auth import Principal
from app.schemas.referral import ReferralMessageCreate, ReferralResponse
from app.services.referral_service import ReferralService, now_iso


class MessageService:
    @staticmethod
    def send(referral_id: str, data: ReferralMessageCreate, principal: Principal) -> ReferralResponse:
        repository = get_workflow_repository(); document = repository.get_referral(referral_id)
        if not document: raise HTTPException(404, "Encaminhamento não encontrado.")
        ReferralService._authorize(document, principal)
        if document.get("chat_closed_at") or document["status"] in {"completed", "cancelled", "refused"}:
            raise HTTPException(409, "Esta conversa está encerrada.")
        timestamp = now_iso()
        document["messages"].append({"id": str(uuid4()), "author_type": principal.role, "author_id": principal.user_id, "author_name": principal.display_name, "content": data.content.strip(), "created_at": timestamp})
        document["updated_at"] = timestamp
        return ReferralResponse(**repository.replace_referral(document))

    @staticmethod
    def close(referral_id: str, principal: Principal) -> ReferralResponse:
        repository = get_workflow_repository(); document = repository.get_referral(referral_id)
        if not document: raise HTTPException(404, "Encaminhamento não encontrado.")
        ReferralService._authorize(document, principal)
        if not document.get("chat_closed_at"):
            timestamp = now_iso(); document["chat_closed_at"] = timestamp; document["updated_at"] = timestamp
            document["events"].append({"type": "chat_closed", "description": "A conversa foi encerrada.", "actor_type": principal.role, "actor_id": principal.user_id, "created_at": timestamp})
            repository.replace_referral(document)
        return ReferralResponse(**document)
