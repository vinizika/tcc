"""
Confere se algum caso da prova nova (data/prova/) compartilha texto com os
documentos da base — a regra 4 da muralha
(docs/plano-base-e-prova.md#a-muralha-entre-base-e-prova):

    "Antes de fechar, um passo automático confere sobreposição de texto
    entre os casos da prova e os documentos da base."

Se um caso repetir a linguagem de um documento, o sistema pode acertar por
eco (recuperar o trecho certo porque o texto bate palavra por palavra) em
vez de por entender o relato — a mesma armadilha que a régua de recuperação
já evita ao escrever os relatos antes de ler a fonte.

Compara por n-gramas de palavras (janela deslizante), não por frase inteira:
um relato de tutor nunca deveria repetir 6 palavras seguidas de um artigo
cientifico por acaso.

Roda dentro do container (só precisa do ChromaDB, sem Ollama):

    docker exec backend-api python -m app.database.check_prova_overlap \\
        --collection <nome-da-candidata> --chroma-path /app/chroma_db \\
        --cases /app/../data/prova/casos_oficiais.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from app.core.logger import setup_logger
from app.database.chroma_client import ChromaDBClient

logger = setup_logger("CheckProvaOverlap")

N_GRAMA = 6


def normaliza_palavras(texto: str) -> list[str]:
    return re.findall(r"[a-zà-ú0-9]+", texto.lower())


def n_gramas(palavras: list[str], tamanho: int) -> set[tuple[str, ...]]:
    return {
        tuple(palavras[i : i + tamanho])
        for i in range(len(palavras) - tamanho + 1)
    }


def main(argv: list[str] | None = None) -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True)
    parser.add_argument("--chroma-path", type=Path, default=None)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--n-grama", type=int, default=N_GRAMA)
    argumentos = parser.parse_args(argv)

    if argumentos.chroma_path:
        ChromaDBClient.configure(path=argumentos.chroma_path)

    colecao = ChromaDBClient._get_strict_collection(
        argumentos.collection,
        with_embedding_function=False,
    )

    conteudo = colecao.get(include=["documents"])
    chunks = conteudo["documents"]

    logger.warning(
        f"Comparando contra {len(chunks)} chunks da coleção "
        f"{argumentos.collection!r}, n-grama={argumentos.n_grama}"
    )

    ngramas_da_base: set[tuple[str, ...]] = set()
    for chunk in chunks:
        ngramas_da_base |= n_gramas(normaliza_palavras(chunk), argumentos.n_grama)

    with argumentos.cases.open(encoding="utf-8", newline="") as arquivo:
        casos = list(csv.DictReader(arquivo))

    problemas = 0

    for caso in casos:
        palavras = normaliza_palavras(caso["text"])
        ngramas_do_caso = n_gramas(palavras, argumentos.n_grama)
        colisoes = ngramas_do_caso & ngramas_da_base

        if colisoes:
            problemas += 1
            exemplo = " ".join(next(iter(colisoes)))
            logger.error(
                f"{caso['id']} ({caso.get('topic') or 'sem tópico'}): "
                f"{len(colisoes)} n-grama(s) em comum com a base. "
                f'Exemplo: "{exemplo}"'
            )

    if problemas == 0:
        print(
            f"OK: nenhum dos {len(casos)} casos compartilha "
            f"{argumentos.n_grama}-grama com a base ({len(chunks)} chunks)."
        )
    else:
        print(
            f"ATENÇÃO: {problemas} de {len(casos)} casos compartilham "
            f"texto com a base. Ver o log acima."
        )


if __name__ == "__main__":
    main()
