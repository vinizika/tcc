"""CLI e orquestração da ingestão das fontes veterinárias."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from app.core.logger import setup_logger
from app.database.document_processing import (
    ProcessingReport,
    Tokenizer,
    chunk_metadata,
    load_embedding_tokenizer,
    process_document,
)


logger = setup_logger("DocumentIngestion")

BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]
DOCUMENTS_DIRECTORY = BACKEND_DIRECTORY / "data" / "documents"
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
UPSERT_BATCH_SIZE = 100


def create_chunk_id(
    relative_path: str,
    page_number: int,
    chunk_index: int,
) -> str:
    """Gera ID estável para o mesmo recorte determinístico do documento."""

    identifier = f"{relative_path}:{page_number}:{chunk_index}"
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def clear_collection(collection) -> None:
    """Remove todos os registros da coleção atual."""

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
    DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

    return sorted(
        document_path
        for document_path in DOCUMENTS_DIRECTORY.rglob("*")
        if document_path.is_file()
        and document_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def resolve_inspection_path(file_name: str) -> Path:
    """Resolve `--file` sem permitir leitura fora da pasta de documentos."""

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
        statistics = report.extraction_statistics
        logger.info("Extrator: %s", statistics.extractor)
        logger.info(
            "Layout: %s página(s) multicoluna; %s bloco(s) removido(s)",
            statistics.multi_column_pages,
            statistics.blocks_removed,
        )

        if inspect_chunks:
            logger.info(
                "Extração: %s blocos; headers=%s; footers=%s; "
                "números de página=%s; captions=%s; editoriais=%s",
                statistics.blocks_extracted,
                statistics.headers_removed,
                statistics.footers_removed,
                statistics.page_numbers_removed,
                statistics.captions_removed,
                statistics.editorial_blocks_removed,
            )
            logger.info(
                "Unicode: %s símbolo(s) de grau recuperado(s); "
                "%s glifo(s) não mapeado(s)",
                statistics.degree_symbols_recovered,
                statistics.unmapped_glyphs,
            )
            for warning in statistics.warnings:
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
    logger.info(
        "Seções excluídas (%s): %s",
        len(dict.fromkeys(report.excluded_sections)),
        _unique(report.excluded_sections),
    )
    logger.info("Chunks produzidos: %s", len(report.chunks))
    if report.corrupted_openers_removed:
        logger.info(
            "Fragmentos iniciais corrompidos descartados: %s",
            report.corrupted_openers_removed,
        )

    if token_counts:
        logger.info(
            "Tamanho dos chunks: mínimo=%s, máximo=%s tokens",
            min(token_counts),
            max(token_counts),
        )

    if inspect_chunks:
        for chunk_index, chunk in enumerate(report.chunks):
            preview = " ".join(chunk.text.split())[:180]
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
    """Processa um documento e substitui seus chunks no ChromaDB."""

    relative_path = str(document_path.relative_to(DOCUMENTS_DIRECTORY))
    processed = process_document(document_path, tokenizer=tokenizer)
    report = processed.report
    log_processing_report(report)

    if not report.chunks:
        raise ValueError(
            f"Nenhum texto utilizável foi encontrado em {document_path.name}."
        )

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for chunk_index, chunk in enumerate(report.chunks):
        ids.append(
            create_chunk_id(
                relative_path=relative_path,
                page_number=chunk.page_start,
                chunk_index=chunk_index,
            )
        )
        documents.append(chunk.text)
        metadatas.append(
            chunk_metadata(
                processed.metadata,
                chunk,
                relative_path,
                document_path.suffix.lower(),
                chunk_index,
            )
        )

    # Mantém a semântica anterior de reinserção. A atomicidade da coleção é
    # acompanhada separadamente no backlog (B-30).
    collection.delete(where={"source_file": relative_path})

    for batch_start in range(0, len(documents), UPSERT_BATCH_SIZE):
        batch_end = batch_start + UPSERT_BATCH_SIZE
        collection.upsert(
            ids=ids[batch_start:batch_end],
            documents=documents[batch_start:batch_end],
            metadatas=metadatas[batch_start:batch_end],
        )

    logger.info("%s: %s chunks inseridos", document_path.name, len(documents))
    return len(documents)


def inspect_documents(
    document_path: Path | None = None,
    tokenizer: Tokenizer | None = None,
) -> list[ProcessingReport]:
    """Executa todo o processamento, sem importar nem alterar o ChromaDB."""

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

    logger.info(
        "Inspeção concluída: nenhum registro foi escrito no ChromaDB."
    )
    return reports


def ingest_documents(reset_collection: bool = False) -> None:
    """Localiza, processa e insere todos os PDFs e TXTs."""

    document_paths = _document_paths()

    if not document_paths:
        logger.warning("Nenhum PDF ou TXT encontrado em %s", DOCUMENTS_DIRECTORY)
        return

    # Import tardio: `--inspect` não deve abrir banco nem carregar o modelo de
    # embeddings do Chroma. O tokenizer é carregado uma única vez por rodada.
    from app.database.chroma_client import ChromaDBClient

    collection = ChromaDBClient.get_collection()
    tokenizer = load_embedding_tokenizer()

    if reset_collection:
        clear_collection(collection)

    total_chunks = 0
    errors: list[str] = []

    for document_path in document_paths:
        try:
            total_chunks += ingest_document(
                collection,
                document_path,
                tokenizer=tokenizer,
            )
        except Exception as error:
            logger.exception(
                "Erro ao processar %s: %s",
                document_path.name,
                error,
            )
            errors.append(document_path.name)

    logger.info(
        "Ingestão concluída: %s documentos, %s chunks processados e %s "
        "registros na coleção",
        len(document_paths) - len(errors),
        total_chunks,
        collection.count(),
    )

    if errors:
        raise RuntimeError(
            "Falha no processamento dos arquivos: " + ", ".join(errors)
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Processa e insere documentos veterinários no ChromaDB."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove todos os registros existentes antes da ingestão.",
    )
    parser.add_argument(
        "--inspect",
        "--dry-run",
        dest="inspect",
        action="store_true",
        help="Mostra seções e chunks sem abrir ou alterar o ChromaDB.",
    )
    parser.add_argument(
        "--file",
        help="No modo --inspect, processa somente este arquivo da pasta.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    arguments = parser.parse_args()

    if arguments.file and not arguments.inspect:
        parser.error("--file só pode ser usado com --inspect.")
    if arguments.reset and arguments.inspect:
        parser.error("--reset não pode ser combinado com --inspect.")

    if arguments.inspect:
        document_path = (
            resolve_inspection_path(arguments.file)
            if arguments.file
            else None
        )
        inspect_documents(document_path=document_path)
    else:
        ingest_documents(reset_collection=arguments.reset)


if __name__ == "__main__":
    main()
