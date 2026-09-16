"""Lógica pura e adaptadores simulados do fluxo tutor–clínica.

As funções públicas deste módulo formam a fronteira que poderá ser substituída
por chamadas de API no futuro. Hoje elas só leem ou alteram o estado recebido
em memória; não há rede, persistência, geolocalização ou comunicação externa.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Iterable
from uuid import uuid4

from mock.demo_data import CLINICS, DEMO_LOCATION
from mock.domain import (
    Case,
    CaseEvent,
    CaseStatus,
    Classification,
    Clinic,
    Message,
    MessageAuthor,
    Pet,
    Triage,
    Tutor,
)


class DemoError(ValueError):
    """Erro esperado de uma operação local do protótipo."""


class ConsentRequiredError(DemoError):
    pass


class ClinicOwnershipError(DemoError):
    pass


def get_location() -> dict[str, str | float]:
    """Futuro: obter localização autorizada do dispositivo do tutor."""
    return dict(DEMO_LOCATION)


def list_clinics() -> list[Clinic]:
    """Futuro: consultar clínicas verificadas e disponibilidade declarada."""
    return list(CLINICS)


def get_clinic(clinic_id: str) -> Clinic | None:
    """Futuro: consultar os detalhes verificáveis de uma clínica."""
    return next((clinic for clinic in CLINICS if clinic.id == clinic_id), None)


def initial_case_store() -> dict[str, list[Case]]:
    return {clinic.id: [] for clinic in CLINICS}


def new_demo_state() -> dict:
    """Estado novo usado tanto no primeiro carregamento quanto no reinício."""
    return {
        "cases_by_clinic": initial_case_store(),
        "selected_clinic_id": None,
        "selected_case_by_clinic": {},
        "referral_case_id": None,
        "flow_stage": "report",
        "triage_conversation": [],
    }


def create_referral(
    cases_by_clinic: dict[str, list[Case]],
    *,
    clinic_id: str,
    tutor: Tutor,
    pet: Pet,
    triage: Triage,
    conversation: Iterable[Message],
    consent: bool,
    now: datetime,
) -> Case:
    """Futuro: criar encaminhamento após consentimento explícito do tutor."""
    if not consent:
        raise ConsentRequiredError("O envio simulado exige consentimento explícito.")

    clinic = get_clinic(clinic_id)
    if clinic is None or clinic_id not in cases_by_clinic:
        raise DemoError("Clínica fictícia inválida.")

    case = Case(
        id=f"DEMO-{uuid4().hex[:8].upper()}",
        clinic_id=clinic_id,
        tutor=tutor,
        pet=pet,
        triage=triage,
        created_at=now,
        expected_arrival=now + timedelta(minutes=clinic.eta_minutes),
        messages=list(conversation),
        events=[
            CaseEvent(
                id=uuid4().hex,
                event_type="referral_created",
                description=(
                    "Encaminhamento criado somente nesta demonstração; nenhum dado "
                    "foi enviado a uma clínica real."
                ),
                created_at=now,
            )
        ],
    )
    cases_by_clinic[clinic_id].insert(0, case)
    return case


def list_clinic_cases(
    cases_by_clinic: dict[str, list[Case]], clinic_id: str
) -> list[Case]:
    """Futuro: listar casos autenticados pertencentes à clínica."""
    return list(cases_by_clinic.get(clinic_id, []))


def find_case(
    cases_by_clinic: dict[str, list[Case]], clinic_id: str, case_id: str
) -> Case:
    for case in cases_by_clinic.get(clinic_id, []):
        if case.id == case_id:
            return case
    raise ClinicOwnershipError("Caso inexistente ou pertencente a outra clínica.")


def update_status(
    cases_by_clinic: dict[str, list[Case]],
    *,
    clinic_id: str,
    case_id: str,
    status: CaseStatus,
    now: datetime,
) -> Case:
    """Futuro: atualizar status com autorização da clínica responsável."""
    case = find_case(cases_by_clinic, clinic_id, case_id)
    case.status = status
    case.events.append(
        CaseEvent(
            id=uuid4().hex,
            event_type="status_changed",
            description=f"Status atualizado para “{status.value}” pela clínica.",
            created_at=now,
        )
    )
    return case


def send_message(
    cases_by_clinic: dict[str, list[Case]],
    *,
    clinic_id: str,
    case_id: str,
    author_type: MessageAuthor,
    author_name: str,
    content: str,
    now: datetime,
) -> Message:
    """Futuro: enviar mensagem humana no canal do caso."""
    if author_type not in {MessageAuthor.TUTOR, MessageAuthor.CLINIC}:
        raise DemoError("Após o encaminhamento, somente tutor e clínica conversam.")
    content = content.strip()
    if not content:
        raise DemoError("A mensagem não pode estar vazia.")

    case = find_case(cases_by_clinic, clinic_id, case_id)
    message = Message(
        id=uuid4().hex,
        author_type=author_type,
        author_name=author_name,
        content=content,
        created_at=now,
    )
    case.messages.append(message)
    case.events.append(
        CaseEvent(
            id=uuid4().hex,
            event_type="message_sent",
            description=f"Mensagem manual enviada por {author_name}.",
            created_at=now,
        )
    )
    return message


def get_history(
    cases_by_clinic: dict[str, list[Case]], clinic_id: str, case_id: str
) -> list[Message]:
    """Futuro: obter histórico auditável da comunicação do caso."""
    return list(find_case(cases_by_clinic, clinic_id, case_id).messages)


def dashboard_metrics(cases: Iterable[Case]) -> dict[str, int | float]:
    cases = list(cases)
    acknowledged = {CaseStatus.ACKNOWLEDGED, CaseStatus.ON_THE_WAY, CaseStatus.IN_CARE}
    recognition_minutes = []
    for case in cases:
        event = next(
            (
                item
                for item in case.events
                if item.event_type == "status_changed"
                and "Reconhecido" in item.description
            ),
            None,
        )
        if event:
            recognition_minutes.append(
                max(0.0, (event.created_at - case.created_at).total_seconds() / 60)
            )

    return {
        "waiting": sum(case.status == CaseStatus.NEW for case in cases),
        "emergencies": sum(
            case.triage.classification == Classification.EMERGENCY
            and case.status not in {CaseStatus.COMPLETED, CaseStatus.CANCELLED}
            for case in cases
        ),
        "acknowledged": sum(case.status in acknowledged for case in cases),
        "on_the_way": sum(case.status == CaseStatus.ON_THE_WAY for case in cases),
        "completed": sum(case.status == CaseStatus.COMPLETED for case in cases),
        "average_recognition_minutes": round(
            sum(recognition_minutes) / len(recognition_minutes), 1
        )
        if recognition_minutes
        else 0.0,
    }


def filter_clinics(
    clinics: Iterable[Clinic],
    *,
    open_24h_only: bool = False,
    available_only: bool = False,
    sort_by: str = "distance",
    query: str = "",
) -> list[Clinic]:
    normalized_query = query.strip().casefold()
    result = [
        clinic
        for clinic in clinics
        if (not open_24h_only or clinic.open_24h)
        and (not available_only or clinic.availability.startswith("Equipe disponível"))
        and (
            not normalized_query
            or normalized_query
            in " ".join(
                (clinic.name, clinic.address, *clinic.services)
            ).casefold()
        )
    ]
    key = (lambda clinic: clinic.eta_minutes) if sort_by == "eta" else (
        lambda clinic: clinic.distance_km
    )
    return sorted(result, key=key)


def filter_cases(
    cases: Iterable[Case],
    *,
    classification: Classification | None = None,
    status: CaseStatus | None = None,
    newest_first: bool = True,
) -> list[Case]:
    result = [
        case
        for case in cases
        if (classification is None or case.triage.classification == classification)
        and (status is None or case.status == status)
    ]
    return sorted(result, key=lambda case: case.created_at, reverse=newest_first)


def clinic_payload(clinic: Clinic) -> dict:
    """Utilitário serializável para inspeção e testes dos campos simulados."""
    return asdict(clinic)
