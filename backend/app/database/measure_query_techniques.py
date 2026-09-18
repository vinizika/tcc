"""
Mede o efeito de reescrita, multi-query e HyDE na recuperação, contra uma
coleção **candidata** (staging) do ChromaDB — sem tocar o ponteiro ativo nem
a rota `POST /search/`.

Existe porque as três técnicas de consulta do trilho B1 nunca puderam ser
medidas isoladamente ([B-09](../../../evidencias/backlog.md#b-09)): a régua
de recuperação sempre rodou contra `POST /search/`, que só enxerga a coleção
ativa — e até 16/09 a ativa sempre teve 0 chunks, então não havia nada para
medir. Os três lotes experimentais do trilho A
(`evidencias/vini/2026-09-1{4,5,6}-*`) deixaram coleções candidatas em
staging, com conteúdo real, prontas para consulta direta.

Cinco arranjos de consulta, por caso:

- `sem_consulta`: o relato cru, sem nenhuma transformação — a linha de base;
- `reescrita`: só `QueryClient.rewrite()`;
- `multi_query`: reescrita + Multi-Query, **do jeito que o pipeline roda
  hoje** — a reescrita some da lista quando há variações (é o
  [B-10](../../../evidencias/backlog.md#b-10));
- `fundido`: `[reescrita] + variações`, sem duplicatas — o candidato a
  correção do B-10, para comparar lado a lado com o comportamento atual;
- `pipeline_completo`: multi-query + HyDE, a configuração padrão do `.env`
  hoje (`QUERY_REWRITING_ENABLED`/`MULTI_QUERY_ENABLED`/`HYDE_ENABLED=True`).

Cada arranjo chama `RetrievalClient.retrieve()` — o mesmo caminho de
produção, corte de relevância incluído — só que apontado para a coleção
candidata em vez da ativa. Não escreve nada; não altera nenhuma coleção.

Roda **dentro do container** (precisa do ChromaDB e do Ollama já
carregados):

    docker compose exec -T backend python -m app.database.measure_query_techniques \\
        --collection <nome-da-candidata> --cases /tmp/cases.json --output /tmp/resultado.json

`--cases` é uma lista JSON de objetos `{"id", "text", "expected_topics"}` —
`expected_topics` é uma string com os tópicos aceitáveis separados por `;`,
no mesmo formato de `data/retrieval/cases.csv`.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from app.clients.query_client import QueryClient
from app.clients.retrieval_client import RetrievalClient
from app.database.chroma_client import ChromaDBClient
from app.core.logger import setup_logger

logger = setup_logger("MeasureQueryTechniques")


def montar_arranjos(relato: str) -> dict[str, list[str]]:
    """
    Gera as consultas dos cinco arranjos para um relato, chamando o
    QueryClient uma vez por etapa (reescrita, variações, HyDE) e
    reaproveitando entre arranjos — mesmo custo de chamadas que o pipeline
    real faria com tudo ligado.
    """

    reescrita = (QueryClient.rewrite(relato) or "").strip() or relato

    variacoes = [
        variacao.strip()
        for variacao in QueryClient.generate_queries(reescrita)
        if variacao and variacao.strip()
    ]

    documento_hipotetico = (
        QueryClient.generate_hypothetical_document(reescrita) or ""
    ).strip()

    multi_query = variacoes if variacoes else [reescrita]

    fundido: list[str] = []
    for consulta in [reescrita, *variacoes]:
        if consulta and consulta not in fundido:
            fundido.append(consulta)

    pipeline_completo = list(multi_query)
    if documento_hipotetico:
        pipeline_completo.append(documento_hipotetico)

    return {
        "sem_consulta": [relato],
        "reescrita": [reescrita],
        "multi_query": multi_query,
        "fundido": fundido,
        "pipeline_completo": pipeline_completo,
    }


def medir_caso(caso: dict) -> dict:

    relato = caso["text"]
    arranjos = montar_arranjos(relato)

    resultado_por_arranjo = {}

    for nome_arranjo, consultas in arranjos.items():

        inicio = time.perf_counter()
        recuperados = RetrievalClient.retrieve(consultas)
        segundos = time.perf_counter() - inicio

        resultado_por_arranjo[nome_arranjo] = {
            "queries": consultas,
            "topics": [documento.topic for documento in recuperados],
            "scores": [
                round(documento.score, 6) for documento in recuperados
            ],
            "chunk_ids": [documento.chunk_id for documento in recuperados],
            "seconds": round(segundos, 3),
        }

        logger.info(
            f"{caso['id']} / {nome_arranjo}: "
            f"{[documento.topic for documento in recuperados]}"
        )

    return {
        "id": caso["id"],
        "expected_topics": caso.get("expected_topics", ""),
        "arranjos": resultado_por_arranjo,
    }


def main(argv: list[str] | None = None) -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--chroma-path",
        type=Path,
        default=None,
        help=(
            "Sobrescreve settings.CHROMA_PATH. Existe porque, em 16-17/09, "
            "os snapshots versionados dos lotes experimentais do trilho A "
            "foram gravados em backend/chroma_db/, e não em "
            "backend/data/chroma/, que é o que o backend real lê — as duas "
            "coisas divergem hoje (ver evidência desta rodada)."
        ),
    )
    argumentos = parser.parse_args(argv)

    if argumentos.chroma_path:
        ChromaDBClient.configure(path=argumentos.chroma_path)

    casos = json.loads(argumentos.cases.read_text(encoding="utf-8"))

    colecao_candidata = ChromaDBClient._get_strict_collection(
        argumentos.collection,
        with_embedding_function=True,
    )

    logger.warning(
        f"Apontando RetrievalClient para a candidata "
        f"{argumentos.collection!r} ({colecao_candidata.count()} chunks) — "
        "só para este processo; o ponteiro ativo não é tocado."
    )

    # Monkeypatch só neste processo de vida curta: RetrievalClient sempre
    # busca via ChromaDBClient.get_collection(), e é a única forma de
    # reaproveitar o caminho de produção (merge de multi-query, corte de
    # relevância) sem reimplementá-lo aqui.
    ChromaDBClient.get_collection = classmethod(
        lambda cls: colecao_candidata
    )

    resultados = [medir_caso(caso) for caso in casos]

    argumentos.output.write_text(
        json.dumps(
            {
                "collection": argumentos.collection,
                "chunk_count": colecao_candidata.count(),
                "cases": resultados,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    logger.info(f"Gravado em {argumentos.output}")


if __name__ == "__main__":
    main()
