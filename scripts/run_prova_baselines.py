"""
Roda os baselines triviais (prova_baselines.py) contra a prova nova e
imprime o veredito do critério do B-05: nenhuma regra sem modelo deveria
passar de 0,90.

    python scripts/run_prova_baselines.py --cases data/prova/casos_oficiais.csv
    python scripts/run_prova_baselines.py --cases data/prova/casos_oficiais.csv --split teste
"""

import argparse
import csv
import json
from pathlib import Path

from prova_baselines import compute_baselines

LIMIAR_B05 = 0.90


def main() -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--split")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--output", type=Path)
    argumentos = parser.parse_args()

    with argumentos.cases.open(encoding="utf-8", newline="") as arquivo:
        casos = list(csv.DictReader(arquivo))

    if argumentos.split:
        casos = [caso for caso in casos if caso.get("split") == argumentos.split]

    resultado = compute_baselines(casos, k=argumentos.k)

    print(f"Casos avaliados: {len(casos)} (split={argumentos.split or 'todos'})\n")

    algum_passou_do_limiar = False

    for baseline in resultado.values():
        acuracia = baseline["acuracia"]
        estourou = acuracia is not None and acuracia >= LIMIAR_B05
        algum_passou_do_limiar = algum_passou_do_limiar or estourou
        marca = "ACIMA DE 0,90 !!" if estourou else "abaixo de 0,90"
        print(f"{baseline['nome']:28s} acurácia={acuracia}  ({marca})  n={baseline['n']}")

    print()
    if algum_passou_do_limiar:
        print("B-05 REPROVADO: pelo menos um baseline trivial passou de 0,90.")
    else:
        print("B-05 OK: nenhum baseline trivial passou de 0,90.")

    if argumentos.output:
        argumentos.output.write_text(
            json.dumps(resultado, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nGravado em {argumentos.output}")


if __name__ == "__main__":
    main()
