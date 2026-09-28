"""New workspace contract; all external providers are isolated test doubles."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import mongomock
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.core.config import settings
from app.schemas.workspace import AnimalInput, TurnInput, LocationInput
from app.schemas.auth import SignupRequest, PasswordLoginRequest
from app.services.auth_service import DEMO_ACCOUNTS
from app.services import poc_identity, workspace_service
from app.services.workspace_service import WorkspaceService as Workspace
from app.repositories import workflow_repository
from app.services.referral_service import ReferralService
from app.schemas.referral import ReferralCreate, ReferralResponse
from test_workflow_api import referral_payload


@pytest.fixture
def env(monkeypatch):
    db = mongomock.MongoClient(tz_aware=True).test
    monkeypatch.setattr(settings, "WORKFLOW_MODE", "poc")
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "local")
    monkeypatch.setattr(settings, "POC_QUICK_LOGIN_ENABLED", True)
    monkeypatch.setattr(workspace_service, "get_mongo_database", lambda: db)
    monkeypatch.setattr(poc_identity, "get_mongo_database", lambda: db)
    monkeypatch.setattr(workflow_repository, "get_mongo_database", lambda: db)
    repo = workflow_repository.MongoWorkflowRepository()
    monkeypatch.setattr(workflow_repository, "_mongo_repository", repo)
    return SimpleNamespace(db=db, repo=repo, client=TestClient(app), tutor=DEMO_ACCOUNTS["tutor-a"])


def headers(client, account="tutor-a"):
    r = client.post("/auth/demo", json={"account": account})
    assert r.status_code == 200
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def completed(env):
    c = Workspace.create(env.tutor)
    t = referral_payload()["triage"]
    triage = {"classificacao": t["classification"], "justificativa": t["justification"],
              "sinais_de_alerta": t["warning_signs"], "recomendacao": t["recommendation"]}
    env.db.poc_conversations.update_one({"id": c["id"]}, {"$set": {"messages": [
        {"id": "t1", "role": "tutor", "content": "Relato persistido original.", "created_at": c["created_at"]},
        {"id": "a1", "role": "assistant", "content": "Resposta automática.", "triage": triage,
         "config": {"internal": True}, "created_at": c["created_at"]}]}})
    return c


def test_quick_sessions_are_opaque_revocable_and_hashed(env):
    c = env.client
    h = headers(c)
    token = h["Authorization"][7:]
    assert token.startswith("poc_")
    assert env.db.poc_sessions.find_one()["_id"] != token
    assert c.get("/auth/me", headers=h).status_code == 200
    assert c.get("/auth/me", headers={"Authorization": "Bearer demo:tutor-a"}).status_code == 401
    assert c.post("/auth/logout", headers=h).status_code == 204
    assert c.get("/auth/me", headers=h).status_code == 401


def test_disabled_quick_access_invalidates_existing_sessions(env, monkeypatch):
    h = headers(env.client)
    monkeypatch.setattr(settings, "POC_QUICK_LOGIN_ENABLED", False)
    assert env.client.post("/auth/demo", json={"account": "tutor-a"}).status_code == 404
    assert env.client.get("/auth/me", headers=h).status_code == 401


def test_own_account_password_duplicate_and_expiration(env):
    c = env.client
    data = {"email": "PERSON@example.org", "password": "test-password-123", "display_name": "Test Person", "role": "tutor"}
    assert c.post("/auth/signup", json=data).status_code == 201
    assert c.post("/auth/signup", json=data).status_code == 409
    doc = env.db.poc_accounts.find_one()
    assert doc["password_hash"] != data["password"] and "password" not in doc
    assert c.post("/auth/login", json={"email": data["email"], "password": "wrong-password"}).status_code == 401
    s = c.post("/auth/login", json=data).json()
    assert s["principal"]["demo"] is False
    env.db.poc_sessions.update_many({}, {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(seconds=1)}})
    assert c.get("/auth/me", headers={"Authorization": "Bearer " + s["access_token"]}).status_code == 401


def test_pet_ownership_optional_fields_and_persistence(env):
    c = env.client; a = headers(c); b = headers(c, "tutor-b")
    created = c.post("/workspace/pets", json={"name": "Lua", "species": "gato"}, headers=a)
    assert created.status_code == 201
    pet = created.json()
    assert pet["weight_kg"] is None
    assert c.get("/workspace/pets", headers=b).json() == []
    assert c.put("/workspace/pets/"+pet["id"], json={"name": "Outro", "species": "cao"}, headers=b).status_code == 404
    assert c.put("/workspace/pets/"+pet["id"], json={"name": "Lua", "species": "gato", "weight_kg": 4}, headers=a).status_code == 200
    assert c.get("/workspace/pets", headers=a).json()[0]["weight_kg"] == 4
    assert c.post("/workspace/pets", json={"name": "Lua", "species": "gato", "weight_kg": -1}, headers=a).status_code == 422


def test_conversation_optional_pet_and_idor(env):
    c = env.client; a = headers(c); b = headers(c, "tutor-b")
    pet = c.post("/workspace/pets", json={"name": "Lua", "species": "gato"}, headers=a).json()
    conv = c.post("/workspace/conversations", json={}, headers=a).json()
    assert conv["pet"] is None
    assert c.get("/workspace/conversations/"+conv["id"], headers=b).status_code == 404
    assert c.post("/workspace/conversations", json={"pet_id": pet["id"]}, headers=b).status_code == 404
    assert c.patch("/workspace/conversations/"+conv["id"], json={"pet_id": pet["id"]}, headers=a).json()["pet"]["name"] == "Lua"
    assert c.get("/workspace/conversations", headers=headers(c, "clinic-a")).status_code == 403


def test_turn_persisted_before_processing_and_idempotent(env):
    c = Workspace.create(env.tutor)
    turn = TurnInput(content="Meu gato não come.", request_id="request-123")
    doc, created = Workspace.submit(env.tutor, c["id"], turn)
    assert created and doc["status"] == "processing"
    assert len(doc["messages"]) == 1
    assert Workspace.submit(env.tutor, c["id"], turn)[1] is False
    with pytest.raises(HTTPException) as error:
        Workspace.submit(env.tutor, c["id"], TurnInput(content="Novo.", request_id="request-456"))
    assert error.value.status_code == 409
    with pytest.raises(HTTPException):
        Workspace.associate(env.tutor, c["id"], None)


def test_worker_failure_does_not_expose_exception_and_preserves_report(env):
    c = Workspace.create(env.tutor)
    Workspace.submit(env.tutor, c["id"], TurnInput(content="Meu gato não come.", request_id="request-123"))
    class Broken:
        def execute(self, *args, **kwargs):
            raise RuntimeError("secret-token-should-not-appear")
    Workspace.process(env.tutor, c["id"], "request-123", pipeline=Broken())
    result = Workspace.get(env.tutor, c["id"])
    assert result["status"] == "failed"
    assert "secret-token" not in result["error"]
    assert result["messages"][0]["content"] == "Meu gato não come."


def test_interrupted_processing_has_expiring_lease(env):
    c = Workspace.create(env.tutor)
    env.db.poc_conversations.update_one({"id": c["id"]}, {"$set": {"status": "processing",
        "updated_at": (datetime.now(timezone.utc)-timedelta(minutes=21)).isoformat()}})
    assert Workspace.get(env.tutor, c["id"])["status"] == "failed"


@pytest.mark.parametrize("share", [False, True])
def test_full_conversation_consent_and_snapshot_not_client_controlled(env, share):
    c = completed(env)
    payload = referral_payload() | {"conversation_id": c["id"], "share_full_conversation": share, "pet": None}
    payload["triage"]["original_report"] = "Forged."
    r, _ = ReferralService.create(ReferralCreate(**payload), env.tutor)
    assert r.triage.original_report == "Relato persistido original."
    assert r.pet is None
    assert len(r.shared_conversation) == (2 if share else 0)
    assert all("config" not in m for m in r.shared_conversation)


def test_foreign_conversation_and_missing_conversation_refused(env):
    c = completed(env)
    payload = referral_payload() | {"conversation_id": c["id"]}
    with pytest.raises(HTTPException) as e:
        ReferralService.create(ReferralCreate(**payload), DEMO_ACCOUNTS["tutor-b"])
    assert e.value.status_code == 404
    with pytest.raises(HTTPException) as e:
        ReferralService.create(ReferralCreate(**referral_payload()), env.tutor)
    assert e.value.status_code == 422


def test_pending_clinic_cannot_list_cases(env):
    assert env.client.get("/referrals/", headers=headers(env.client, "clinic-pending")).status_code == 403


def test_location_requires_owner_on_way_and_consent(env):
    from app.services.travel_service import TravelService
    from app.schemas.referral import StatusTransitionRequest
    c = completed(env)
    r, _ = ReferralService.create(ReferralCreate(**(referral_payload() | {"conversation_id": c["id"]})), env.tutor)
    location = LocationInput(consent=True, latitude=-23.56, longitude=-46.65)
    with pytest.raises(HTTPException):
        TravelService.update(r.id, location, env.tutor)
    clinic = DEMO_ACCOUNTS["clinic-a"]
    ReferralService.get(r.id, clinic)
    ReferralService.transition(r.id, StatusTransitionRequest(action="accept"), clinic)
    ReferralService.transition(r.id, StatusTransitionRequest(action="confirm_on_the_way"), env.tutor)
    with pytest.raises(HTTPException):
        TravelService.update(r.id, location, clinic)
    updated = TravelService.update(r.id, location, env.tutor)
    assert updated.location["estimate"] is None  # Never route to fictional clinic.
    assert TravelService.update(r.id, LocationInput(consent=False), env.tutor).location is None
    TravelService.update(r.id, location, env.tutor)
    assert ReferralService.transition(r.id, StatusTransitionRequest(action="arrived"), clinic).location is None


def test_stale_location_is_not_disclosed(env):
    c = completed(env)
    r, _ = ReferralService.create(ReferralCreate(**(referral_payload() | {"conversation_id": c["id"]})), env.tutor)
    doc = r.model_dump() | {"status": "on_the_way", "location": {"latitude": 0, "longitude": 0,
        "updated_at": (datetime.now(timezone.utc)-timedelta(minutes=3)).isoformat()}}
    assert ReferralResponse(**doc).location is None


def test_concurrent_updates_do_not_lose_messages(env):
    c = completed(env)
    r, _ = ReferralService.create(ReferralCreate(**(referral_payload() | {"conversation_id": c["id"]})), env.tutor)
    one = env.repo.get_referral(r.id); two = env.repo.get_referral(r.id)
    one["reviewed_summary"] = "Primeira atualização."
    env.repo.replace_referral(one)
    with pytest.raises(HTTPException) as error:
        env.repo.replace_referral(two)
    assert error.value.status_code == 409
    assert env.repo.get_referral(r.id)["reviewed_summary"] == "Primeira atualização."


def test_maps_real_error_never_becomes_fixtures(env, monkeypatch):
    from app.services import clinic_discovery_service
    monkeypatch.setattr(settings, "MAPS_PROVIDER", "google")
    def fail(*args, **kwargs):
        raise HTTPException(429, "Cota temporariamente indisponível.")
    monkeypatch.setattr(clinic_discovery_service, "google_request", fail)
    response = env.client.post("/clinics/search", json={"latitude": 0, "longitude": 0})
    assert response.status_code == 429
    assert "clinics" not in response.json()


def test_demo_key_does_not_request_user_generated_content(env, monkeypatch):
    from app.services import clinic_discovery_service
    monkeypatch.setattr(settings, "MAPS_PROVIDER", "google")
    monkeypatch.setattr(settings, "MAPS_KEY_KIND", "demo")
    calls = []
    def capture(*args, **kwargs):
        calls.append(kwargs); return {"places": []}
    monkeypatch.setattr(clinic_discovery_service, "google_request", capture)
    result = env.client.post("/clinics/search", json={"latitude": 0, "longitude": 0})
    assert result.json()["mode"] == "real"
    assert all(x not in calls[0]["fields"] for x in ("rating", "userRatingCount", "photos", "reviews"))


def test_poc_protects_legacy_resources(env):
    assert env.client.get("/tutors/known").status_code == 401
    assert env.client.get("/pets/known").status_code == 401
    assert env.client.get("/conversations/known").status_code == 401


def test_worker_uses_current_report_without_truncation_and_records_real_metadata(env):
    from app.pipeline.chat_pipeline import ChatPipeline
    from conftest import LLMClientFalso, RetrievalClientFalso, RerankerFalso, QueryClientFalso, documento
    c = Workspace.create(env.tutor)
    report = "Contexto do tutor. " * 110 + "SINAL_IMPORTANTE_NO_FINAL"
    Workspace.submit(env.tutor, c["id"], TurnInput(content=report, request_id="whole-report-123"))
    llm = LLMClientFalso()
    pipeline = ChatPipeline(query_client=QueryClientFalso(), retrieval_client=RetrievalClientFalso([documento()]), reranker=RerankerFalso, llm_client=llm)
    Workspace.process(env.tutor, c["id"], "whole-report-123", pipeline=pipeline)
    result = Workspace.get(env.tutor, c["id"])
    assert result["status"] == "idle"
    assert len(result["messages"]) == 2
    assert result["messages"][-1]["retrieval"]["used_count"] == 1
    assert result["messages"][-1]["config"]["query_rewriting_enabled"] is False
    assert "SINAL_IMPORTANTE_NO_FINAL" in str(llm.chamadas[0]["messages"])


def test_expired_location_is_physically_removed_when_read(env):
    c = completed(env)
    r, _ = ReferralService.create(ReferralCreate(**(referral_payload() | {"conversation_id": c["id"]})), env.tutor)
    env.repo.referrals.update_one({"id": r.id},{"$set":{"status":"on_the_way","location":{
        "latitude":0,"longitude":0,"updated_at":(datetime.now(timezone.utc)-timedelta(minutes=3)).isoformat()}}})
    assert env.repo.get_referral(r.id)["location"] is None
    assert env.repo.referrals.find_one({"id":r.id})["location"] is None
