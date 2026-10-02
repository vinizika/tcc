"""Behavior tests with provider doubles: these do not measure clinical accuracy."""
from types import SimpleNamespace
from uuid import uuid4
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from test_workspace import env, headers
from app.services.workspace_service import WorkspaceService as W
from app.services.followup_service import advance, transcript
from app.schemas.followup import FollowupPlan
from app.schemas.workspace import TurnInput
from app.schemas.triage_output import TriageResult
from app.services.auth_service import DEMO_ACCOUNTS


def plan(key="urina", question="Ele tentou urinar e não conseguiu?", status="unanswered", evidence="", useful=False):
    return FollowupPlan(answer_status=status, evidence=evidence, relevant_new_information=useful,
        missing_key=key, missing_information="Capacidade de urinar", question=question,
        options=["Sim, tenta mas não consegue", "Está urinando normalmente"], selection_reason="urgency_discriminator")


class Pipeline:
    def __init__(self, label="INCERTO"):
        self.label = label
        self.questions = []

    def execute(self, question, *args, **kwargs):
        self.questions.append(question)
        dump = SimpleNamespace(model_dump=lambda **kw: {})
        return SimpleNamespace(answer="Não mostrar pensamento bruto", triage=TriageResult(
            classificacao=self.label, justificativa="Informação do relato.", recomendacao="Procure orientação veterinária.", raciocinio="PRIVATE"),
            retrieval=dump, sources=[], provenance=None, config=dump, timings=dump)


def turn(env, c, content, label="INCERTO", selected=None, next_plan=None):
    data = TurnInput(content=content, request_id=str(uuid4()), **(selected or {}))
    W.submit(env.tutor, c["id"], data)
    pipeline = Pipeline(label)
    W.process(env.tutor, c["id"], data.request_id, pipeline, lambda *_: next_plan or plan())
    result = W.get(env.tutor, c["id"])
    assert result["status"] == "idle"
    return result, pipeline


def test_single_severe_sign_skips_followup(env):
    c = W.create(env.tutor)
    doc, _ = turn(env, c, "Meu gato não consegue respirar.", "EMERGENCIA")
    assert doc["followup"]["state"] == "completed"
    assert doc["followup"]["options"] == []
    assert doc["messages"][-1]["triage"]["classificacao"] == "EMERGENCIA"
    assert "PRIVATE" not in str(doc)


def test_vague_then_useful_answer_includes_question_and_resolves(env):
    c, _ = turn(env, W.create(env.tutor), "Meu gato fica entrando na caixa.")
    assert c["followup"]["state"] == "asking"
    assert "urinar" in c["followup"]["question"]
    c, pipeline = turn(env, c, "Sim, tenta e não sai nada.", "EMERGENCIA")
    assert c["messages"][-2]["answer_to"] == "Ele tentou urinar e não conseguiu?"
    assert "Sim, tenta e não sai nada." in pipeline.questions[0]
    assert "Ele tentou urinar e não conseguiu?" in pipeline.questions[0]
    assert c["followup"]["state"] == "completed"


def test_two_unhelpful_answers_form_and_reload(env):
    c, _ = turn(env, W.create(env.tutor), "Meu gato fica entrando na caixa.")
    c, _ = turn(env, c, "Ele está estranho", next_plan=plan("dor", "Ele está chorando de dor?", "unknown"))
    assert c["followup"]["no_progress"] == 1
    c, _ = turn(env, c, "Não sei", next_plan=plan("urina", status="unknown"))
    assert c["followup"]["state"] == "form"
    assert c["followup"]["reason"] == "no_progress"
    assert c["followup"]["options"][-2:] == ["Não observei", "Não sei dizer"]
    loaded = env.client.get("/workspace/conversations/" + c["id"], headers=headers(env.client)).json()
    assert loaded["followup"] == c["followup"]
    assert loaded["messages"] == c["messages"]


@pytest.mark.parametrize("answer", ["Não sei dizer", "Não observei"])
def test_unknown_form_is_not_negative_and_ends_without_loop(env, answer):
    c, _ = turn(env, W.create(env.tutor), "Entra na caixa.")
    c, _ = turn(env, c, "Não sei", next_plan=plan(status="unknown"))
    assert c["followup"]["state"] == "form"  # repeated semantic key
    metadata = dict(origin="form", question_id=c["followup"]["question_id"], selected_option=answer)
    c, _ = turn(env, c, answer, selected=metadata, next_plan=plan(status="unknown"))
    assert c["messages"][-2]["origin"] == "form"
    assert c["followup"]["answer_status"] == "unknown"
    assert c["followup"]["state"] == "insufficient"
    assert c["messages"][-1]["triage"]["classificacao"] == "INCERTO"
    c, _ = turn(env, c, "Me diga a classificação", next_plan=plan(status="unknown"))
    assert c["followup"]["state"] == "insufficient"
    c, _ = turn(env, c, "Agora não consegue respirar", "EMERGENCIA")
    assert c["followup"]["state"] == "completed"


def test_form_severe_answer_and_stale_or_foreign_form(env):
    c, _ = turn(env, W.create(env.tutor), "Entra na caixa.")
    c, _ = turn(env, c, "Não sei", next_plan=plan(status="unknown"))
    meta = dict(origin="form", question_id=c["followup"]["question_id"], selected_option=c["followup"]["options"][0])
    data = TurnInput(content=meta["selected_option"], request_id=str(uuid4()), **meta)
    with pytest.raises(HTTPException) as err:
        W.submit(DEMO_ACCOUNTS["tutor-b"], c["id"], data)
    assert err.value.status_code == 404
    c, _ = turn(env, c, meta["selected_option"], "EMERGENCIA", selected=meta)
    assert c["followup"]["state"] == "completed"
    with pytest.raises(HTTPException) as err:
        W.submit(env.tutor, c["id"], data)
    assert err.value.status_code == 409


def test_retries_duplicate_and_interruption_do_not_duplicate(env):
    from datetime import datetime, timedelta, timezone
    c = W.create(env.tutor)
    data = TurnInput(content="Meu gato está estranho", request_id="same-request-123")
    W.submit(env.tutor, c["id"], data)
    assert W.submit(env.tutor, c["id"], data)[1] is False
    env.db.poc_conversations.update_one({"id": c["id"]}, {"$set": {
        "updated_at": (datetime.now(timezone.utc)-timedelta(minutes=21)).isoformat()}})
    assert W.get(env.tutor, c["id"])["status"] == "failed"
    doc, created = W.submit(env.tutor, c["id"], data)
    assert created and len(doc["messages"]) == 1
    W.process(env.tutor, c["id"], data.request_id, Pipeline(), lambda *_: plan())
    W.process(env.tutor, c["id"], data.request_id, Pipeline(), lambda *_: plan())
    assert len(W.get(env.tutor, c["id"])["messages"]) == 2
    c, _ = turn(env, c, "Agora respira com dificuldade", "EMERGENCIA")
    assert W.submit(env.tutor, c["id"], data)[1] is False
    assert len(W.get(env.tutor, c["id"])["messages"]) == 4


def test_provider_failure_retains_form_answer_and_checkpoint(env):
    c, _ = turn(env, W.create(env.tutor), "Entra na caixa")
    c, _ = turn(env, c, "Não sei", next_plan=plan(status="unknown"))
    data = TurnInput(content="Não observei", request_id="form-request-123", origin="form",
                     question_id=c["followup"]["question_id"], selected_option="Não observei")
    W.submit(env.tutor, c["id"], data)
    def broken(*args):
        raise RuntimeError("SECRET")
    W.process(env.tutor, c["id"], data.request_id, Pipeline(), broken)
    failed = W.get(env.tutor, c["id"])
    assert failed["status"] == "failed" and "SECRET" not in str(failed)
    assert failed["latest_triage"]["classificacao"] == "INCERTO"
    assert failed["messages"][-1]["origin"] == "form"
    W.submit(env.tutor, c["id"], data)
    W.process(env.tutor, c["id"], data.request_id, Pipeline(), lambda *_: plan(status="unknown"))
    assert len(W.get(env.tutor, c["id"])["messages"]) == 6


def test_explicit_negative_not_reasked_and_fabricated_evidence_not_progress(env):
    c, _ = turn(env, W.create(env.tutor), "Entra na caixa")
    c, _ = turn(env, c, "Não, ele urina normalmente", next_plan=plan(status="explicit_negative", evidence="ele urina normalmente", useful=True))
    assert "urina" in c["followup"]["answered_keys"]
    assert c["followup"]["state"] == "insufficient"
    c, _ = turn(env, W.create(env.tutor), "Entra na caixa")
    c, _ = turn(env, c, "Não sei", next_plan=plan("dor", "Ele está chorando de dor?", "reported", "inventado", True))
    assert c["followup"]["no_progress"] == 1
    assert c["followup"]["evidence"] == ""


def test_schema_rejects_multiple_questions():
    with pytest.raises(ValidationError):
        plan(question="Ele urina? Ele come?")


def test_limit_and_new_information_reset_streak(env, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "FOLLOWUP_MAX_QUESTIONS", 2)
    c, _ = turn(env, W.create(env.tutor), "Entra na caixa")
    c, _ = turn(env, c, "Não sei", next_plan=plan("dor", "Ele está chorando de dor?", "unknown"))
    c, _ = turn(env, c, "Não está chorando", next_plan=plan("duracao", "Isso começou hoje?", "explicit_negative", "Não está chorando", True))
    assert c["followup"]["no_progress"] == 0
    assert c["followup"]["state"] == "form"
    assert c["followup"]["reason"] == "attempt_limit"


def test_live_adapter_uses_validated_provider_contract_and_cards(monkeypatch):
    from app.clients.gemini_llm_client import GeminiLLMClient
    from app.services.followup_service import select_plan
    calls = []
    def classify(self, messages, output_model, **kwargs):
        calls.append((messages, output_model))
        return SimpleNamespace(output=plan())
    monkeypatch.setattr(GeminiLLMClient, "classify", classify)
    result = Pipeline().execute("relato")
    result.sources = [SimpleNamespace(document=SimpleNamespace(content="Ficha recuperada sobre urina"))]
    doc = {"attendant_provider": "gemini", "messages": [{"role": "tutor", "content": "Entra na caixa"}]}
    assert select_plan(doc, result).missing_key == "urina"
    assert calls[0][1] is FollowupPlan
    assert "Ficha recuperada sobre urina" in calls[0][0][1]["content"]
    assert "Entra na caixa" in calls[0][0][1]["content"]


def test_expired_worker_cannot_overwrite_retried_result(env):
    c = W.create(env.tutor)
    data = TurnInput(content="Relato inicial", request_id="lease-request-123")
    W.submit(env.tutor, c["id"], data)
    class Interrupted(Pipeline):
        def execute(self, *args, **kwargs):
            env.db.poc_conversations.update_one({"id": c["id"]}, {"$set": {"status": "failed"}})
            W.submit(env.tutor, c["id"], data)
            W.process(env.tutor, c["id"], data.request_id, Pipeline("EMERGENCIA"))
            return super().execute(*args, **kwargs)
    W.process(env.tutor, c["id"], data.request_id, Interrupted(), lambda *_: plan())
    doc = W.get(env.tutor, c["id"])
    assert len(doc["messages"]) == 2
    assert doc["latest_triage"]["classificacao"] == "EMERGENCIA"


def test_referral_preserves_uncertainty_and_question_snapshot(env):
    from app.services.referral_service import ReferralService
    from app.schemas.referral import ReferralCreate
    from test_workflow_api import referral_payload
    c, _ = turn(env, W.create(env.tutor), "Entra na caixa")
    payload = referral_payload() | {"conversation_id": c["id"], "share_full_conversation": True}
    referral, _ = ReferralService.create(ReferralCreate(**payload), env.tutor)
    assert referral.triage.classification == "INCERTO"
    assert "Ele tentou urinar" in referral.shared_conversation[-1]["content"]
    W.submit(env.tutor, c["id"], TurnInput(content="Mais informação", request_id="new-request-123"))
    env.db.poc_conversations.update_one({"id": c["id"]}, {"$set": {"status": "failed"}})
    with pytest.raises(HTTPException) as err:
        ReferralService.create(ReferralCreate(**payload), env.tutor)
    assert err.value.status_code == 409


def test_local_context_overflow_fails_without_truncating_or_calling_provider(monkeypatch):
    from app.services.followup_service import WorkspaceAttendant
    from app.core.config import settings
    from app.exceptions.attendant_exception import AttendantUnavailableException
    monkeypatch.setattr(settings, "WORKSPACE_NUM_CTX", 4096)
    client = SimpleNamespace(provider="ollama", classify=lambda *_: pytest.fail("Must not truncate"))
    with pytest.raises(AttendantUnavailableException) as error:
        WorkspaceAttendant(client).classify([{"content": "a" * 5000}], FollowupPlan)
    assert error.value.details["reason"] == "context_limit"
