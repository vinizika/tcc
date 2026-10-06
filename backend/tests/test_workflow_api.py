"""Fluxos integrados e autorização da segunda etapa, sem serviços externos."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.repositories import workflow_repository


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "WORKFLOW_MODE", "demo")
    repository = workflow_repository.MemoryWorkflowRepository()
    monkeypatch.setattr(workflow_repository, "_mongo_repository", repository)
    return TestClient(app)


def auth(account: str) -> dict[str, str]:
    return {"Authorization": f"Bearer demo:{account}"}


def referral_payload(clinic_id="demo-clinic-a", key="idem-key-0001"):
    return {
        "clinic_id": clinic_id,
        "idempotency_key": key,
        "pet": {"name": "Thor", "species": "cao", "age": "6 anos"},
        "contact": {"name": "Ana", "phone": "(11) 90000-0000"},
        "triage": {
            "schema_version": "triage_snapshot.v1",
            "original_report": "Thor está ofegante e não consegue levantar.",
            "classification": "EMERGENCIA",
            "justification": "Há sinais relatados que pedem avaliação imediata.",
            "warning_signs": ["ofegância", "fraqueza"],
            "recommendation": "Procure atendimento.",
            "automatic": True,
        },
        "reviewed_summary": "Thor, cão, 6 anos. Ofegante e sem conseguir levantar.",
        "consent_to_share": True,
    }


def create_referral(client, **overrides):
    payload = referral_payload(**overrides)
    response = client.post("/referrals/", json=payload, headers=auth("tutor-a"))
    assert response.status_code == 201
    return response.json()


def test_demo_search_is_explicit_and_public_clinic_cannot_receive_referral(client):
    search = client.post("/clinics/search", json={"latitude": -23.56, "longitude": -46.65})
    assert search.status_code == 200
    assert search.json()["mode"] == "demo"
    public = next(item for item in search.json()["clinics"] if item["id"] == "demo-public-only")
    assert public["digital_referral_enabled"] is False

    denied = client.post(
        "/referrals/",
        json=referral_payload(clinic_id="demo-public-only"),
        headers=auth("tutor-a"),
    )
    assert denied.status_code == 409


def test_consent_is_required_and_repeated_submit_is_idempotent(client):
    payload = referral_payload()
    payload["consent_to_share"] = False
    assert client.post("/referrals/", json=payload, headers=auth("tutor-a")).status_code == 422

    first = client.post("/referrals/", json=referral_payload(), headers=auth("tutor-a"))
    second = client.post("/referrals/", json=referral_payload(), headers=auth("tutor-a"))
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.headers["X-Idempotent-Replay"] == "true"
    assert first.json()["id"] == second.json()["id"]


def test_tutor_and_clinic_are_isolated_by_resource(client):
    referral = create_referral(client)
    assert client.get(f"/referrals/{referral['id']}", headers=auth("tutor-b")).status_code == 404
    assert client.get(f"/referrals/{referral['id']}", headers=auth("clinic-b")).status_code == 404
    assert client.get("/referrals/dashboard", headers=auth("clinic-pending")).status_code == 403


def test_state_machine_dashboard_and_human_chat(client):
    referral = create_referral(client)
    referral_id = referral["id"]

    viewed = client.get(f"/referrals/{referral_id}", headers=auth("clinic-a"))
    assert viewed.json()["status"] == "viewed"

    accepted = client.post(
        f"/referrals/{referral_id}/status",
        json={"action": "accept"},
        headers=auth("clinic-a"),
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"

    invalid = client.post(
        f"/referrals/{referral_id}/status",
        json={"action": "complete"},
        headers=auth("clinic-a"),
    )
    assert invalid.status_code == 409

    on_way = client.post(
        f"/referrals/{referral_id}/status",
        json={"action": "confirm_on_the_way"},
        headers=auth("tutor-a"),
    )
    assert on_way.json()["status"] == "on_the_way"

    message = client.post(
        f"/referrals/{referral_id}/messages",
        json={"content": "Estamos saindo agora."},
        headers=auth("tutor-a"),
    )
    assert message.json()["messages"][0]["author_type"] == "tutor"

    dashboard = client.get("/referrals/dashboard", headers=auth("clinic-a"))
    assert dashboard.status_code == 200
    assert dashboard.json()["metrics"]["confirmed_on_the_way"] == 1
    assert dashboard.json()["metrics"]["awaiting_review"] == 0


def test_reload_reads_persisted_referral_and_messages(client):
    referral = create_referral(client)
    client.post(
        f"/referrals/{referral['id']}/messages",
        json={"content": "Mensagem persistida."},
        headers=auth("tutor-a"),
    )
    reloaded = client.get(f"/referrals/{referral['id']}", headers=auth("tutor-a"))
    assert reloaded.status_code == 200
    assert reloaded.json()["messages"][0]["content"] == "Mensagem persistida."


def test_real_mode_requires_session_for_legacy_personal_resources(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKFLOW_MODE", "real")

    assert client.get("/conversations/known-id").status_code == 401
    # O cadastro de tutor/pet no Supabase saiu na rodada 25 do Ryu.
    assert client.get("/tutors/known-id").status_code == 404
    assert client.get("/pets/known-id").status_code == 404
