"""
Conferência de vazamento da prova 2 antes de congelar (B-63; especificação na
rodada 20 do João, medidas registradas na rodada 17 do Ryu).

Só entram o texto, a classe e o assunto: nenhum sistema é avaliado, então
rodar isto não "gasta" o lote teste. As referências da prova 1 (0,79 por
assunto, 0,91 aleatória, 0,77 no "mas") são as da rodada 20.

    python scripts/prova2_conferir.py
    python scripts/prova2_conferir.py --output <arquivo.json>
"""

import argparse
import csv
import json
from pathlib import Path

from prova_baselines import (
    naive_bayes_cv_repetido,
    naive_bayes_treino_teste,
    regra_mas,
)

RAIZ = Path(__file__).resolve().parents[1]
PROVA2 = RAIZ / "data" / "prova2" / "casos.csv"
PROVA1 = [
    RAIZ / "data" / "prova" / "casos_oficiais.csv",
    RAIZ / "data" / "prova" / "casos_calibracao.csv",
]


def ler(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def conferir(prova2: list[dict], prova1: list[dict]) -> dict:
    calibracao = [c for c in prova2 if c["split"] == "calibracao"]
    teste = [c for c in prova2 if c["split"] == "teste"]
    return {
        "a_cv_por_assunto": naive_bayes_cv_repetido(prova2, chave_grupo="topic"),
        "b_treino_prova1_teste_prova2": naive_bayes_treino_teste(prova1, prova2),
        "c_regra_mas": regra_mas(prova2),
        "d_treino_calibracao_teste_teste": naive_bayes_treino_teste(calibracao, teste),
        "e_cv_aleatoria": naive_bayes_cv_repetido(prova2),
        "referencia_prova1": {
            "cv_por_assunto": naive_bayes_cv_repetido(prova1, chave_grupo="topic"),
            "cv_aleatoria": naive_bayes_cv_repetido(prova1),
            "regra_mas": regra_mas(prova1),
        },
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    prova1 = [linha for caminho in PROVA1 for linha in ler(caminho)]
    resultado = conferir(ler(PROVA2), prova1)
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    if args.output:
        args.output.write_text(texto + "\n", encoding="utf-8", newline="\n")
    print(texto)


if __name__ == "__main__":
    main()
