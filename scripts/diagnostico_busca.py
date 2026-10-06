"""
A busca sabe quando erra? (rodada 19 do Ryu, B-69)

Para cada relato dos conjuntos de desenvolvimento, chama `POST /search/` com o
relato cru e guarda as fichas devolvidas, as notas de semelhança e a posição
da ficha certa. Não chama modelo de linguagem: não gasta cota do Gemini.
Nenhum caso dos lotes `teste` (prova 1 e prova 2) entra.

    python scripts/diagnostico_busca.py --output <arquivo.jsonl>
"""

import argparse
import csv
import json
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[1]

# (nome, papel, arquivo, split exigido ou None, coluna do assunto)
CONJUNTOS = [
    ("prova2_calibracao", "calibrar", "data/prova2/casos.csv", "calibracao", "topic"),
    ("prova1_dev", "calibrar", "data/prova/casos_oficiais.csv", "dev", "topic"),
    ("prova1_calibracao", "calibrar", "data/prova/casos_calibracao.csv", None, "topic"),
    ("regua", "calibrar", "data/retrieval/cases.csv", None, "expected_topics"),
    ("independentes", "conferir", "data/diagnostico/relatos_independentes.csv", None, "topic"),
    ("piloto", "conferir", "data/diagnostico/piloto_prova2.csv", None, "topic"),
]


def casos_do_conjunto(arquivo: str, split: str | None, coluna: str) -> list[dict]:
    with (RAIZ / arquivo).open(encoding="utf-8", newline="") as entrada:
        linhas = list(csv.DictReader(entrada))
    casos = []
    for linha in linhas:
        if split is not None and linha.get("split") != split:
            continue
        assuntos = [a.strip() for a in linha.get(coluna, "").replace(";", "|").split("|") if a.strip()]
        if assuntos:
            casos.append({"id": linha["id"], "text": linha["text"], "topics": assuntos})
    return casos


def buscar(api_url: str, texto: str) -> list[dict]:
    resposta = requests.post(f"{api_url}/search/", json={"question": texto}, timeout=600)
    resposta.raise_for_status()
    return [{"topic": d["topic"], "score": d["score"]} for d in resposta.json()["documents"]]


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    with args.output.open("w", encoding="utf-8", newline="\n") as saida:
        for nome, papel, arquivo, split, coluna in CONJUNTOS:
            casos = casos_do_conjunto(arquivo, split, coluna)
            for caso in casos:
                fichas = buscar(args.api_url, caso["text"])
                posicoes = [i + 1 for i, f in enumerate(fichas) if f["topic"] in caso["topics"]]
                saida.write(json.dumps({
                    "conjunto": nome, "papel": papel, "id": caso["id"],
                    "topics": caso["topics"], "fichas": fichas,
                    "posicao_certa": posicoes[0] if posicoes else None,
                }, ensure_ascii=False) + "\n")
            print(f"{nome}: {len(casos)} casos")


if __name__ == "__main__":
    main()
