"""Offline, dependency-free aggregation of the real conversational benchmark."""
import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import random
import re
import statistics

LABELS = ["EMERGENCIA", "NAO_EMERGENCIA", "INCERTO"]


def ratio(n, d):
    return n / d if d else None


def percentile(values, fraction):
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * fraction
    lo = int(index)
    return values[lo] + (values[min(lo + 1, len(values)-1)] - values[lo]) * (index-lo)


def distribution(values):
    return {"n": len(values), "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None, "p95": percentile(values, .95),
            "min": min(values) if values else None, "max": max(values) if values else None}


def score(rows):
    matrix = {true: {pred: 0 for pred in LABELS + ["ERROR"]} for true in LABELS}
    for row in rows:
        matrix[row["expected"]][row["classification"] if row["status"] == "idle" and row["classification"] in LABELS else "ERROR"] += 1
    support = {key: sum(value.values()) for key, value in matrix.items()}
    recalls = {key: ratio(matrix[key][key], support[key]) for key in LABELS}
    f1 = {}
    for label in LABELS:
        tp = matrix[label][label]
        fn = support[label] - tp
        fp = sum(matrix[other][label] for other in LABELS if other != label)
        f1[label] = ratio(2*tp, 2*tp+fn+fp)
    return {"n": len(rows), "correct": sum(matrix[k][k] for k in LABELS),
            "accuracy": ratio(sum(matrix[k][k] for k in LABELS), len(rows)),
            "macro_f1": statistics.mean(v for v in f1.values() if v is not None) if rows else None,
            "balanced_accuracy": statistics.mean(v for v in recalls.values() if v is not None) if rows else None,
            "recall": recalls, "f1": f1, "confusion_matrix": matrix,
            "emergency_to_non_emergency": matrix["EMERGENCIA"]["NAO_EMERGENCIA"],
            "emergency_to_uncertain": matrix["EMERGENCIA"]["INCERTO"],
            "binary_coverage": ratio(sum(r["classification"] in LABELS[:2] and r["status"] == "idle" for r in rows), len(rows)),
            "errors": sum(r["status"] != "idle" for r in rows),
            "latency_s": distribution([r["wall_s"] for r in rows]),
            "calls_per_turn": distribution([len(r["calls"]) for r in rows]),
            "prompt_tokens_total": sum(c.get("prompt_tokens", 0) for r in rows for c in r["calls"]),
            "completion_tokens_total": sum(c.get("completion_tokens", 0) for r in rows for c in r["calls"]),
            "invalid_schema_calls": sum(c.get("schema_valid") is False for r in rows for c in r["calls"]),
            "llm_attempts": sum(c.get("attempts", 0) for r in rows for c in r["calls"])}


def paired(before, after):
    left = {(r["case_id"], r["repetition"]): r for r in before}
    right = {(r["case_id"], r["repetition"]): r for r in after}
    keys = sorted(left.keys() & right.keys())
    groups = defaultdict(list)
    latencies = []
    retrieval_jaccard = []
    regressions, gains, changed = [], [], []
    for key in keys:
        a, b = left[key], right[key]
        sources_a = {x.get("title", x.get("source")) for x in a.get("message", {}).get("sources", [])}
        sources_b = {x.get("title", x.get("source")) for x in b.get("message", {}).get("sources", [])}
        if sources_a or sources_b:
            retrieval_jaccard.append(len(sources_a & sources_b) / len(sources_a | sources_b))
        ca = a["status"] == "idle" and a["classification"] == a["expected"]
        cb = b["status"] == "idle" and b["classification"] == b["expected"]
        groups[key[0]].append(int(cb)-int(ca))
        latencies.append(b["wall_s"]-a["wall_s"])
        if ca and not cb:
            regressions.append(list(key))
        if cb and not ca:
            gains.append(list(key))
        if a["classification"] != b["classification"]:
            changed.append(list(key))
    rng = random.Random(42)
    values = [statistics.mean(v) for v in groups.values()]
    boots = [statistics.mean(rng.choices(values, k=len(values))) for _ in range(4000)] if values else []
    return {"paired_predictions": len(keys), "independent_case_clusters": len(groups),
            "accuracy_delta": statistics.mean(values) if values else None,
            "cluster_bootstrap_ci95": [percentile(boots,.025), percentile(boots,.975)],
            "latency_delta_s": distribution(latencies), "retrieval_source_jaccard": distribution(retrieval_jaccard), "regressions": regressions,
            "gains": gains, "changed_predictions": changed}


def summarize(records):
    turns = [r for r in records if r["kind"] == "turn"]
    calibration = [r for r in turns if r["phase"] == "baseline" and r["arm"] != "warmup"]
    grouped = {arm: [r for r in calibration if r["arm"] == arm] for arm in ["before", "after"]}
    dialog_arms = sorted(set(r["arm"] for r in turns if r["phase"] in {"prepare", "finish"} and r["arm"] != "warmup"))
    dialogs = {arm: [r for r in turns if r["arm"] == arm and r["phase"] in {"prepare", "finish"}] for arm in dialog_arms}
    prepared = [r for r in records if r["kind"] == "prepared"]
    form_cases = [r for r in prepared if (r.get("followup") or {}).get("state") == "form"]
    results = {"calibration": {arm: score(rows) for arm, rows in grouped.items()},
               "calibration_paired": paired(grouped["before"], grouped["after"]),
               "per_repetition": {str(rep): {arm: score([r for r in rows if r["repetition"] == rep]) for arm, rows in grouped.items()}
                                  for rep in sorted(set(r["repetition"] for r in calibration))},
               "dialogs": {arm: score(rows) for arm, rows in dialogs.items()},
               "prepared_cases": len(prepared), "form_reached": len(form_cases),
               "form_reasons": dict(Counter(r["followup"]["reason"] for r in form_cases)),
               "turns_to_form": distribution([sum(t["case_id"] == r["case_id"] and t["arm"] in {"after_initial","after_unknown"} for t in turns) for r in form_cases]),
               "form_vs_identical_text": paired(dialogs.get("after_same_text", []), dialogs.get("after_form", [])),
               "old_vs_new_with_identical_data": paired(dialogs.get("before_same_text", []), dialogs.get("after_form", [])),
               "total_turns": len(turns), "total_llm_calls": sum(len(r["calls"]) for r in turns),
               "warmup": [r["wall_s"] for r in turns if r["arm"] == "warmup"],
               "stage_metrics": {stage: {"latency_s": distribution([c["wall_s"] for r in turns for c in r["calls"] if c["stage"] == stage]),
                   "prompt_tokens": sum(c.get("prompt_tokens",0) for r in turns for c in r["calls"] if c["stage"] == stage),
                   "completion_tokens": sum(c.get("completion_tokens",0) for r in turns for c in r["calls"] if c["stage"] == stage)} for stage in ["classification","followup"]}}
    results["exploratory_ablation"] = score([r for r in turns if r["phase"] == "ablation" and r["arm"] != "warmup"])
    results["exploratory_recheck"] = {arm: score([r for r in turns if r["phase"] == "recheck" and r["arm"] == arm]) for arm in ["after_form", "after_same_text"]}
    if any(r["phase"] == "legacy_recheck" for r in turns):
        results["legacy_recheck"] = {arm: score([r for r in turns if r["phase"] == "legacy_recheck" and r["arm"] == arm])
                                     for arm in ["after_form", "after_same_text"]}
    results["journeys"] = []
    for prepared_case in prepared:
        case_id = prepared_case["case_id"]
        prefix = [r for r in turns if r["phase"] == "prepare" and r["case_id"] == case_id and r["arm"] in {"after_initial", "after_unknown"}]
        final = next((r for r in turns if r["phase"] == "finish" and r["case_id"] == case_id and r["arm"] == "after_form"), None)
        journey = prefix + ([final] if final else [])
        results["journeys"].append({"case_id": case_id, "turns": len(journey),
            "wall_s": sum(r["wall_s"] for r in journey), "calls": sum(len(r["calls"]) for r in journey),
            "initial_classification": prefix[0]["classification"] if prefix else None,
            "final_classification": final["classification"] if final else None,
            "expected_final": prepared_case["expected_final"], "form_answered": final is not None,
            "prompt_tokens": sum(c.get("prompt_tokens",0) for r in journey for c in r["calls"]),
            "completion_tokens": sum(c.get("completion_tokens",0) for r in journey for c in r["calls"])})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    records = [json.loads(line) for line in (args.directory / "raw.jsonl").read_text().splitlines()]
    summary = summarize(records)
    summary["provider_backoffs"] = {path.name.removesuffix("-runtime.log"): {
        "http_429_backoff_events": len(re.findall(r"Gemini 429", path.read_text())),
        "http_503_backoff_events": len(re.findall(r"Gemini 503", path.read_text()))}
        for path in sorted(args.directory.glob("*-runtime.log"))}
    summary["logical_llm_calls_note"] = "classify invocations; HTTP backoff retries are additional, token counts are those reported by the successful/last response."
    summary["all_turns_idle"] = all(r["status"] == "idle" for r in records if r["kind"] == "turn")
    audit_path = args.directory / "auditoria-formularios.csv"
    if audit_path.exists():
        with audit_path.open() as handle:
            audit = list(csv.DictReader(handle))
        summary["preset_audit"] = {
            "reviewer": "engineering agent, not clinical expert", "forms": len(audit),
            "compatible_presets_among_six_known_cases": sum(r["preset_compativel_fato_congelado"] == "sim" for r in audit),
            "missing_normal_option": sum(r["opcao_factual_ausente"] == "sim" for r in audit),
            "semantic_key_reused_for_different_question": sum(r["mudanca_semantica_mesma_chave"] == "sim" for r in audit)}
    (args.directory / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n")
    turns = [r for r in records if r["kind"] == "turn"]
    columns = ["case_id", "phase", "arm", "repetition", "expected", "classification", "status", "wall_s", "state", "form_reason", "calls", "prompt_tokens", "completion_tokens"]
    with (args.directory / "turns.csv").open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in turns:
            writer.writerow({**{k: row.get(k) for k in columns[:8]}, "state": (row.get("followup") or {}).get("state"),
                "form_reason": (row.get("followup") or {}).get("reason"), "calls": len(row["calls"]),
                "prompt_tokens": sum(c.get("prompt_tokens",0) for c in row["calls"]),
                "completion_tokens": sum(c.get("completion_tokens",0) for c in row["calls"])})
    print(json.dumps({"calibration": summary["calibration"], "dialogs": summary["dialogs"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
