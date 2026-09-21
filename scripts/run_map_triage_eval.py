"""Avalia a triagem nos relatos PT-BR da régua de recuperação.

Complementa ``run_evaluation.py``: aquele preserva o conjunto histórico em
inglês; este verifica se melhorar a busca pelo mapa também melhora a decisão
final nos relatos cotidianos em português.
"""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

import requests

from run_evaluation import agora, escrever_atomico, git_estado


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "retrieval" / "cases.csv"
RUNS = ROOT / "data" / "evaluation" / "map_runs"


def options(mode: str) -> dict:
    return {
        "retrieval_enabled": mode == "rag",
        "query_rewriting_enabled": False,
        "multi_query_enabled": False,
        "hyde_enabled": False,
        "prompt_version": "v1_grounded",
        "context_min_score": 0.72,
        "include_debug": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("rag", "no_rag"), required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    with CASES.open(encoding="utf-8", newline="") as source:
        cases = list(csv.DictReader(source))
    if args.limit:
        cases = cases[: args.limit]

    run_id = f"{datetime.now():%Y%m%d-%H%M%S}_{args.name}"
    directory = RUNS / run_id
    started_at = agora()

    health = requests.get(f"{args.api_url.rstrip('/')}/health/", timeout=10)
    health.raise_for_status()
    fingerprint = requests.get(
        f"{args.api_url.rstrip('/')}/health/fingerprint", timeout=30
    ).json()

    rows = []
    selected_options = options(args.mode)
    for index, case in enumerate(cases, 1):
        response = requests.post(
            f"{args.api_url.rstrip('/')}/chat/",
            json={"question": case["text"], "options": selected_options},
            timeout=(5, args.timeout),
        )
        response.raise_for_status()
        payload = response.json()
        triage = payload["triage"]
        retrieval = payload.get("retrieval") or {}
        predicted = triage["classificacao"]
        row = {
            "id": case["id"],
            "text": case["text"],
            "expected": case["expected_class"],
            "predicted": predicted,
            "correct": predicted == case["expected_class"],
            "sources_used": retrieval.get("used_count", 0),
            "max_vector_score": retrieval.get("max_score"),
            "max_ranking_score": retrieval.get("max_ranking_score"),
            "classification": triage,
        }
        rows.append(row)
        print(
            f"[{index:2}/{len(cases)}] {case['id']} "
            f"{case['expected_class']} -> {predicted} "
            f"ctx={row['sources_used']}"
        )

    total = len(rows)
    correct = sum(row["correct"] for row in rows)
    false_nonurgent = sum(
        row["expected"] == "EMERGENCIA"
        and row["predicted"] != "EMERGENCIA"
        for row in rows
    )
    false_urgent = sum(
        row["expected"] == "NAO_EMERGENCIA"
        and row["predicted"] == "EMERGENCIA"
        for row in rows
    )
    emergency_total = sum(
        row["expected"] == "EMERGENCIA" for row in rows
    )
    nonurgent_total = sum(
        row["expected"] == "NAO_EMERGENCIA" for row in rows
    )
    emergency_recall = (
        (emergency_total - false_nonurgent) / emergency_total
        if emergency_total else None
    )
    nonurgent_recall = (
        (nonurgent_total - false_urgent) / nonurgent_total
        if nonurgent_total else None
    )
    balanced_accuracy = (
        (emergency_recall + nonurgent_recall) / 2
        if emergency_recall is not None and nonurgent_recall is not None
        else None
    )
    metrics = {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else None,
        "balanced_accuracy": balanced_accuracy,
        "emergency_recall": emergency_recall,
        "nonurgent_recall": nonurgent_recall,
        "false_nonurgent": false_nonurgent,
        "false_urgent": false_urgent,
        "cases_with_context": sum(row["sources_used"] > 0 for row in rows),
    }
    manifest = {
        "run_id": run_id,
        "started_at": started_at,
        "mode": args.mode,
        "options": selected_options,
        "git": git_estado(),
        "backend_fingerprint": fingerprint,
    }

    # Só materializa a rodada depois que todos os casos terminam. Uma queda
    # da API ou interrupção do Ollama não pode deixar uma pasta vazia que
    # pareça uma avaliação reproduzida.
    directory.mkdir(parents=True)
    escrever_atomico(
        directory / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2),
    )
    escrever_atomico(
        directory / "metrics.json",
        json.dumps(metrics, ensure_ascii=False, indent=2),
    )
    escrever_atomico(
        directory / "predictions.jsonl",
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(directory)


if __name__ == "__main__":
    main()
