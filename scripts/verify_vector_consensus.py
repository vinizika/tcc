"""Verifica consenso entre fingerprints e artefatos de uma ingestão."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


FINGERPRINT_FIELDS = (
    "collection",
    "document_count",
    "chunk_count",
    "chunk_ids_sha256",
    "content_sha256",
    "embedding_model",
    "embedding_revision",
    "recipe_sha256",
    "source_set_sha256",
    "profile",
)


class ConsensusError(ValueError):
    pass


def load_json(path: Path) -> dict:
    if not path.exists():
        raise ConsensusError(f"Artefato ausente: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConsensusError(f"JSON inválido em {path}: {error}") from error
    if not isinstance(payload, dict):
        raise ConsensusError(f"{path} deve conter um objeto JSON.")
    return payload


def vector_store(fingerprint: dict) -> dict:
    return fingerprint.get("vector_store") or fingerprint


def fingerprint_identity(fingerprint: dict) -> dict:
    store = vector_store(fingerprint)
    return {field: store.get(field) for field in FINGERPRINT_FIELDS}


def _required(payload: dict, fields: tuple[str, ...], artifact: str) -> None:
    missing = [field for field in fields if payload.get(field) in (None, "")]
    if missing:
        raise ConsensusError(
            f"{artifact} sem campo(s) obrigatório(s): {', '.join(missing)}"
        )


def verify_fingerprint_consensus(fingerprints: list[dict]) -> dict:
    if len(fingerprints) < 2:
        raise ConsensusError("Informe ao menos dois fingerprints.")
    identities = [fingerprint_identity(item) for item in fingerprints]
    for index, identity in enumerate(identities, start=1):
        _required(identity, FINGERPRINT_FIELDS, f"fingerprint {index}")
    reference = identities[0]
    divergences = {
        field: [identity[field] for identity in identities]
        for field in FINGERPRINT_FIELDS
        if any(identity[field] != reference[field] for identity in identities[1:])
    }
    if divergences:
        raise ConsensusError(
            "Fingerprints divergentes: "
            + json.dumps(divergences, ensure_ascii=False, sort_keys=True)
        )
    return {
        "status": "consensus",
        "fingerprint_count": len(fingerprints),
        "identity": reference,
    }


def _manifest_sha256(manifest: dict) -> str:
    canonical = json.dumps(
        manifest,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_artifact_consensus(
    *,
    manifest: dict,
    fingerprint: dict,
    receipt: dict,
    actual: dict | None = None,
) -> dict:
    """Cruza manifesto, fingerprint, recibo e estado real opcional."""

    chunks = manifest.get("chunks") or {}
    embedding = manifest.get("embedding") or {}
    chunking = manifest.get("chunking") or {}
    sources = manifest.get("sources") or {}
    expected = {
        "collection": manifest.get("collection_name"),
        "document_count": sources.get("document_count"),
        "chunk_count": chunks.get("count"),
        "chunk_ids_sha256": chunks.get("ids_sha256"),
        "content_sha256": chunks.get("content_sha256"),
        "embedding_model": embedding.get("model"),
        "embedding_revision": embedding.get("revision"),
        "recipe_sha256": chunking.get("recipe_sha256"),
        "source_set_sha256": sources.get("source_set_sha256"),
        "profile": manifest.get("profile"),
    }
    _required(expected, FINGERPRINT_FIELDS, "manifesto")
    observed = fingerprint_identity(fingerprint)
    _required(observed, FINGERPRINT_FIELDS, "fingerprint")

    divergences = {
        field: {"manifest": expected[field], "fingerprint": observed[field]}
        for field in FINGERPRINT_FIELDS
        if expected[field] != observed[field]
    }
    receipt_expected = {
        "collection_name": expected["collection"],
        "profile": expected["profile"],
        "chunk_count": expected["chunk_count"],
        "manifest_sha256": _manifest_sha256(manifest),
    }
    for field, expected_value in receipt_expected.items():
        if receipt.get(field) != expected_value:
            divergences[f"receipt.{field}"] = {
                "expected": expected_value,
                "actual": receipt.get(field),
            }

    if actual is not None:
        for field in ("chunk_count", "chunk_ids_sha256", "content_sha256"):
            if actual.get(field) != expected[field]:
                divergences[f"actual.{field}"] = {
                    "expected": expected[field],
                    "actual": actual.get(field),
                }

    if divergences:
        raise ConsensusError(
            "Artefatos divergentes: "
            + json.dumps(divergences, ensure_ascii=False, sort_keys=True)
        )
    return {
        "status": "consensus",
        "collection": expected["collection"],
        "profile": expected["profile"],
        "chunk_count": expected["chunk_count"],
        "manifest_sha256": receipt_expected["manifest_sha256"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Confere fingerprints de máquinas ou artefatos de ingestão."
    )
    parser.add_argument(
        "fingerprints",
        nargs="*",
        type=Path,
        help="Dois ou mais fingerprints para consenso entre máquinas.",
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--fingerprint", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--actual", type=Path)
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    artifact_args = (args.manifest, args.fingerprint, args.receipt)
    if any(artifact_args):
        if not all(artifact_args):
            raise SystemExit(
                "--manifest, --fingerprint e --receipt devem ser usados juntos."
            )
        result = verify_artifact_consensus(
            manifest=load_json(args.manifest),
            fingerprint=load_json(args.fingerprint),
            receipt=load_json(args.receipt),
            actual=load_json(args.actual) if args.actual else None,
        )
    else:
        result = verify_fingerprint_consensus(
            [load_json(path) for path in args.fingerprints]
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
