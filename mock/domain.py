"""Modelos de domínio do protótipo de encaminhamento simulado."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Classification(str, Enum):
    EMERGENCY = "Emergência"
    NON_EMERGENCY = "Não emergência"
    UNCERTAIN = "Incerto"


class CaseStatus(str, Enum):
    NEW = "Novo"
    ACKNOWLEDGED = "Reconhecido"
    ON_THE_WAY = "Tutor a caminho"
    IN_CARE = "Em atendimento"
    COMPLETED = "Concluído"
    CANCELLED = "Cancelado"


class MessageAuthor(str, Enum):
    AI = "IA de pré-triagem"
    TUTOR = "Tutor"
    CLINIC = "Clínica"
    SYSTEM = "Sistema demonstrativo"


@dataclass(frozen=True)
class Clinic:
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    eta_minutes: int
    open_24h: bool
    phone: str
    rating: float
    review_count: int
    services: tuple[str, ...]
    availability: str
    last_updated: datetime
    opening_hours: str
    notes: str


@dataclass(frozen=True)
class Tutor:
    name: str
    phone: str


@dataclass(frozen=True)
class Pet:
    name: str
    species: str
    breed: str
    age: str
    weight: str
    relevant_history: tuple[str, ...]


@dataclass(frozen=True)
class TriageAnswer:
    question: str
    answer: str


@dataclass(frozen=True)
class Triage:
    original_report: str
    answers: tuple[TriageAnswer, ...]
    classification: Classification
    signs: tuple[str, ...]
    rationale: str
    guidance: tuple[str, ...]
    caveats: tuple[str, ...]


@dataclass(frozen=True)
class Message:
    id: str
    author_type: MessageAuthor
    author_name: str
    content: str
    created_at: datetime


@dataclass(frozen=True)
class CaseEvent:
    id: str
    event_type: str
    description: str
    created_at: datetime


@dataclass
class Case:
    id: str
    clinic_id: str
    tutor: Tutor
    pet: Pet
    triage: Triage
    created_at: datetime
    expected_arrival: datetime
    status: CaseStatus = CaseStatus.NEW
    messages: list[Message] = field(default_factory=list)
    events: list[CaseEvent] = field(default_factory=list)
