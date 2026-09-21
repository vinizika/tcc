"""
Mede `query_s` (o tempo da etapa de consulta) com o modelo já aquecido,
contra uma coleção candidata do trilho A — o número que faltava para
fechar o B-07 (evidencias/backlog.md#b-07).

As rodadas anteriores (17/09) confirmaram por log que Multi-Query e HyDE
rodam em paralelo, mas não produziram um número limpo: a chamada caiu num
cold-start do Ollama (a reescrita sozinha levou 70s) e a coleção ativa
estava vazia. Este script resolve os dois problemas: aquece o modelo com
uma chamada descartada antes de medir, e aponta o `ChatPipeline` para uma
coleção candidata via monkeypatch de `ChromaDBClient.get_collection` — o
mesmo mecanismo de `measure_query_techniques.py` —, sem tocar o ponteiro
ativo.

Roda dentro do container (precisa do ChromaDB e do Ollama já de pé):

    docker exec backend-api python -m app.database.measure_query_latency \\
        --collection <nome-da-candidata> --chroma-path /app/chroma_db \\
        --repeats 5
"""

from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path

from app.core.logger import setup_logger
from app.database.chroma_client import ChromaDBClient
from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.triage import PipelineOptions

logger = setup_logger("MeasureQueryLatency")

RELATOS = [
    "meu cachorro comeu chocolate",
    "minha gata não consegue fazer xixi desde ontem",
    "meu cachorro está com diarreia e vômito há dois dias",
    "meu gato está espirrando e com o olho lacrimejando",
    "minha cadela está com a barriga inchada e tentando vomitar sem sucesso",
]


def aquecer(pipeline: ChatPipeline) -> None:
    """
    Uma chamada descartada, fora da medição — a primeira chamada ao Ollama
    depois de um tempo parado recarrega o modelo e não representa o custo
    em regime normal (visto na rodada 8: a reescrita sozinha levou 70s).
    """

    inicio = time.perf_counter()

    pipeline.execute(
        RELATOS[0],
        PipelineOptions(
            multi_query_enabled=True,
            hyde_enabled=True,
            retrieval_enabled=False,
        ),
    )

    logger.info(f"Aquecimento concluído em {time.perf_counter() - inicio:.1f}s")


def medir(pipeline: ChatPipeline, repeats: int) -> list[float]:

    tempos: list[float] = []

    for indice in range(repeats):

        relato = RELATOS[indice % len(RELATOS)]

        resultado = pipeline.execute(
            relato,
            PipelineOptions(
                multi_query_enabled=True,
                hyde_enabled=True,
                include_debug=True,
            ),
        )

        query_s = resultado.timings.query_s
        tempos.append(query_s)

        logger.info(f"[{indice + 1}/{repeats}] {relato!r} -> query_s={query_s:.3f}")

    return tempos


def main(argv: list[str] | None = None) -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True)
    parser.add_argument("--chroma-path", type=Path, default=None)
    parser.add_argument("--repeats", type=int, default=5)
    argumentos = parser.parse_args(argv)

    if argumentos.chroma_path:
        ChromaDBClient.configure(path=argumentos.chroma_path)

    colecao = ChromaDBClient._get_strict_collection(
        argumentos.collection,
        with_embedding_function=True,
    )

    logger.warning(
        f"Apontando ChatPipeline para a candidata {argumentos.collection!r} "
        f"({colecao.count()} chunks) — só neste processo; ponteiro ativo "
        "não é tocado."
    )

    ChromaDBClient.get_collection = classmethod(lambda cls: colecao)

    pipeline = ChatPipeline()

    aquecer(pipeline)

    tempos = medir(pipeline, argumentos.repeats)

    print(f"\nquery_s por chamada: {[round(t, 3) for t in tempos]}")
    print(f"mediana: {statistics.median(tempos):.3f}s")
    print(f"média:   {statistics.mean(tempos):.3f}s")
    print(f"min/max: {min(tempos):.3f}s / {max(tempos):.3f}s")


if __name__ == "__main__":
    main()
