"""Orquestra avaliação antes/depois e ingestão com fail-stop."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
RETRIEVAL_RUNS = ROOT / "data" / "retrieval" / "runs"
CYCLE_RUNS = ROOT / "data" / "retrieval" / "cycles"


class CycleError(RuntimeError):
    pass


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def run_command(
    command: list[str],
    *,
    cwd: Path = ROOT,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=capture_output,
        capture_output=capture_output,
    )
    if completed.returncode:
        details = ""
        if capture_output:
            details = f"\n{completed.stdout or ''}{completed.stderr or ''}".rstrip()
        raise CycleError(
            f"Etapa falhou ({completed.returncode}): {' '.join(command)}"
            + details
        )
    if capture_output and completed.stderr:
        sys.stderr.write(completed.stderr)
    return completed


def api_fingerprint(api_url: str, timeout: int) -> dict:
    response = requests.get(
        f"{api_url.rstrip('/')}/health/fingerprint",
        timeout=(5, timeout),
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise CycleError("Fingerprint da API não é um objeto JSON.")
    return payload


def newest_run(before: set[Path]) -> Path:
    after = set(RETRIEVAL_RUNS.iterdir()) if RETRIEVAL_RUNS.exists() else set()
    created = sorted(after - before)
    if len(created) != 1:
        raise CycleError(
            f"Esperava uma rodada nova; encontrei {len(created)}."
        )
    return created[0]


def run_retrieval(name: str, api_url: str, timeout: int) -> Path:
    before = set(RETRIEVAL_RUNS.iterdir()) if RETRIEVAL_RUNS.exists() else set()
    run_command(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_retrieval_eval.py"),
            "--name",
            name,
            "--api-url",
            api_url,
            "--timeout",
            str(timeout),
        ]
    )
    return newest_run(before)


def plan(name: str, profile: str, activate: bool) -> dict:
    return {
        "name": name,
        "profile": profile,
        "steps": [
            "capture_before_fingerprint",
            "run_before_retrieval_evaluation",
            "prepare_all_documents_before_chroma",
            "create_and_validate_staged_collection",
            *(["activate_candidate"] if activate else ["stop_after_staging"]),
            *(
                [
                    "capture_after_fingerprint",
                    "run_after_retrieval_evaluation",
                    "compare_runs",
                ]
                if activate
                else []
            ),
            "write_cycle_receipt",
        ],
    }


def execute_cycle(
    *,
    name: str,
    profile: str,
    api_url: str,
    timeout: int,
    activate: bool,
) -> dict:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", name):
        raise CycleError("O nome do ciclo deve ser um slug sem caminho.")
    cycle_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + f"_{name}"
    )
    cycle_dir = CYCLE_RUNS / cycle_id
    before_fingerprint = api_fingerprint(api_url, timeout)
    before_run = run_retrieval(f"{name}_before", api_url, timeout)

    ingestion_command = [
        sys.executable,
        "-m",
        "app.database.ingest_documents",
        "--profile",
        profile,
        "--activate" if activate else "--stage-only",
    ]
    completed = run_command(
        ingestion_command,
        cwd=BACKEND,
        capture_output=True,
    )
    try:
        ingestion_result = json.loads(completed.stdout)
        manifest = ingestion_result["manifest"]
        ingestion_receipt = ingestion_result["receipt"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise CycleError(
            "A ingestão terminou sem manifesto/recibo JSON utilizável."
        ) from error

    receipt = {
        "schema_version": 1,
        "cycle_id": cycle_id,
        "profile": profile,
        "before_fingerprint": before_fingerprint,
        "before_run": str(before_run.relative_to(ROOT)),
        "activated": activate,
        "staged_collection": manifest["collection_name"],
        "manifest": manifest,
        "ingestion_receipt": ingestion_receipt,
    }
    if activate:
        try:
            after_fingerprint = api_fingerprint(api_url, timeout)
            from verify_vector_consensus import verify_artifact_consensus

            artifact_consensus = verify_artifact_consensus(
                manifest=manifest,
                fingerprint=after_fingerprint,
                receipt=ingestion_receipt,
            )
            after_run = run_retrieval(f"{name}_after", api_url, timeout)
            run_command(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_retrieval_eval.py"),
                    "compare",
                    str(before_run),
                    str(after_run),
                ]
            )
            receipt.update(
                {
                    "after_fingerprint": after_fingerprint,
                    "after_run": str(after_run.relative_to(ROOT)),
                    "artifact_consensus": artifact_consensus,
                }
            )
        except Exception as error:
            receipt["error"] = str(error)
            rollback_command = [
                sys.executable,
                "-m",
                "app.database.ingest_documents",
                "--rollback",
            ]
            receipt["rollback_command"] = "cd backend && " + " ".join(
                rollback_command
            )
            try:
                rollback = run_command(
                    rollback_command,
                    cwd=BACKEND,
                    capture_output=True,
                )
                receipt["rollback"] = json.loads(rollback.stdout)
            except Exception as rollback_error:
                receipt["rollback_error"] = str(rollback_error)
            atomic_write(
                cycle_dir / "receipt.json",
                json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            )
            raise

    atomic_write(
        cycle_dir / "receipt.json",
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
    )
    return receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Planeja ou executa o ciclo controlado de ingestão."
    )
    parser.add_argument("--name", required=True)
    parser.add_argument(
        "--profile",
        choices=("curated", "experimental", "legacy_rechunk"),
        default="curated",
    )
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Sem esta flag, apenas imprime o plano sem modificar estado.",
    )
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Após validar staging, ativa e executa avaliação posterior.",
    )
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    planned = plan(args.name, args.profile, args.activate)
    if not args.execute:
        print(json.dumps(planned, ensure_ascii=False, indent=2))
        return
    result = execute_cycle(
        name=args.name,
        profile=args.profile,
        api_url=args.api_url,
        timeout=args.timeout,
        activate=args.activate,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
