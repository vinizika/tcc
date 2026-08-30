import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from app.core.logger import setup_logger
from app.database.chroma_client import ChromaDBClient


logger = setup_logger("DocumentIngestion")

BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]
DOCUMENTS_DIRECTORY = BACKEND_DIRECTORY / "data" / "documents"

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
UPSERT_BATCH_SIZE = 100


def normalize_text(text: str) -> str:
    """
    Remove espaços e quebras de linha excessivos.
    """

    return re.sub(r"\s+", " ", text).strip()


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Divide o texto em chunks com sobreposição.
    Tenta encerrar cada chunk no final de uma frase ou palavra.
    """

    if overlap >= chunk_size:
        raise ValueError(
            "O overlap deve ser menor que o tamanho do chunk."
        )

    text = normalize_text(text)

    if not text:
        return []

    chunks = []
    start = 0
    minimum_boundary = int(chunk_size * 0.6)

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            sentence_boundary = text.rfind(
                ". ",
                start + minimum_boundary,
                end,
            )

            if sentence_boundary != -1:
                end = sentence_boundary + 1
            else:
                word_boundary = text.rfind(
                    " ",
                    start + minimum_boundary,
                    end,
                )

                if word_boundary != -1:
                    end = word_boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def load_metadata(document_path: Path) -> dict[str, Any]:
    """
    Carrega metadados de um arquivo JSON com o mesmo nome
    do documento.

    Exemplo:
        protocolo.pdf
        protocolo.json
    """

    metadata_path = document_path.with_suffix(".json")

    default_metadata = {
        "title": document_path.stem.replace("_", " ").title(),
        "source": document_path.name,
        "document_type": "synthetic_test",
        "validation_status": "not_validated",
        "species": "not_informed",
        "topic": "not_informed",
    }

    if not metadata_path.exists():
        logger.warning(
            f"Metadados não encontrados para {document_path.name}. "
            "Valores padrão serão utilizados."
        )
        return default_metadata

    with metadata_path.open(
        "r",
        encoding="utf-8",
    ) as metadata_file:
        loaded_metadata = json.load(metadata_file)

    default_metadata.update(loaded_metadata)

    return default_metadata


def extract_pdf_pages(
    document_path: Path,
) -> list[tuple[int, str]]:
    """
    Extrai o texto de cada página do PDF.
    """

    reader = PdfReader(str(document_path))

    if reader.is_encrypted:
        decryption_result = reader.decrypt("")

        if decryption_result == 0:
            raise ValueError(
                f"O PDF {document_path.name} está protegido por senha."
            )

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        page_text = normalize_text(
            page.extract_text() or ""
        )

        if page_text:
            pages.append(
                (page_number, page_text)
            )
        else:
            logger.warning(
                f"Nenhum texto extraído de "
                f"{document_path.name}, página {page_number}. "
                "A página pode ser uma imagem escaneada."
            )

    return pages


def extract_txt_content(
    document_path: Path,
) -> list[tuple[int, str]]:
    """
    Lê um documento TXT.
    A página zero representa um arquivo sem paginação.
    """

    text = document_path.read_text(
        encoding="utf-8"
    )

    text = normalize_text(text)

    if not text:
        return []

    return [(0, text)]


def extract_document_content(
    document_path: Path,
) -> list[tuple[int, str]]:
    """
    Seleciona o extrator conforme a extensão.
    """

    if document_path.suffix.lower() == ".pdf":
        return extract_pdf_pages(document_path)

    if document_path.suffix.lower() == ".txt":
        return extract_txt_content(document_path)

    raise ValueError(
        f"Formato não suportado: {document_path.suffix}"
    )


def create_chunk_id(
    relative_path: str,
    page_number: int,
    chunk_index: int,
) -> str:
    """
    Gera um ID estável para cada chunk.
    """

    identifier = (
        f"{relative_path}:"
        f"{page_number}:"
        f"{chunk_index}"
    )

    return hashlib.sha256(
        identifier.encode("utf-8")
    ).hexdigest()


def clear_collection(collection) -> None:
    """
    Remove todos os registros da coleção atual.
    """

    removed_documents = 0

    while collection.count() > 0:
        existing_records = collection.get(
            limit=1000
        )

        existing_ids = existing_records.get(
            "ids",
            []
        )

        if not existing_ids:
            break

        collection.delete(ids=existing_ids)
        removed_documents += len(existing_ids)

    logger.info(
        f"{removed_documents} registros antigos removidos"
    )


def ingest_document(
    collection,
    document_path: Path,
) -> int:
    """
    Extrai, divide e insere um documento no ChromaDB.
    """

    relative_path = str(
        document_path.relative_to(
            DOCUMENTS_DIRECTORY
        )
    )

    document_metadata = load_metadata(
        document_path
    )

    extracted_sections = extract_document_content(
        document_path
    )

    ids = []
    documents = []
    metadatas = []

    for page_number, section_text in extracted_sections:
        chunks = split_text(section_text)

        for chunk_index, chunk in enumerate(chunks):
            chunk_id = create_chunk_id(
                relative_path=relative_path,
                page_number=page_number,
                chunk_index=chunk_index,
            )

            chunk_metadata = {
                "title": str(
                    document_metadata["title"]
                ),
                "source": str(
                    document_metadata["source"]
                ),
                "document_type": str(
                    document_metadata["document_type"]
                ),
                "validation_status": str(
                    document_metadata["validation_status"]
                ),
                "species": str(
                    document_metadata["species"]
                ),
                "topic": str(
                    document_metadata["topic"]
                ),
                "source_file": relative_path,
                "file_type": document_path.suffix.lower(),
                "page": page_number,
                "chunk_index": chunk_index,
            }

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(chunk_metadata)

    if not documents:
        raise ValueError(
            f"Nenhum texto utilizável foi encontrado em "
            f"{document_path.name}."
        )

    # Remove chunks antigos do mesmo arquivo antes da reinserção.
    collection.delete(
        where={
            "source_file": relative_path
        }
    )

    for batch_start in range(
        0,
        len(documents),
        UPSERT_BATCH_SIZE,
    ):
        batch_end = (
            batch_start + UPSERT_BATCH_SIZE
        )

        collection.upsert(
            ids=ids[batch_start:batch_end],
            documents=documents[
                batch_start:batch_end
            ],
            metadatas=metadatas[
                batch_start:batch_end
            ],
        )

    logger.info(
        f"{document_path.name}: "
        f"{len(documents)} chunks inseridos"
    )

    return len(documents)


def ingest_documents(
    reset_collection: bool = False,
) -> None:
    """
    Localiza e processa todos os PDFs e TXTs.
    """

    DOCUMENTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    collection = (
        ChromaDBClient.get_collection()
    )

    document_paths = sorted(
        document_path
        for document_path
        in DOCUMENTS_DIRECTORY.rglob("*")
        if (
            document_path.is_file()
            and document_path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        )
    )

    if not document_paths:
        logger.warning(
            f"Nenhum PDF ou TXT encontrado em "
            f"{DOCUMENTS_DIRECTORY}"
        )
        return

    if reset_collection:
        clear_collection(collection)

    total_chunks = 0
    errors = []

    for document_path in document_paths:
        try:
            total_chunks += ingest_document(
                collection,
                document_path,
            )
        except Exception as error:
            logger.exception(
                f"Erro ao processar "
                f"{document_path.name}: {error}"
            )
            errors.append(document_path.name)

    logger.info(
        f"Ingestão concluída: "
        f"{len(document_paths) - len(errors)} documentos, "
        f"{total_chunks} chunks processados e "
        f"{collection.count()} registros na coleção"
    )

    if errors:
        raise RuntimeError(
            "Falha no processamento dos arquivos: "
            + ", ".join(errors)
        )


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(
        description=(
            "Insere documentos veterinários "
            "no ChromaDB."
        )
    )

    argument_parser.add_argument(
        "--reset",
        action="store_true",
        help=(
            "Remove todos os registros existentes "
            "antes da ingestão."
        ),
    )

    arguments = argument_parser.parse_args()

    ingest_documents(
        reset_collection=arguments.reset
    )