from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.triage_output import Classificacao


ReferralStatus = Literal[
    "delivered", "viewed", "acknowledged", "accepted", "refused",
    "on_the_way", "arrived", "completed", "cancelled",
]


class PetSnapshot(BaseModel):
    id: Optional[str] = None
    name: str = Field(min_length=1, max_length=100)
    species: Literal["cao", "gato"]
    age: Optional[str] = Field(default=None, max_length=100)
    weight_kg: Optional[float] = Field(default=None, gt=0, le=150)
    breed: Optional[str] = Field(default=None, max_length=100)
    relevant_history: Optional[str] = Field(default=None, max_length=1000)
    # Rodada 24 do Ryu: a clínica recebe o que o tutor cadastrou.
    sex: Optional[Literal["macho", "femea"]] = None
    neutered: Optional[bool] = None
    reproductive_status: Optional[Literal["prenhe", "amamentando"]] = None


class ContactSnapshot(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=200)


class TriageSnapshotV1(BaseModel):
    schema_version: Literal["triage_snapshot.v1"] = "triage_snapshot.v1"
    original_report: str = Field(min_length=1, max_length=4000)
    classification: Classificacao
    justification: str = Field(min_length=1, max_length=4000)
    warning_signs: list[str] = Field(default_factory=list, max_length=8)
    recommendation: str = Field(min_length=1, max_length=2000)
    automatic: Literal[True] = True


class ReferralCreate(BaseModel):
    clinic_id: str
    idempotency_key: str = Field(min_length=8, max_length=100)
    pet: Optional[PetSnapshot] = None
    conversation_id: Optional[str] = None
    share_full_conversation: bool = False
    contact: ContactSnapshot = ContactSnapshot()
    triage: TriageSnapshotV1
    reviewed_summary: str = Field(min_length=1, max_length=5000)
    consent_to_share: bool

    @model_validator(mode="after")
    def consent_required(self):
        if not self.consent_to_share:
            raise ValueError("O encaminhamento exige consentimento explícito.")
        return self


class ReferralEvent(BaseModel):
    type: str
    description: str
    actor_type: Literal["system", "tutor", "clinic"]
    actor_id: Optional[str] = None
    created_at: str


class ReferralMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class ReferralMessage(BaseModel):
    id: str
    author_type: Literal["tutor", "clinic"]
    author_id: str
    author_name: str
    content: str
    created_at: str


class ReferralResponse(BaseModel):
    id: str
    tutor_id: str
    clinic_id: str
    clinic_name: str
    status: ReferralStatus
    pet: Optional[PetSnapshot] = None
    conversation_id: Optional[str] = None
    share_full_conversation: bool = False
    shared_conversation: list[dict] = Field(default_factory=list)
    location: Optional[dict] = None
    contact: ContactSnapshot
    triage: TriageSnapshotV1
    reviewed_summary: str
    consented_at: str
    created_at: str
    updated_at: str
    events: list[ReferralEvent]
    messages: list[ReferralMessage]
    chat_closed_at: Optional[str] = None

    @model_validator(mode="after")
    def only_current_location(self):
        from datetime import datetime, timezone
        if self.location:
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(self.location["updated_at"])).total_seconds()
                if age > 120 or age < -30 or self.status != "on_the_way":
                    self.location = None
            except (KeyError, ValueError, TypeError):
                self.location = None
        return self


class StatusTransitionRequest(BaseModel):
    action: Literal["acknowledge", "accept", "refuse", "confirm_on_the_way", "arrived", "complete", "cancel"]
    reason: Optional[str] = Field(default=None, max_length=500)


class DashboardMetrics(BaseModel):
    confirmed_on_the_way: int
    awaiting_review: int
    arrived_last_24h: int
    total_received: int
    definitions: dict[str, str]


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    referrals: list[ReferralResponse]
    polling_interval_s: int
    has_more: bool = False
