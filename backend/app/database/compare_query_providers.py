"""
Compara Gemini x Ollama na etapa de consulta (reescrita, Multi-Query, HyDE)
— o teste pedido pelo grupo em 22/09: um modelo maior ajuda o suficiente
para justificar depender de uma API externa?

Isolado da produção de propósito: `ChatPipeline` continua usando só o
`QueryClient` (Ollama). Este script só compara os dois, sem tocar em nada
que o tutor real usa.

Para cada caso, monta a lista de consultas (reescrita + Multi-Query + HyDE,
já fundidas como o B-10 decidiu) com cada provedor, e recupera contra a
mesma coleção candidata — o mesmo mecanismo de
`measure_query_techniques.py`, sem tocar o ponteiro ativo.

Respeita o limite gratuito do Gemini com dois freios, porque a cota diária
(por volta de 250-1.000 chamadas, dependendo do modelo) e o limite por
minuto (por volta de 10-15) são baixos:

- `--gemini-delay-s`: pausa entre chamadas ao Gemini (padrão 7s, seguro
  mesmo no limite mais apertado).
- `--max-gemini-calls`: teto rígido de chamadas nesta execução (padrão 30
  — dá para 10 casos, 3 chamadas cada). Passar do teto para a execução
  sem gastar mais nada.

Se o Gemini estourar o limite no meio da rodada (`LLMException`), o caso
é registrado com o erro em vez de derrubar a execução inteira — os casos
já medidos não se perdem.

Roda dentro do container (precisa do ChromaDB já de pé, do Ollama, e de
GEMINI_API_KEY configurada no .env):

    docker exec backend-api python -m app.database.compare_query_providers \\
        --collection <nome-da-candidata> --chroma-path /app/chroma_db \\
        --cases /tmp/cases.json --output /tmp/comparacao.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from app.clients.gemini_query_client import GeminiQueryClient
from app.clients.query_client import QueryClient
from app.clients.retrieval_client import RetrievalClient
from app.core.logger import setup_logger
from app.database.chroma_client import ChromaDBClient
from app.exceptions.llm_exception import LLMException

logger = setup_logger("CompareQueryProviders")

GEMINI_DELAY_S_PADRAO = 7.0
MAX_GEMINI_CALLS_PADRAO = 30


def montar_consultas(query_client, relato: str, contador_gemini: list[int] | None,
                      max_chamadas: int, atraso_s: float, e_gemini: bool) -> dict:
    """
    Reescrita + Multi-Query + HyDE, fundidas do mesmo jeito que
    `chat_pipeline._build_queries` faz em produção (decisão do B-10) — só
    assim a comparação mede o que o pipeline real usaria com cada provedor.
    """

    def chamar(func, *args):
        if e_gemini:
            if contador_gemini[0] >= max_chamadas:
                raise LLMException(
                    f"Teto de {max_chamadas} chamadas ao Gemini atingido "
                    "nesta execução — pare aqui para não gastar mais cota."
                )
            contador_gemini[0] += 1
        resultado = func(*args)
        if e_gemini:
            time.sleep(atraso_s)
        return resultado

    reescrita = (chamar(query_client.rewrite, relato) or "").strip() or relato

    variacoes = [
        v.strip()
        for v in chamar(query_client.generate_queries, reescrita)
        if v and v.strip()
    ]

    hipotetico = (
        chamar(query_client.generate_hypothetical_document, reescrita) or ""
    ).strip()

    fundido = []
    for consulta in [reescrita, *variacoes]:
        if consulta and consulta not in fundido:
            fundido.append(consulta)
    if hipotetico:
        fundido.append(hipotetico)

    return {
        "rewritten": reescrita,
        "variations": variacoes,
        "hypothetical_document": hipotetico,
        "queries": fundido,
    }


def medir_caso(caso: dict, contador_gemini: list[int], max_chamadas: int,
               atraso_s: float) -> dict:

    resultado = {"id": caso["id"], "expected_topics": caso.get("expected_topics", "")}

    for nome, cliente, e_gemini in (
        ("ollama", QueryClient, False),
        ("gemini", GeminiQueryClient, True),
    ):
        try:
            consultas = montar_consultas(
                cliente, caso["text"], contador_gemini, max_chamadas, atraso_s, e_gemini
            )
            recuperados = RetrievalClient.retrieve(consultas["queries"])
            resultado[nome] = {
                **consultas,
                "topics": [documento.topic for documento in recuperados],
                "scores": [round(documento.score, 6) for documento in recuperados],
            }
            logger.info(
                f"{caso['id']} / {nome}: {[d.topic for d in recuperados]}"
            )
        except LLMException as erro:
            logger.error(f"{caso['id']} / {nome}: {erro}")
            resultado[nome] = {"erro": str(erro)}

    return resultado


def main(argv: list[str] | None = None) -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True)
    parser.add_argument("--chroma-path", type=Path, default=None)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--gemini-delay-s", type=float, default=GEMINI_DELAY_S_PADRAO)
    parser.add_argument("--max-gemini-calls", type=int, default=MAX_GEMINI_CALLS_PADRAO)
    argumentos = parser.parse_args(argv)

    if argumentos.chroma_path:
        ChromaDBClient.configure(path=argumentos.chroma_path)

    casos = json.loads(argumentos.cases.read_text(encoding="utf-8"))

    colecao_candidata = ChromaDBClient._get_strict_collection(
        argumentos.collection, with_embedding_function=True
    )

    logger.warning(
        f"Apontando RetrievalClient para a candidata {argumentos.collection!r} "
        f"({colecao_candidata.count()} chunks) — só neste processo. "
        f"Teto de {argumentos.max_gemini_calls} chamadas ao Gemini, "
        f"{argumentos.gemini_delay_s}s entre cada uma."
    )

    ChromaDBClient.get_collection = classmethod(lambda cls: colecao_candidata)

    contador_gemini = [0]
    resultados = []

    for caso in casos:
        resultados.append(
            medir_caso(caso, contador_gemini, argumentos.max_gemini_calls, argumentos.gemini_delay_s)
        )

    argumentos.output.write_text(
        json.dumps(
            {
                "collection": argumentos.collection,
                "gemini_calls_used": contador_gemini[0],
                "cases": resultados,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    logger.info(
        f"Gravado em {argumentos.output} "
        f"({contador_gemini[0]} chamadas ao Gemini usadas)"
    )


if __name__ == "__main__":
    main()
