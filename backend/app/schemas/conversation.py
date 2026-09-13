from typing import Optional

from pydantic import BaseModel

from app.schemas.triage_output import TriageResult


class ConversationMessage(BaseModel):

    role: str  # "tutor" ou "assistente"
    content: str
    timestamp: str

    # Só o turno do assistente carrega a triagem estruturada.
    triage: Optional[TriageResult] = None


class ConversationResponse(BaseModel):

    id: str
    tutor_id: Optional[str] = None
    pet_id: Optional[str] = None
    created_at: str
    updated_at: str
    messages: list[ConversationMessage]
