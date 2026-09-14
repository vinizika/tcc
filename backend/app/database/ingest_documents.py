"""CLI auditável para ingestão versionada das fontes veterinárias."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from app.core.logger import setup_logger
from app.database.document_processing import (
    ProcessedDocument,
    ProcessingReport,
    Tokenizer,
    chunk_metadata,
    load_embedding_tokenizer,
    load_metadata,
    process_document,
)
from app.database.embedding_config import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MAX_TOKENS,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_REVISION,
    embedding_recipe,
    embedding_recipe_sha256,
)


logger = setup_logger("DocumentIngestion")

BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]
REPOSITORY_DIRECTORY = BACKEND_DIRECTORY.parent
DOCUMENTS_DIRECTORY = BACKEND_DIRECTORY / "data" / "documents"
TOPIC_MAP_PATH = REPOSITORY_DIRECTORY / "data" / "curadoria" / "mapa-de-assuntos.csv"
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
UPSERT_BATCH_SIZE = 100
INGESTION_PROFILES = {"curated", "experimental", "legacy_rechunk"}
CANONICAL_SPECIES = {"dog", "cat", "dog_and_cat"}
CURATED_DOCUMENT_TYPES = {
    "owner_guidance",
    "peer_reviewed_article",
    "peer_reviewed_review",
    "clinical_guideline",
}
CURATED_VALIDATION_STATUSES = {
    "approved_by_specialist",
    "approved_with_reservations",
}


class IngestionValidationError(ValueError):
    """A seleção documental falhou antes de qualquer acesso ao Chroma."""


@dataclass(frozen=True)
class PreparedDocument:
    path: Path
    relative_path: str
    source_sha256: str
    sidecar_sha256: str
    processed: ProcessedDocument
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PreparedIngestion:
    profile: str
    documents: tuple[PreparedDocument, ...]
    source_set_sha256: str
    warning_count: int


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def create_chunk_id(
    relative_path: str,
    page_number: int,
    chunk_index: int,
) -> str:
    """Gera ID estável para o mesmo recorte determinístico do documento."""

    identifier = f"{relative_path}:{page_number}:{chunk_index}"
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def clear_collection(collection) -> None:
    """Compatibilidade administrativa; nunca usada na ingestão versionada."""

    removed_documents = 0
    while collection.count() > 0:
        existing_records = collection.get(limit=1000)
        existing_ids = existing_records.get("ids", [])
        if not existing_ids:
            break
        collection.delete(ids=existing_ids)
        removed_documents += len(existing_ids)
    logger.info("%s registros antigos removidos", removed_documents)


def _document_paths() -> list[Path]:
    if not DOCUMENTS_DIRECTORY.exists():
        return []
    return sorted(
        document_path
        for document_path in DOCUMENTS_DIRECTORY.rglob("*")
        if document_path.is_file()
        and document_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def resolve_inspection_path(file_name: str) -> Path:
    """Resolve ``--file`` sem permitir leitura fora da pasta documental."""

    documents_root = DOCUMENTS_DIRECTORY.resolve()
    candidate = (DOCUMENTS_DIRECTORY / file_name).resolve()
    if candidate != documents_root and documents_root not in candidate.parents:
        raise ValueError("--file deve apontar para a pasta de documentos.")
    if not candidate.is_file():
        raise FileNotFoundError(f"Documento não encontrado: {file_name}")
    if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato não suportado: {candidate.suffix}")
    return candidate


def _unique(values: tuple[str, ...]) -> str:
    return ", ".join(dict.fromkeys(values)) or "nenhuma"


def log_processing_report(
    report: ProcessingReport,
    *,
    inspect_chunks: bool = False,
) -> None:
    token_counts = [chunk.token_count for chunk in report.chunks]
    logger.info("Documento: %s", report.document_name)
    if report.extraction_statistics:
        statistics_report = report.extraction_statistics
        logger.info("Extrator: %s", statistics_report.extractor)
        logger.info(
            "Layout: %s página(s) multicoluna; %s bloco(s) removido(s)",
            statistics_report.multi_column_pages,
            statistics_report.blocks_removed,
        )
        if inspect_chunks:
            for warning in statistics_report.warnings:
                logger.warning("Aviso de extração: %s", warning)
    logger.info("Páginas extraídas: %s", report.pages_extracted)
    logger.info(
        "Seções detectadas (%s): %s",
        len(dict.fromkeys(report.detected_sections)),
        _unique(report.detected_sections),
    )
    logger.info(
        "Seções indexadas (%s): %s",
        len(dict.fromkeys(report.included_sections)),
        _unique(report.included_sections),
    )
    logger.info("Chunks produzidos: %s", len(report.chunks))
    if token_counts:
        logger.info(
            "Tamanho dos chunks: mínimo=%s, máximo=%s tokens",
            min(token_counts),
            max(token_counts),
        )
    if inspect_chunks:
        for chunk_index, chunk in enumerate(report.chunks):
            preview = " ".join((chunk.body or chunk.text).split())[:180]
            logger.info(
                "Chunk %s | %s tokens | página(s) %s-%s | seção=%s | %s",
                chunk_index,
                chunk.token_count,
                chunk.page_start,
                chunk.page_end,
                chunk.section,
                preview,
            )


def ingest_document(
    collection,
    document_path: Path,
    tokenizer: Tokenizer | None = None,
) -> int:
    """API legada: substitui um único documento em uma coleção fornecida.

    O ciclo seguro não usa esta função; ela permanece para integrações antigas
    que já entregam explicitamente uma coleção.
    """

    relative_path = str(document_path.relative_to(DOCUMENTS_DIRECTORY))
    processed = process_document(document_path, tokenizer=tokenizer)
    report = processed.report
    log_processing_report(report)
    if not report.chunks:
        raise ValueError(
            f"Nenhum texto utilizável foi encontrado em {document_path.name}."
        )

    ids, documents, metadatas = _materialize_document(
        PreparedDocument(
            path=document_path,
            relative_path=relative_path,
            source_sha256=_sha256_file(document_path),
            sidecar_sha256=(
                _sha256_file(document_path.with_suffix(".json"))
                if document_path.with_suffix(".json").exists()
                else ""
            ),
            processed=processed,
            warnings=(),
        )
    )
    collection.delete(where={"source_file": relative_path})
    _upsert_batches(collection, ids, documents, metadatas)
    logger.info("%s: %s chunks inseridos", document_path.name, len(documents))
    return len(documents)


def inspect_documents(
    document_path: Path | None = None,
    tokenizer: Tokenizer | None = None,
) -> list[ProcessingReport]:
    """Executa o processamento sem importar ou alterar o ChromaDB."""

    paths = [document_path] if document_path else _document_paths()
    if not paths:
        logger.warning("Nenhum PDF ou TXT encontrado em %s", DOCUMENTS_DIRECTORY)
        return []
    active_tokenizer = tokenizer or load_embedding_tokenizer()
    reports: list[ProcessingReport] = []
    for path in paths:
        processed = process_document(path, tokenizer=active_tokenizer)
        reports.append(processed.report)
        log_processing_report(processed.report, inspect_chunks=True)
    logger.info("Inspeção concluída: nenhum registro foi escrito no ChromaDB.")
    return reports


def _known_topics() -> set[str]:
    if not TOPIC_MAP_PATH.exists():
        return set()
    with TOPIC_MAP_PATH.open("r", encoding="utf-8", newline="") as map_file:
        return {
            row["id"].strip()
            for row in csv.DictReader(map_file)
            if row.get("id", "").strip()
        }


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _curated_errors(path: Path, metadata: dict, known_topics: set[str]) -> list[str]:
    errors: list[str] = []
    sidecar_path = path.with_suffix(".json")
    if not sidecar_path.exists():
        return ["sidecar JSON ausente"]

    if metadata.get("ingestion_scope") != "curated":
        errors.append("ingestion_scope deve ser curated")
    if metadata.get("document_type") not in CURATED_DOCUMENT_TYPES:
        errors.append("document_type não é uma fonte original aceita")
    if metadata.get("validation_status") not in CURATED_VALIDATION_STATUSES:
        errors.append("validation_status não registra aprovação especialista")
    if metadata.get("species") not in CANONICAL_SPECIES:
        errors.append("species fora do vocabulário canônico")
    if metadata.get("topic") not in known_topics:
        errors.append("topic não existe no mapa de assuntos")
    for field_name in ("title", "source", "source_url"):
        if not _nonempty(metadata.get(field_name)):
            errors.append(f"{field_name} obrigatório")

    expected_hash = metadata.get("captured_sha256") or metadata.get("sha256")
    if not _nonempty(expected_hash):
        errors.append("hash SHA-256 da fonte ausente")
    elif expected_hash != _sha256_file(path):
        errors.append("hash SHA-256 da fonte divergente")

    specialist = metadata.get("specialist")
    if not isinstance(specialist, dict):
        errors.append("specialist deve ser objeto")
    else:
        for field_name in ("verdict", "name", "date"):
            if not _nonempty(specialist.get(field_name)):
                errors.append(f"specialist.{field_name} obrigatório")
        expected_verdicts = {
            "approved",
            "approved_by_specialist",
            "approved_with_reservations",
        }
        if (
            _nonempty(specialist.get("verdict"))
            and specialist["verdict"] not in expected_verdicts
        ):
            errors.append("specialist.verdict não aprova a fonte")

    rights = metadata.get("rights")
    if not isinstance(rights, dict):
        errors.append("rights deve ser objeto")
    else:
        if rights.get("status") not in {"approved", "allowed"}:
            errors.append("rights.status não autoriza uso")
        for field_name in ("basis", "checked_by", "date"):
            if not _nonempty(rights.get(field_name)):
                errors.append(f"rights.{field_name} obrigatório")

    indexing = metadata.get("indexing") or {}
    if path.suffix.lower() == ".pdf":
        include_sections = indexing.get("include_sections")
        if not isinstance(include_sections, list) or not include_sections:
            errors.append("PDF curado exige indexing.include_sections")
        if indexing.get("extraction_reviewed") is not True:
            errors.append("PDF curado exige indexing.extraction_reviewed=true")
    return errors


def _profile_paths(profile: str, paths: Iterable[Path]) -> tuple[list[Path], list[str]]:
    if profile not in INGESTION_PROFILES:
        raise IngestionValidationError(f"Perfil desconhecido: {profile}")
    selected: list[Path] = []
    rejection_messages: list[str] = []
    known_topics = _known_topics() if profile == "curated" else set()

    for path in paths:
        try:
            metadata = load_metadata(path)
        except Exception as error:
            rejection_messages.append(f"{path.name}: sidecar inválido: {error}")
            continue
        if profile == "legacy_rechunk":
            if metadata.get("document_type") == "synthetic_protocol":
                selected.append(path)
            continue
        if profile == "experimental":
            selected.append(path)
            continue
        errors = _curated_errors(path, metadata, known_topics)
        if errors:
            rejection_messages.append(f"{path.name}: " + "; ".join(errors))
        else:
            selected.append(path)

    if not selected:
        details = "\n".join(f"- {message}" for message in rejection_messages)
        raise IngestionValidationError(
            f"Nenhum documento elegível para o perfil {profile}."
            + (f"\n{details}" if details else "")
        )
    if profile == "curated" and rejection_messages:
        details = "\n".join(f"- {message}" for message in rejection_messages)
        raise IngestionValidationError(
            "O perfil curated exige que todos os candidatos sejam elegíveis.\n"
            + details
        )
    return selected, rejection_messages


def _section_key(value: str) -> str:
    import re
    import unicodedata

    decomposed = unicodedata.normalize("NFKD", value or "")
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", plain.casefold())


def _post_processing_curated_errors(
    path: Path,
    processed: ProcessedDocument,
) -> list[str]:
    errors: list[str] = []
    report = processed.report
    configured = (
        (processed.metadata.get("indexing") or {}).get("include_sections") or []
    )
    detected = {_section_key(value) for value in report.detected_sections}
    missing = [value for value in configured if _section_key(value) not in detected]
    if missing:
        errors.append("seções não detectadas: " + ", ".join(missing))
    if report.used_section_fallback:
        errors.append("fallback de seção não é permitido")
    if report.corrupted_openers_removed:
        errors.append("fragmento corrompido detectado")
    if not report.chunks:
        errors.append("nenhum chunk válido")
    if any(chunk.token_count > EMBEDDING_MAX_TOKENS for chunk in report.chunks):
        errors.append("chunk excede o limite do embedding")
    return errors


def prepare_ingestion(
    *,
    profile: str,
    paths: Iterable[Path] | None = None,
    tokenizer: Tokenizer | None = None,
) -> PreparedIngestion:
    """Valida e processa tudo antes de importar/abrir o ChromaDB."""

    selected, policy_rejections = _profile_paths(
        profile, list(paths) if paths is not None else _document_paths()
    )
    active_tokenizer = tokenizer or load_embedding_tokenizer()
    prepared: list[PreparedDocument] = []

    for path in selected:
        processed = process_document(path, tokenizer=active_tokenizer)
        if not processed.report.chunks:
            raise IngestionValidationError(
                f"{path.name}: nenhum texto utilizável após filtragem."
            )
        if profile == "curated":
            errors = _post_processing_curated_errors(path, processed)
            if errors:
                raise IngestionValidationError(
                    f"{path.name}: " + "; ".join(errors)
                )

        warnings: list[str] = []
        metadata = processed.metadata
        if metadata.get("validation_status") not in CURATED_VALIDATION_STATUSES:
            warnings.append("documento sem aprovação clínica local")
        if metadata.get("ingestion_scope") != "curated":
            warnings.append("documento restrito a uso experimental")
        if processed.report.used_section_fallback:
            warnings.append("estrutura de seção em fallback")
        if processed.report.fallback_splits:
            warnings.append(
                f"{processed.report.fallback_splits} divisão(ões) lexical(is)"
            )
        if processed.report.corrupted_openers_removed:
            warnings.append(
                f"{processed.report.corrupted_openers_removed} fragmento(s) corrompido(s)"
            )
        sidecar_path = path.with_suffix(".json")
        prepared.append(
            PreparedDocument(
                path=path,
                relative_path=str(path.relative_to(DOCUMENTS_DIRECTORY)),
                source_sha256=_sha256_file(path),
                sidecar_sha256=(
                    _sha256_file(sidecar_path) if sidecar_path.exists() else ""
                ),
                processed=processed,
                warnings=tuple(warnings),
            )
        )

    source_identity = [
        {
            "path": item.relative_path,
            "source_sha256": item.source_sha256,
            "sidecar_sha256": item.sidecar_sha256,
        }
        for item in prepared
    ]
    source_set_sha256 = _sha256_bytes(
        _canonical_json(source_identity).encode("utf-8")
    )
    return PreparedIngestion(
        profile=profile,
        documents=tuple(prepared),
        source_set_sha256=source_set_sha256,
        warning_count=sum(len(item.warnings) for item in prepared)
        + len(policy_rejections),
    )


def _materialize_document(
    prepared: PreparedDocument,
) -> tuple[list[str], list[str], list[dict]]:
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    for chunk_index, chunk in enumerate(prepared.processed.report.chunks):
        ids.append(
            create_chunk_id(
                prepared.relative_path,
                chunk.page_start,
                chunk_index,
            )
        )
        documents.append(chunk.text)
        metadatas.append(
            chunk_metadata(
                prepared.processed.metadata,
                chunk,
                prepared.relative_path,
                prepared.path.suffix.lower(),
                chunk_index,
            )
        )
    return ids, documents, metadatas


def _upsert_batches(
    collection,
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    for batch_start in range(0, len(documents), UPSERT_BATCH_SIZE):
        batch_end = batch_start + UPSERT_BATCH_SIZE
        collection.upsert(
            ids=ids[batch_start:batch_end],
            documents=documents[batch_start:batch_end],
            metadatas=metadatas[batch_start:batch_end],
        )


def _collection_name(base_name: str, prepared: PreparedIngestion) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{base_name}__{timestamp}__{prepared.source_set_sha256[:8]}"


def _build_manifest(
    collection_name: str,
    prepared: PreparedIngestion,
    *,
    identifiers: list[str],
    documents: list[str],
    metadatas: list[dict],
) -> dict:
    from app.database.chroma_client import (
        chunk_content_sha256,
        chunk_ids_sha256,
    )

    token_counts = [
        chunk.token_count
        for document in prepared.documents
        for chunk in document.processed.report.chunks
    ]
    topic_counts = Counter(metadata.get("topic", "") for metadata in metadatas)
    species_counts = Counter(metadata.get("species", "") for metadata in metadatas)
    validation_counts = Counter(
        metadata.get("validation_status", "") for metadata in metadatas
    )
    return {
        "schema_version": 1,
        "collection_name": collection_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile": prepared.profile,
        "embedding": {
            "model": EMBEDDING_MODEL_NAME,
            "revision": EMBEDDING_MODEL_REVISION,
            "dimensions": EMBEDDING_DIMENSIONS,
        },
        "chunking": {
            **embedding_recipe(),
            "recipe_sha256": embedding_recipe_sha256(),
        },
        "sources": {
            "document_count": len(prepared.documents),
            "source_set_sha256": prepared.source_set_sha256,
            "documents": [
                {
                    "path": item.relative_path,
                    "source_sha256": item.source_sha256,
                    "sidecar_sha256": item.sidecar_sha256,
                    "chunk_count": len(item.processed.report.chunks),
                }
                for item in prepared.documents
            ],
        },
        "chunks": {
            "count": len(identifiers),
            "ids_sha256": chunk_ids_sha256(identifiers),
            "content_sha256": chunk_content_sha256(
                identifiers, documents, metadatas
            ),
            "tokens": {
                "min": min(token_counts),
                "mean": round(statistics.mean(token_counts), 3),
                "median": statistics.median(token_counts),
                "max": max(token_counts),
            },
        },
        "quality": {
            "warning_count": prepared.warning_count,
            "fallback_count": sum(
                item.processed.report.fallback_splits
                for item in prepared.documents
            ),
            "corrupt_document_count": sum(
                bool(item.processed.report.corrupted_openers_removed)
                for item in prepared.documents
            ),
            "topic_counts": dict(sorted(topic_counts.items())),
            "species_counts": dict(sorted(species_counts.items())),
            "validation_status_counts": dict(sorted(validation_counts.items())),
        },
    }


def stage_ingestion(
    prepared: PreparedIngestion,
    *,
    activate: bool = False,
) -> dict:
    """Materializa candidata; ativação é uma segunda etapa explícita."""

    from app.database.chroma_client import ChromaDBClient, atomic_write_json

    collection_name = _collection_name(
        ChromaDBClient.base_collection_name(), prepared
    )
    collection = ChromaDBClient.create_staging_collection(
        collection_name, profile=prepared.profile
    )
    all_ids: list[str] = []
    all_documents: list[str] = []
    all_metadatas: list[dict] = []
    try:
        for document in prepared.documents:
            ids, documents, metadatas = _materialize_document(document)
            _upsert_batches(collection, ids, documents, metadatas)
            all_ids.extend(ids)
            all_documents.extend(documents)
            all_metadatas.extend(metadatas)

        manifest = _build_manifest(
            collection_name,
            prepared,
            identifiers=all_ids,
            documents=all_documents,
            metadatas=all_metadatas,
        )
        manifest_sha256 = ChromaDBClient.write_manifest(
            collection_name, manifest
        )
        ChromaDBClient.validate_collection_integrity(
            collection_name, manifest=manifest
        )
    except BaseException:
        # Uma candidata incompleta jamais vira ativa. Ela é removida para não
        # parecer uma versão válida em listagens administrativas.
        ChromaDBClient.get_client().delete_collection(collection_name)
        ChromaDBClient.manifest_path(collection_name).unlink(missing_ok=True)
        raise

    pointer = (
        ChromaDBClient.activate_collection(collection_name) if activate else None
    )
    receipt = {
        "schema_version": 1,
        "collection_name": collection_name,
        "profile": prepared.profile,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "manifest_sha256": manifest_sha256,
        "chunk_count": len(all_ids),
        "activated": bool(pointer),
        "active_pointer": pointer,
    }
    receipt_path = (
        ChromaDBClient.chroma_path()
        / "receipts"
        / f"{collection_name}.json"
    )
    atomic_write_json(receipt_path, receipt)
    return {"manifest": manifest, "receipt": receipt, "receipt_path": receipt_path}


def ingest_documents(
    reset_collection: bool = False,
    *,
    profile: str = "curated",
    activate: bool = False,
    tokenizer: Tokenizer | None = None,
) -> dict:
    """API compatível que agora executa staging seguro em vez de sobrescrever."""

    if reset_collection:
        raise IngestionValidationError(
            "--reset foi removido: use staging e ativação explícita."
        )
    prepared = prepare_ingestion(profile=profile, tokenizer=tokenizer)
    return stage_ingestion(prepared, activate=activate)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Processa documentos em uma coleção Chroma versionada."
    )
    parser.add_argument(
        "--profile",
        choices=sorted(INGESTION_PROFILES),
        default="curated",
        help="Política de seleção documental (padrão seguro: curated).",
    )
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Ativa a candidata somente depois de validar manifesto e hashes.",
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="Explicita o padrão: cria candidata sem trocar a coleção ativa.",
    )
    parser.add_argument(
        "--inspect",
        "--dry-run",
        dest="inspect",
        action="store_true",
        help="Mostra seções/chunks sem abrir ou alterar o ChromaDB.",
    )
    parser.add_argument(
        "--file",
        help="No modo --inspect, processa somente este arquivo da pasta.",
    )
    parser.add_argument(
        "--rollback",
        nargs="?",
        const="previous",
        metavar="COLLECTION",
        help="Reativa a coleção indicada ou a anterior registrada no ponteiro.",
    )
    parser.add_argument(
        "--list-collections",
        action="store_true",
        help="Lista coleções versionadas e manifestos.",
    )
    # Mantido apenas para produzir erro acionável em automações antigas.
    parser.add_argument("--reset", action="store_true", help=argparse.SUPPRESS)
    return parser


def main() -> None:
    parser = build_argument_parser()
    arguments = parser.parse_args()
    if arguments.file and not arguments.inspect:
        parser.error("--file só pode ser usado com --inspect.")
    if arguments.activate and arguments.stage_only:
        parser.error("--activate e --stage-only são mutuamente exclusivos.")
    if arguments.reset:
        parser.error("--reset foi removido; use staging e --activate.")

    if arguments.rollback or arguments.list_collections:
        from app.database.chroma_client import ChromaDBClient
        if arguments.list_collections:
            print(json.dumps(
                ChromaDBClient.list_versioned_collections(),
                ensure_ascii=False,
                indent=2,
            ))
            return
        target = None if arguments.rollback == "previous" else arguments.rollback
        print(json.dumps(
            ChromaDBClient.rollback(target),
            ensure_ascii=False,
            indent=2,
        ))
        return

    if arguments.inspect:
        document_path = (
            resolve_inspection_path(arguments.file) if arguments.file else None
        )
        inspect_documents(document_path=document_path)
        return

    try:
        result = ingest_documents(
            profile=arguments.profile,
            activate=arguments.activate,
        )
    except IngestionValidationError as error:
        parser.error(str(error))
    print(json.dumps(
        {
            "manifest": result["manifest"],
            "receipt": result["receipt"],
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
