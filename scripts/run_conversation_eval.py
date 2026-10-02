"""Real before/after service benchmark, executed inside the existing backend container.
Uses a separate Mongo database, frozen old workspace source and real provider calls.
Usage: python scripts/run_conversation_eval.py --phase baseline|prepare|finish|ablation|recheck --output-dir DIR
Prepare freezes actual questions before a human selects truthful form responses in actions.json.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

MARKER = "EVAL_JSON "


def completed_turns(records, phase):
    """A recheck must never suppress a primary observation with the same case ID."""
    return [[r["case_id"], r["arm"], r["repetition"]] for r in records
            if r["kind"] == "turn" and r["phase"] == phase and r["status"] == "idle"]


def worker(payload):
    import copy
    import hashlib
    import time
    from datetime import datetime, timezone
    from types import ModuleType
    from uuid import uuid4
    from app.core.config import settings
    from app.schemas.auth import Principal
    from app.schemas.workspace import TurnInput
    from app.services import workspace_service as current
    from app.clients.gemini_llm_client import GeminiLLMClient
    from app.clients.llm_client import LLMClient

    settings.MONGODB_DB_NAME = payload.get("mongo_database", "tcc_followup_eval_20260928")
    old_module = ModuleType("baseline_workspace")
    exec(compile(payload["baseline_source"], "baseline_workspace.py", "exec"), old_module.__dict__)
    old = old_module.WorkspaceService
    new = current.WorkspaceService
    principal = Principal(user_id="benchmark-synthetic-tutor", role="tutor", display_name="Avaliação sintética")
    calls = []

    def emit(value):
        def clean(item):
            if isinstance(item, dict):
                return {k: clean(v) for k, v in item.items() if k not in {"raciocinio", "_id"}}
            if isinstance(item, list):
                return [clean(v) for v in item]
            return item
        print(MARKER + json.dumps(clean(value), ensure_ascii=False), flush=True)

    for cls in (GeminiLLMClient, LLMClient):
        original = cls.classify
        def instrument(self, messages, output_model, _original=original, **kwargs):
            started = time.perf_counter()
            item = {"stage": "followup" if output_model.__name__ in {"FollowupPlan", "FollowupSelection"} else "classification",
                    "input_sha256": hashlib.sha256(json.dumps(messages, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                    "provider": self.provider, "model": kwargs.get("model") or getattr(self, "model", settings.LLM_MODEL)}
            try:
                result = _original(self, messages, output_model, **kwargs)
                item.update(prompt_tokens=result.prompt_tokens, completion_tokens=result.completion_tokens,
                    attempts=result.attempts, schema_valid=result.schema_valid, model=result.model,
                    model_version=result.model_version)
                return result
            except Exception as error:
                item["error_type"] = type(error).__name__
                raise
            finally:
                item["wall_s"] = time.perf_counter() - started
                calls.append(item)
        cls.classify = instrument

    def turn(service, doc, text, case_id, arm, expected, repetition=0, metadata=None):
        calls.clear()
        started = time.perf_counter()
        request_id = str(uuid4())
        submitted, created = service.submit(principal, doc["id"], TurnInput(
            content=text, request_id=request_id, attendant_provider=payload["manifest"]["provider"], **(metadata or {})))
        service.process(principal, doc["id"], request_id)
        elapsed = time.perf_counter() - started
        saved = service.get(principal, doc["id"])
        message = next((m for m in reversed(saved["messages"]) if m["role"] == "assistant"), {})
        row = {"kind": "turn", "phase": payload["phase"], "case_id": case_id, "arm": arm,
               "repetition": repetition, "expected": expected, "request_id": request_id,
               "conversation_id": saved["id"], "input": text, "status": saved["status"],
               "error": saved.get("error"), "wall_s": elapsed, "calls": list(calls),
               "classification": message.get("triage", {}).get("classificacao") if saved["status"] == "idle" else None,
               "message": message, "followup": saved.get("followup"),
               "message_count": len(saved["messages"]), "utc": datetime.now(timezone.utc).isoformat()}
        emit(row)
        if saved.get("error_code") == "quota_exhausted":
            raise RuntimeError("Daily provider quota exhausted; partial results saved")
        return saved

    emit({"kind": "environment", "phase": payload["phase"], "utc": datetime.now(timezone.utc).isoformat(),
          "collection": current.active_collection_name(), "mongo_database": settings.MONGODB_DB_NAME,
          "baseline_sha256": hashlib.sha256(payload["baseline_source"].encode()).hexdigest(),
          "settings": {key: getattr(settings, key) for key in ["ATTENDANT_PROVIDER", "ATTENDANT_FALLBACK", "GEMINI_MODEL",
              "RETRIEVAL_MODE", "CONTEXT_TOP_K", "CONTEXT_MIN_SCORE", "TRIAGE_PROMPT_VERSION", "COT_ENABLED",
              "LLM_NUM_CTX", "WORKSPACE_NUM_CTX", "FOLLOWUP_NO_PROGRESS_LIMIT", "FOLLOWUP_MAX_QUESTIONS"]}})
    if payload["phase"] == "baseline":
        # Separate cold initialization/warmup from steady-state latency.
        turn(old, old.create(principal), "Meu gato não consegue respirar, está com a boca aberta e faz força para respirar.",
             "warmup", "warmup", "EMERGENCIA")
        for repetition in range(payload["manifest"]["calibration_repetitions"]):
            for index, case in enumerate(payload["manifest"]["calibration"]):
                services = [("before", old), ("after", new)]
                if (index + repetition) % 2:
                    services.reverse()
                for arm, service in services:
                    key = [case["id"], arm, repetition]
                    if key in payload.get("completed", []):
                        continue
                    turn(service, service.create(principal), case["text"], case["id"], arm, case["expected_class"], repetition)
    elif payload["phase"] in {"recheck", "legacy_recheck"}:
        turn(old, old.create(principal), "Meu gato tem muita dificuldade para respirar de boca aberta.", "warmup", "warmup", "EMERGENCIA")
        case = next(c for c in payload["manifest"]["dialogs"] if c["id"] == "c03")
        if payload["phase"] == "legacy_recheck":
            action = payload["legacy_action"]
            prepared = payload["legacy_prepared"]
            original_doc = new.create(principal)
            original_doc.update(messages=prepared["messages"], followup=prepared["followup"])
        else:
            action = payload["actions"]["c03"]
            original_doc = new.get(principal, action["conversation_id"])
        text = action["option"] + " — " + action["complement"]
        for repetition in range(3):
            arms = ["after_form", "after_same_text"] if repetition % 2 == 0 else ["after_same_text", "after_form"]
            for arm in arms:
                if ["c03", arm, repetition] in payload.get("completed_phase", []):
                    continue
                clone = copy.deepcopy(original_doc)
                clone["id"] = str(uuid4())
                clone.pop("_id", None)
                new.db().poc_conversations.insert_one(clone)
                metadata = {"origin": "form", "question_id": original_doc["followup"]["question_id"], "selected_option": action["option"]} if arm == "after_form" else {}
                turn(new, clone, text, "c03", arm, case["expected_final"], repetition, metadata)
    elif payload["phase"] == "ablation":
        turn(old, old.create(principal), "Meu gato tem muita dificuldade para respirar de boca aberta.", "warmup", "warmup", "EMERGENCIA")
        # Exploratory diagnostic only: keep new classification prompt/state,
        # remove workspace instructions/JSON from the vector-search query.
        from types import MethodType
        from app.services.followup_service import RULES
        pipeline = current.poc_pipeline()
        original_build = pipeline._build_queries
        def clean_queries(self, question, config):
            if question.startswith(RULES):
                entries = json.loads(question[len(RULES):])
                question = "\n".join(e["resposta_do_tutor"] for e in entries)
            return original_build(question, config)
        pipeline._build_queries = MethodType(clean_queries, pipeline)
        for repetition in range(2):
            for case in payload["manifest"]["calibration"]:
                if case["id"] not in {"p01", "p02", "p11", "p14"}:
                    continue
                if [case["id"], "after_clean_retrieval", repetition] in payload.get("completed", []):
                    continue
                turn(new, new.create(principal), case["text"], case["id"], "after_clean_retrieval", case["expected_class"], repetition)
    elif payload["phase"] == "prepare":
        for case in payload["manifest"]["dialogs"]:
            if case["id"] in payload.get("prepared", []):
                continue
            before = turn(old, old.create(principal), case["initial"], case["id"], "before_initial", "INCERTO")
            doc = turn(new, new.create(principal), case["initial"], case["id"], "after_initial", "INCERTO")
            for i in range(5):
                if doc["status"] != "idle" or (doc.get("followup") or {}).get("state") != "asking":
                    break
                doc = turn(new, doc, "Não sei dizer", case["id"], "after_unknown", "INCERTO", i)
            emit({"kind": "prepared", "case_id": case["id"], "conversation_id": doc["id"],
                  "status": doc["status"], "followup": doc.get("followup"), "fact": case["fact"],
                  "expected_final": case["expected_final"], "messages": doc["messages"]})
    elif payload["phase"] == "finish":
        turn(old, old.create(principal), "Meu gato tem muita dificuldade para respirar de boca aberta.", "warmup", "warmup", "EMERGENCIA")
        for case in payload["manifest"]["dialogs"]:
            action = payload["actions"].get(case["id"])
            if action is None:
                continue
            original_doc = new.get(principal, action["conversation_id"])
            state = original_doc.get("followup") or {}
            if state.get("state") != "form":
                raise ValueError("Expected an actual pending form")
            option = action["option"]
            if option is not None and option not in state["options"]:
                raise ValueError("Option is not part of the actual form")
            text = ((option + " — ") if option and action.get("complement") else (option or "")) + action.get("complement", "")
            branches = [("after_form", new, text, case["expected_final"], {"origin": "form", "question_id": state["question_id"], "selected_option": option}),
                        ("after_same_text", new, text, case["expected_final"], {}),
                        ("before_same_text", old, text, case["expected_final"], {}),
                        ("after_no_data", new, "Não observei", "INCERTO", {"origin": "form", "question_id": state["question_id"], "selected_option": "Não observei"})]
            if option is None:
                branches = [branch for branch in branches if branch[0] != "after_form"]
                emit({"kind": "unavailable_form_answer", "case_id": case["id"], "reason": action["note"]})
            # Alternate arm order across cases.
            if int(case["id"][1:]) % 2:
                branches.reverse()
            for arm, service, content, expected, metadata in branches:
                if [case["id"], arm, 0] in payload.get("completed", []):
                    continue
                clone = copy.deepcopy(original_doc)
                clone["id"] = str(uuid4())
                clone.pop("_id", None)
                new.db().poc_conversations.insert_one(clone)
                turn(service, clone, content, case["id"], arm, expected, metadata=metadata)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["baseline", "prepare", "finish", "ablation", "recheck", "legacy_recheck"], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mongo-database", default="tcc_followup_eval_20260928")
    parser.add_argument("--legacy-dir", type=Path)
    args = parser.parse_args()
    directory = args.output_dir
    out = directory / "raw.jsonl"
    existing = [json.loads(line) for line in out.read_text().splitlines()] if out.exists() else []
    payload = {"phase": args.phase, "mongo_database": args.mongo_database,
               "manifest": json.loads((directory / "cases.json").read_text()),
               "baseline_source": (directory / "baseline_workspace.py").read_text(),
               "completed": completed_turns(existing, args.phase),
               "completed_phase": [[r["case_id"], r["arm"], r["repetition"]] for r in existing if r["kind"] == "turn" and r["phase"] == args.phase],
               "prepared": [r["case_id"] for r in existing if r["kind"] == "prepared"],
               "actions": json.loads((directory / "actions.json").read_text()) if (directory / "actions.json").exists() else {}}
    if args.phase == "legacy_recheck":
        if args.legacy_dir is None:
            parser.error("legacy_recheck requires --legacy-dir")
        payload["legacy_action"] = json.loads((args.legacy_dir / "actions.json").read_text())["c03"]
        payload["legacy_prepared"] = next(r for r in map(json.loads, (args.legacy_dir / "raw.jsonl").read_text().splitlines())
                                          if r["kind"] == "prepared" and r["case_id"] == "c03")
    source = Path(__file__).read_text().rsplit('if __name__ == "__main__":', 1)[0] + "\nworker(json.load(sys.stdin))\n"
    with (directory / (args.phase + "-runtime.log")).open("a") as log, out.open("a") as output:
        process = subprocess.Popen(["docker", "exec", "-i", "backend-api", "python", "-u", "-c", source],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, text=True)
        process.stdin.write(json.dumps(payload))
        process.stdin.close()
        for line in process.stdout:
            if line.startswith(MARKER):
                value = json.loads(line[len(MARKER):])
                output.write(json.dumps(value, ensure_ascii=False) + "\n")
                output.flush()
                print(value.get("case_id", "env"), value.get("arm", value["kind"]), value.get("classification", ""),
                      round(value.get("wall_s", 0), 2), flush=True)
            else:
                log.write(line)
        raise SystemExit(process.wait())


if __name__ == "__main__":
    main()
