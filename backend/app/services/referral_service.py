from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException

from app.repositories.workflow_repository import get_workflow_repository
from app.schemas.auth import Principal
from app.schemas.referral import ReferralCreate, ReferralEvent, ReferralResponse, StatusTransitionRequest
from app.core.config import settings


TRANSITIONS = {
    "acknowledge": ({"delivered", "viewed"}, "acknowledged"),
    "accept": ({"viewed", "acknowledged"}, "accepted"),
    "refuse": ({"delivered", "viewed", "acknowledged"}, "refused"),
    "confirm_on_the_way": ({"accepted"}, "on_the_way"),
    "arrived": ({"accepted", "on_the_way"}, "arrived"),
    "complete": ({"arrived"}, "completed"),
    "cancel": ({"delivered", "viewed", "acknowledged", "accepted", "on_the_way"}, "cancelled"),
}

ACTION_ACTOR = {
    "acknowledge": "clinic", "accept": "clinic", "refuse": "clinic",
    "arrived": "clinic", "complete": "clinic", "confirm_on_the_way": "tutor",
    "cancel": "either",
}

DESCRIPTIONS = {
    "acknowledge": "A clínica confirmou o recebimento do encaminhamento.",
    "accept": "A clínica aceitou analisar/receber o caso; isso não garante vaga nem atendimento imediato.",
    "refuse": "A clínica recusou o encaminhamento.",
    "confirm_on_the_way": "O tutor confirmou que está a caminho.",
    "arrived": "A clínica registrou a chegada física do paciente.",
    "complete": "A clínica marcou o caso como concluído.",
    "cancel": "O encaminhamento foi cancelado.",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ReferralService:
    @staticmethod
    def create(data: ReferralCreate, principal: Principal) -> tuple[ReferralResponse, bool]:
        if settings.WORKFLOW_MODE != "demo" and not data.conversation_id:
            raise HTTPException(422, "O envio deve usar uma conversa persistida da pré-triagem.")
        repository = get_workflow_repository()
        clinic = repository.get_clinic(data.clinic_id)
        if not clinic or not clinic.get("participant") or not clinic.get("verified") or not clinic.get("enabled"):
            raise HTTPException(409, "A clínica não participa ou não está habilitada para encaminhamento digital.")
        if bool(principal.demo) != (clinic.get("source") == "demo"):
            raise HTTPException(403, "Contas acadêmicas só compartilham com a clínica acadêmica; contas próprias usam unidades verificadas.")
        shared_conversation = []
        if data.conversation_id:
            from app.services.workspace_service import WorkspaceService
            conversation = WorkspaceService.get(principal, data.conversation_id)
            responses = [m for m in conversation["messages"] if m.get("triage")]
            if not responses or conversation["status"] != "idle":
                raise HTTPException(409, "Aguarde uma resposta de pré-triagem antes de compartilhar.")
            # Automatic content comes from the stored answer, never a client claim.
            latest = responses[-1]["triage"]
            data.triage.classification = latest["classificacao"]
            data.triage.justification = latest["justificativa"]
            data.triage.warning_signs = latest.get("sinais_de_alerta", [])
            data.triage.recommendation = latest["recomendacao"]
            data.triage.original_report = next(m["content"] for m in conversation["messages"] if m["role"] == "tutor")
            if data.share_full_conversation:
                shared_conversation = [{k: m[k] for k in ("id", "role", "content", "created_at", "triage", "answer_to", "origin", "selected_option") if k in m}
                                       for m in conversation["messages"]]
        elif data.share_full_conversation:
            raise HTTPException(422, "Selecione a conversa que deseja compartilhar.")
        timestamp = now_iso(); referral_id = str(uuid4())
        document = {
            "id": referral_id, "idempotency_key": data.idempotency_key,
            "tutor_id": principal.user_id, "clinic_id": clinic["id"], "clinic_name": clinic["name"],
            "status": "delivered", "pet": data.pet.model_dump() if data.pet else None, "contact": data.contact.model_dump(),
            "conversation_id": data.conversation_id, "share_full_conversation": data.share_full_conversation,
            "shared_conversation": shared_conversation, "location": None,
            "triage": data.triage.model_dump(), "reviewed_summary": data.reviewed_summary,
            "consented_at": timestamp, "created_at": timestamp, "updated_at": timestamp,
            "events": [
                {"type": "submitted", "description": "Encaminhamento gravado no sistema após consentimento do tutor.", "actor_type": "tutor", "actor_id": principal.user_id, "created_at": timestamp},
                {"type": "delivered", "description": "Encaminhamento disponibilizado no painel da clínica.", "actor_type": "system", "actor_id": None, "created_at": timestamp},
            ],
            "messages": [], "chat_closed_at": None,
        }
        saved, created = repository.save_referral(document, data.idempotency_key)
        return ReferralResponse(**saved), created

    @staticmethod
    def _authorize(document: dict, principal: Principal) -> None:
        if principal.role == "tutor" and document["tutor_id"] != principal.user_id:
            raise HTTPException(404, "Encaminhamento não encontrado.")
        if principal.role == "clinic" and document["clinic_id"] != principal.clinic_id:
            raise HTTPException(404, "Encaminhamento não encontrado.")
        if principal.role == "clinic" and not principal.clinic_verified:
            raise HTTPException(403, "A clínica ainda não foi verificada.")

    @staticmethod
    def get(referral_id: str, principal: Principal, mark_viewed: bool = True) -> ReferralResponse:
        repository = get_workflow_repository(); document = repository.get_referral(referral_id)
        if not document: raise HTTPException(404, "Encaminhamento não encontrado.")
        ReferralService._authorize(document, principal)
        if mark_viewed and principal.role == "clinic" and document["status"] == "delivered":
            timestamp = now_iso(); document["status"] = "viewed"; document["updated_at"] = timestamp
            document["events"].append({"type": "viewed", "description": "A clínica visualizou o encaminhamento.", "actor_type": "clinic", "actor_id": principal.user_id, "created_at": timestamp})
            repository.replace_referral(document)
        return ReferralResponse(**document)

    @staticmethod
    def list_for(principal: Principal) -> list[ReferralResponse]:
        if principal.role == "clinic" and (not principal.clinic_verified or not principal.clinic_id):
            raise HTTPException(403, "O cadastro da clínica ainda não foi verificado.")
        query = {"tutor_id": principal.user_id} if principal.role == "tutor" else {"clinic_id": principal.clinic_id}
        documents = get_workflow_repository().list_referrals(query)
        return [ReferralResponse(**item) for item in documents]

    @staticmethod
    def transition(referral_id: str, request: StatusTransitionRequest, principal: Principal) -> ReferralResponse:
        repository = get_workflow_repository(); document = repository.get_referral(referral_id)
        if not document: raise HTTPException(404, "Encaminhamento não encontrado.")
        ReferralService._authorize(document, principal)
        allowed_actor = ACTION_ACTOR[request.action]
        if allowed_actor != "either" and principal.role != allowed_actor:
            raise HTTPException(403, "Seu perfil não pode executar esta transição.")
        allowed_from, target = TRANSITIONS[request.action]
        if document["status"] not in allowed_from:
            raise HTTPException(409, f"Transição inválida: {document['status']} → {target}.")
        timestamp = now_iso(); document["status"] = target; document["updated_at"] = timestamp
        if target in {"refused", "cancelled", "arrived", "completed"}:
            document["location"] = None
        description = DESCRIPTIONS[request.action]
        if request.reason: description += f" Motivo informado: {request.reason}"
        document["events"].append({"type": target, "description": description, "actor_type": principal.role, "actor_id": principal.user_id, "created_at": timestamp})
        return ReferralResponse(**repository.replace_referral(document))
