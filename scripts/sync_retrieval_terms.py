"""Gera o vocabulário de recuperação a partir do mapa de assuntos.

O backend roda dentro de uma imagem que contém apenas ``backend/``. Por isso
ele não lê o CSV da raiz em produção: este script compila somente os campos
necessários para um JSON pequeno e versionável. ``--check`` permite ao CI
detectar quando o mapa mudou e o artefato ficou desatualizado.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "curadoria" / "mapa-de-assuntos.csv"
OUTPUT_PATH = ROOT / "backend" / "data" / "retrieval_terms.json"


def build_payload() -> dict:
    raw = MAP_PATH.read_bytes()
    with MAP_PATH.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    topics: dict[str, list[str]] = {}
    for row in rows:
        terms = [
            row["quadro"].strip(),
            *(
                term.strip()
                for term in row["sinais_que_o_tutor_relata"].split(";")
            ),
        ]
        topics[row["id"].strip()] = [term for term in terms if term]

    return {
        "source": "data/curadoria/mapa-de-assuntos.csv",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "topics": dict(sorted(topics.items())),
    }


def render(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = render(build_payload())
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""

    if args.check:
        if current != expected:
            raise SystemExit(
                "backend/data/retrieval_terms.json está desatualizado; "
                "execute python scripts/sync_retrieval_terms.py"
            )
        print("retrieval_terms.json atualizado")
        return

    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"gerado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
