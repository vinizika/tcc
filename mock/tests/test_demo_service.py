from dataclasses import fields
from datetime import datetime, timedelta

import pytest

from mock.demo_data import (
    CLINICS,
    DEFAULT_REPORT,
    DEMO_PET,
    DEMO_TIMEZONE,
    DEMO_TUTOR,
    EMERGENCY_GUIDANCE,
    REQUIRED_CLINIC_FIELDS,
    TRIAGE_CAVEATS,
)
from mock.demo_service import (
    ClinicOwnershipError,
    ConsentRequiredError,
    create_referral,
    dashboard_metrics,
    filter_cases,
    filter_clinics,
    find_case,
    initial_case_store,
    new_demo_state,
    send_message,
    update_status,
)
from mock.domain import (
    CaseStatus,
    Classification,
    Message,
    MessageAuthor,
    Triage,
    TriageAnswer,
)


NOW = datetime(2026, 9, 14, 15, 0, tzinfo=DEMO_TIMEZONE)


def triage(classification=Classification.EMERGENCY):
    return Triage(
        original_report=DEFAULT_REPORT,
        answers=(
            TriageAnswer(
                question="Está ofegante ou respirando com dificuldade?",
                answer="Sim",
            ),
        ),
        classification=classification,
        signs=("Respiração acelerada", "Cansaço", "Recusa alimentar"),
        rationale="Sinais respiratórios justificam avaliação imediata.",
        guidance=EMERGENCY_GUIDANCE,
        caveats=TRIAGE_CAVEATS,
    )


def conversation():
    return [
        Message(
            id="message-1",
            author_type=MessageAuthor.TUTOR,
            author_name=DEMO_TUTOR.name,
            content=DEFAULT_REPORT,
            created_at=NOW - timedelta(minutes=1),
        )
    ]


def referral(store, clinic_id=None, classification=Classification.EMERGENCY):
    return create_referral(
        store,
        clinic_id=clinic_id or CLINICS[0].id,
        tutor=DEMO_TUTOR,
        pet=DEMO_PET,
        triage=triage(classification),
        conversation=conversation(),
        consent=True,
        now=NOW,
    )


def test_selected_clinic_receives_case_and_other_clinics_do_not():
    store = initial_case_store()
    case = referral(store, CLINICS[1].id)

    assert store[CLINICS[1].id] == [case]
    assert store[CLINICS[0].id] == []
    assert store[CLINICS[2].id] == []


def test_referral_requires_consent():
    with pytest.raises(ConsentRequiredError):
        create_referral(
            initial_case_store(),
            clinic_id=CLINICS[0].id,
            tutor=DEMO_TUTOR,
            pet=DEMO_PET,
            triage=triage(),
            conversation=conversation(),
            consent=False,
            now=NOW,
        )


def test_case_receives_unique_id_and_correct_arrival_prediction():
    store = initial_case_store()
    first = referral(store)
    second = referral(store)

    assert first.id.startswith("DEMO-")
    assert first.id != second.id
    assert first.expected_arrival == NOW + timedelta(minutes=CLINICS[0].eta_minutes)


def test_status_update_records_event_and_updates_metrics():
    store = initial_case_store()
    case = referral(store)
    changed = update_status(
        store,
        clinic_id=case.clinic_id,
        case_id=case.id,
        status=CaseStatus.ACKNOWLEDGED,
        now=NOW + timedelta(minutes=4),
    )

    assert changed.status == CaseStatus.ACKNOWLEDGED
    assert changed.events[-1].created_at == NOW + timedelta(minutes=4)
    assert dashboard_metrics(store[case.clinic_id]) == {
        "waiting": 0,
        "emergencies": 1,
        "acknowledged": 1,
        "on_the_way": 0,
        "completed": 0,
        "average_recognition_minutes": 4.0,
    }


def test_filters_and_sorting():
    available_24h = filter_clinics(
        CLINICS, open_24h_only=True, available_only=True, sort_by="eta"
    )
    assert [clinic.id for clinic in available_24h] == [CLINICS[0].id]
    assert filter_clinics(CLINICS, query="nome que não existe") == []

    store = initial_case_store()
    emergency = referral(store)
    non_emergency = referral(store, classification=Classification.NON_EMERGENCY)
    update_status(
        store,
        clinic_id=emergency.clinic_id,
        case_id=emergency.id,
        status=CaseStatus.IN_CARE,
        now=NOW,
    )
    filtered = filter_cases(
        store[emergency.clinic_id],
        classification=Classification.EMERGENCY,
        status=CaseStatus.IN_CARE,
    )
    assert filtered == [emergency]
    assert non_emergency not in filtered


def test_messages_are_added_to_correct_case_without_ai_response():
    store = initial_case_store()
    first = referral(store)
    second = referral(store)
    original_second_count = len(second.messages)

    message = send_message(
        store,
        clinic_id=first.clinic_id,
        case_id=first.id,
        author_type=MessageAuthor.CLINIC,
        author_name=CLINICS[0].name,
        content="Estamos aguardando vocês.",
        now=NOW,
    )

    assert first.messages[-1] == message
    assert message.author_type == MessageAuthor.CLINIC
    assert len(second.messages) == original_second_count


def test_clinic_cannot_read_update_or_message_another_clinics_case():
    store = initial_case_store()
    case = referral(store, CLINICS[0].id)

    with pytest.raises(ClinicOwnershipError):
        find_case(store, CLINICS[1].id, case.id)
    with pytest.raises(ClinicOwnershipError):
        update_status(
            store,
            clinic_id=CLINICS[1].id,
            case_id=case.id,
            status=CaseStatus.CANCELLED,
            now=NOW,
        )
    with pytest.raises(ClinicOwnershipError):
        send_message(
            store,
            clinic_id=CLINICS[1].id,
            case_id=case.id,
            author_type=MessageAuthor.CLINIC,
            author_name=CLINICS[1].name,
            content="Mensagem indevida",
            now=NOW,
        )


def test_new_demo_state_resets_all_mutable_data():
    state = new_demo_state()
    referral(state["cases_by_clinic"])
    reset = new_demo_state()

    assert reset["flow_stage"] == "report"
    assert reset["selected_clinic_id"] is None
    assert all(not cases for cases in reset["cases_by_clinic"].values())


def test_simulated_clinics_have_all_required_fields():
    field_names = {field.name for field in fields(CLINICS[0])}
    assert set(REQUIRED_CLINIC_FIELDS) <= field_names
    assert len({clinic.id for clinic in CLINICS}) == len(CLINICS)
    assert all(clinic.phone.startswith("(11) 90000-") for clinic in CLINICS)
    assert all(clinic.last_updated.tzinfo is not None for clinic in CLINICS)
