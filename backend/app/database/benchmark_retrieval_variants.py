"""Benchmark reproduzível das partes da recuperação e de receitas de chunks.

Executa contra coleção candidata, sem alterar o ponteiro ativo. Também pode
criar coleções efêmeras em outro diretório Chroma para comparar overlap.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import time
from pathlib import Path

from app.clients.reranker_client import RerankerClient
from app.clients.retrieval_client import RetrievalClient
from app.database.chroma_client import ChromaDBClient
from app.database.document_processing import (
    chunk_metadata,
    load_embedding_tokenizer,
    process_document,
)
from app.database.ingest_documents import (
    _upsert_batches,
    prepare_ingestion,
)


VARIANTS = ("vector_only", "rerank_only", "routing_only", "production")


def expected_topics(case: dict) -> set[str]:
    return {
        item.strip()
        for item in case.get("expected_topics", "").split(";")
        if item.strip()
    }


def reciprocal_rank(topics: list[str], expected: set[str]) -> float:
    for index, topic in enumerate(topics, 1):
        if topic in expected:
            return 1 / index
    return 0.0


def summarize(rows: list[dict], thresholds: list[float]) -> dict:
    summary: dict[str, dict] = {}
    for variant in VARIANTS:
        relevant = [row for row in rows if row["expected_topics"]]
        hits_1 = [row["variants"][variant]["hit_at_1"] for row in relevant]
        hits_5 = [row["variants"][variant]["hit_at_5"] for row in relevant]
        ranks = [row["variants"][variant]["reciprocal_rank"] for row in relevant]
        latencies = [row["variants"][variant]["seconds"] for row in rows]
        summary[variant] = {
            "cases": len(rows),
            "precision_at_1": sum(hits_1) / len(hits_1) if hits_1 else None,
            "recall_at_5": sum(hits_5) / len(hits_5) if hits_5 else None,
            "mrr": sum(ranks) / len(ranks) if ranks else None,
            "latency_ms_median": round(1000 * statistics.median(latencies), 3),
            "latency_ms_p95": round(
                1000 * sorted(latencies)[max(0, int(len(latencies) * .95) - 1)], 3
            ),
        }

    production = [row["variants"]["production"] for row in rows]
    summary["production"]["thresholds"] = {
        str(threshold): {
            "cases_with_context": sum(
                any(score >= threshold for score in item["context_scores"])
                for item in production
            ),
            "correct_topic_in_context": sum(
                any(
                    topic in set(row["expected_topics"]) and score >= threshold
                    for topic, score in zip(
                        row["variants"]["production"]["topics"],
                        row["variants"]["production"]["context_scores"],
                    )
                )
                for row in rows
            ),
        }
        for threshold in thresholds
    }
    return summary


def run_variant(question: str, variant: str) -> dict:
    use_routing = variant in {"routing_only", "production"}
    use_reranker = variant in {"rerank_only", "production"}
    started = time.perf_counter()
    documents = RetrievalClient.retrieve(
        [question], routing_query=question if use_routing else None
    )
    if use_reranker:
        documents = RerankerClient.rerank(
            [question], documents, eligibility_query=question
        )
    else:
        documents = documents[:5]
    seconds = time.perf_counter() - started
    topics = [document.topic for document in documents]
    scores = [round(document.score, 6) for document in documents]
    context_scores = [
        round(document.ranking_score if document.ranking_score is not None else document.score, 6)
        for document in documents
    ]
    return {
        "topics": topics,
        "chunk_ids": [document.chunk_id for document in documents],
        "scores": scores,
        "context_scores": context_scores,
        "seconds": round(seconds, 6),
    }


def evaluate(collection, cases: list[dict], thresholds: list[float]) -> dict:
    ChromaDBClient.get_collection = classmethod(lambda cls: collection)
    rows = []
    for index, case in enumerate(cases, 1):
        expected = expected_topics(case)
        variants = {}
        for variant in VARIANTS:
            result = run_variant(case["text"], variant)
            result["hit_at_1"] = bool(result["topics"] and result["topics"][0] in expected)
            result["hit_at_5"] = any(topic in expected for topic in result["topics"][:5])
            result["reciprocal_rank"] = reciprocal_rank(result["topics"][:5], expected)
            variants[variant] = result
        rows.append({
            "id": case["id"],
            "text": case["text"],
            "expected_topics": sorted(expected),
            "variants": variants,
        })
        print(f"[{index}/{len(cases)}] {case['id']}", flush=True)
    return {"rows": rows, "summary": summarize(rows, thresholds)}


def build_ephemeral_collection(path: Path, overlap: int, target: int):
    ChromaDBClient.configure(path=path)
    client = ChromaDBClient.get_client()
    name = f"benchmark_overlap_{overlap}"
    try:
        client.delete_collection(name)
    except Exception:
        pass
    collection = client.create_collection(
        name=name,
        embedding_function=ChromaDBClient._get_embedding_function(),
        metadata={"hnsw:space": "cosine", "benchmark": True},
    )
    prepared = prepare_ingestion(profile="experimental")
    tokenizer = load_embedding_tokenizer()
    total = 0
    for item in prepared.documents:
        processed = process_document(
            item.path,
            tokenizer=tokenizer,
            target_tokens=target,
            overlap_tokens=overlap,
        )
        ids, documents, metadatas = [], [], []
        for chunk_index, chunk in enumerate(processed.report.chunks):
            identity = f"overlap={overlap}:{item.relative_path}:{chunk.page_start}:{chunk_index}"
            ids.append(hashlib.sha256(identity.encode()).hexdigest())
            documents.append(chunk.text)
            metadatas.append(chunk_metadata(
                processed.metadata, chunk, item.relative_path,
                item.path.suffix.lower(), chunk_index,
            ))
        _upsert_batches(collection, ids, documents, metadatas)
        total += len(ids)
    return collection, total, len(prepared.documents)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection")
    parser.add_argument("--chroma-path", type=Path, default=Path("/app/chroma_db"))
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--thresholds", default="0.60,0.65,0.70,0.72,0.75")
    parser.add_argument("--overlap", type=int)
    parser.add_argument("--target", type=int, default=96)
    parser.add_argument("--temporary-chroma-path", type=Path)
    args = parser.parse_args()

    with args.cases.open(encoding="utf-8", newline="") as source:
        cases = list(csv.DictReader(source))
    if args.limit:
        cases = cases[:args.limit]
    if not cases:
        parser.error("o arquivo de casos está vazio após os filtros")
    thresholds = [float(item) for item in args.thresholds.split(",")]

    if args.overlap is not None:
        if not args.temporary_chroma_path:
            parser.error("--overlap exige --temporary-chroma-path")
        collection, chunk_count, document_count = build_ephemeral_collection(
            args.temporary_chroma_path, args.overlap, args.target
        )
        identity = {"kind": "ephemeral", "overlap": args.overlap, "target": args.target}
    else:
        if not args.collection:
            parser.error("informe --collection ou --overlap")
        ChromaDBClient.configure(path=args.chroma_path)
        collection = ChromaDBClient._get_strict_collection(
            args.collection, with_embedding_function=True
        )
        chunk_count, document_count = collection.count(), None
        identity = {"kind": "candidate", "name": args.collection}

    result = {
        "schema_version": 1,
        "collection": identity,
        "chunk_count": chunk_count,
        "document_count": document_count,
        "case_count": len(cases),
        "thresholds": thresholds,
        **evaluate(collection, cases, thresholds),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
