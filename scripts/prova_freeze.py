"""
Congela um split da prova nova por hash (docs/plano-base-e-prova.md, "A
cadência: congelar não é deixar de usar").

Congelar significa: a partir de agora, nenhuma linha do split `teste` pode
mudar — nem para corrigir um caso que o sistema errou. Se algum dia isso
precisar acontecer de propósito (ex.: validação de especialista muda um
rótulo), é uma decisão explícita: recongelar, registrar por quê e quando, e
qualquer rodada anterior que citava o hash antigo passa a apontar para uma
versão que não existe mais — o que é o comportamento certo, não um bug.

O hash cobre a linha inteira (todas as colunas), não só `text` e
`expected_class`: editar até a coluna `note` sem recongelar conscientemente
já é o tipo de deriva silenciosa que este instrumento existe para impedir.

Uso:

    # Congela pela primeira vez (ou recongela de propósito)
    python scripts/prova_freeze.py --cases data/prova/casos_oficiais.csv \\
        --split teste --freeze

    # Confere se o split ainda bate com o que foi congelado (falha se não)
    python scripts/prova_freeze.py --cases data/prova/casos_oficiais.csv \\
        --split teste
"""

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def carregar_split(caminho: Path, split: str) -> list[dict]:

    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = [row for row in csv.DictReader(arquivo) if row["split"] == split]

    return sorted(linhas, key=lambda linha: linha["id"])


def hash_split(linhas: list[dict]) -> str:

    serializado = json.dumps(linhas, ensure_ascii=False, sort_keys=True)

    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def caminho_manifesto(caminho_casos: Path, split: str) -> Path:

    return caminho_casos.with_suffix(f".{split}.freeze.json")


def main(argv: list[str] | None = None) -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument(
        "--freeze",
        action="store_true",
        help="Grava (ou regrava) o manifesto de congelamento com o hash atual.",
    )
    argumentos = parser.parse_args(argv)

    linhas = carregar_split(argumentos.cases, argumentos.split)

    if not linhas:
        raise SystemExit(
            f"Nenhuma linha com split={argumentos.split!r} em {argumentos.cases}."
        )

    hash_atual = hash_split(linhas)
    manifesto_path = caminho_manifesto(argumentos.cases, argumentos.split)

    if argumentos.freeze:

        manifesto = {
            "cases_file": str(argumentos.cases),
            "split": argumentos.split,
            "row_count": len(linhas),
            "sha256": hash_atual,
            "frozen_at": datetime.now(timezone.utc).astimezone().isoformat(),
        }

        manifesto_path.write_text(
            json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        print(f"Congelado: {len(linhas)} linhas, sha256={hash_atual}")
        print(f"Manifesto: {manifesto_path}")
        return

    if not manifesto_path.exists():
        raise SystemExit(
            f"Nenhum congelamento registrado em {manifesto_path}. "
            "Rode com --freeze para criar um."
        )

    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    hash_esperado = manifesto["sha256"]

    if hash_atual != hash_esperado:
        raise SystemExit(
            f"O split {argumentos.split!r} MUDOU desde o congelamento "
            f"({manifesto['frozen_at']}).\n"
            f"  esperado: {hash_esperado}\n"
            f"  atual   : {hash_atual}\n"
            "Se a mudança foi de propósito (ex.: validação de especialista), "
            "rode de novo com --freeze para recongelar conscientemente."
        )

    print(
        f"OK: {len(linhas)} linhas batem com o congelamento de "
        f"{manifesto['frozen_at']} (sha256={hash_atual})."
    )


if __name__ == "__main__":
    main()
