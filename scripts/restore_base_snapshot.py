"""
Restaura um retrato da base vetorial no ChromaDB.

Existe por causa do [B-37](../evidencias/backlog.md#b-37): a base de 18
trechos que sustenta as rodadas citadas até 05/09 não pode mais ser gerada a
partir do código, porque a receita de chunking mudou em 07/09. Sem um caminho
de volta, reproduzir uma daquelas rodadas seria impossível.

O retrato traz os vetores já calculados, então a restauração **não** baixa o
modelo de embedding nem depende da versão do ChromaDB que o gravou.

Este script escreve na coleção. Ele recusa rodar sobre uma coleção que já
tenha conteúdo, a menos que `--force` seja passado — apagar a base de alguém
por engano custaria uma reindexação e, pior, silenciosamente mudaria o que as
próximas rodadas medem.

Este script fala com o ChromaDB direto, então precisa rodar **dentro do
container** — e o Compose monta apenas `./backend`, não a raiz. Por isso o
comando leva as duas pastas de fora:

    docker run --rm \\
      -v "$PWD/backend:/app" -v "$PWD/scripts:/scripts" -v "$PWD/data:/data" \\
      -w /app -e PYTHONPATH=/app tcc-backend:latest \\
      python /scripts/restore_base_snapshot.py \\
        /data/evaluation/cited/base-2026-09-04-18-chunks/export.json

O `PYTHONPATH` é necessário porque o interpretador põe no caminho a pasta do
script (`/scripts`), e não o diretório de trabalho.

Pare o backend antes (`docker compose stop backend`): dois processos
escrevendo no mesmo SQLite é pedir corrupção.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


UPSERT_BATCH_SIZE = 100


def carregar(caminho: Path) -> dict:

    retrato = json.loads(caminho.read_text(encoding="utf-8"))

    registros = retrato.get("records") or []

    if not registros:
        raise SystemExit(f"{caminho} não tem registros.")

    faltando = [
        indice
        for indice, registro in enumerate(registros)
        if not registro.get("embedding")
    ]

    if faltando:
        raise SystemExit(
            f"{len(faltando)} registro(s) sem vetor. Restaurar sem os vetores "
            "recalcularia os embeddings com o modelo atual, e o retrato "
            "deixaria de ser o mesmo."
        )

    return retrato


def restaurar(retrato: dict, colecao, forcar: bool) -> None:

    existentes = colecao.count()

    if existentes and not forcar:
        raise SystemExit(
            f"A coleção já tem {existentes} registro(s).\n"
            "Restaurar apagaria a base atual e mudaria o que as próximas "
            "rodadas medem. Se é isso mesmo que você quer, repita com "
            "--force."
        )

    if existentes:
        print(f"Apagando {existentes} registro(s) da coleção atual...")

        while colecao.count() > 0:
            lote = colecao.get(limit=1000).get("ids") or []
            if not lote:
                break
            colecao.delete(ids=lote)

    registros = retrato["records"]

    ids = [registro["id"] for registro in registros]
    documentos = [registro["document"] for registro in registros]
    metadados = [registro["metadata"] for registro in registros]
    vetores = [registro["embedding"] for registro in registros]

    for inicio in range(0, len(ids), UPSERT_BATCH_SIZE):
        fim = inicio + UPSERT_BATCH_SIZE
        colecao.upsert(
            ids=ids[inicio:fim],
            documents=documentos[inicio:fim],
            metadatas=metadados[inicio:fim],
            embeddings=vetores[inicio:fim],
        )

    print(f"{len(ids)} trecho(s) restaurado(s). Coleção: {colecao.count()}.")


def conferir(retrato: dict) -> None:
    """
    Compara o retrato restaurado com os hashes que ele declara.

    É o que transforma "restaurei" em "restaurei a base certa": os mesmos
    hashes aparecem no `backend_fingerprint` das rodadas citadas.
    """

    from app.services.fingerprint_service import FingerprintService

    base = FingerprintService._base_vetorial()

    problemas = []

    for campo in ("chunk_ids_sha256", "content_sha256"):

        esperado = retrato.get(campo)
        obtido = base.get(campo)

        if esperado and esperado != obtido:
            problemas.append(f"  {campo}\n    retrato: {esperado}\n    agora  : {obtido}")

    if problemas:
        print("\nA base restaurada NÃO bate com o retrato:")
        print("\n".join(problemas))
        raise SystemExit(1)

    print("Hashes conferem com o retrato:")
    print(f"  chunk_ids_sha256: {base.get('chunk_ids_sha256')}")
    print(f"  content_sha256  : {base.get('content_sha256')}")


def main(argv: list[str] | None = None) -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Restaura um retrato da base vetorial (com os vetores já "
            "calculados) no ChromaDB."
        )
    )
    parser.add_argument(
        "retrato",
        type=Path,
        help=(
            "Caminho do export.json, como visto de dentro do container "
            "(ex.: /data/evaluation/cited/base-2026-09-04-18-chunks/"
            "export.json)."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Apaga a coleção atual antes de restaurar.",
    )

    argumentos = parser.parse_args(argv)

    if not argumentos.retrato.is_file():
        raise SystemExit(f"Retrato não encontrado: {argumentos.retrato}")

    retrato = carregar(argumentos.retrato)

    print(
        f"Retrato: {argumentos.retrato.name} · "
        f"{retrato['count']} trecho(s) · "
        f"{retrato.get('embedding_model')}"
    )

    # Import tardio: abrir a coleção carrega o modelo de embeddings, e
    # `--help` não precisa disso.
    from app.database.chroma_client import ChromaDBClient

    restaurar(retrato, ChromaDBClient.get_collection(), argumentos.force)
    conferir(retrato)


if __name__ == "__main__":
    main(sys.argv[1:])
