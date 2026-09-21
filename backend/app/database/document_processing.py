"""
Processamento determinístico das fontes usadas pelo RAG.

O módulo preserva páginas e seções, remove ruído previsível e produz chunks
com o tokenizer do mesmo modelo empregado pelo ChromaDB. Não resume, traduz
ou reescreve o conteúdo clínico da fonte.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from pypdf import PdfReader

from app.core.logger import setup_logger
from app.database.embedding_config import (
    CHUNK_OVERLAP_TOKENS,
    CHUNK_TARGET_TOKENS,
    EMBEDDING_MAX_TOKENS,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_REVISION,
)
from app.database.pdf_layout_extraction import (
    ExtractionStatistics,
    extract_pdf_with_layout,
)


logger = setup_logger("DocumentProcessing")

DEFAULT_EXCLUDED_SECTIONS = (
    "References",
    "Bibliography",
    "About the authors",
    "Author information",
    "Disclosure of potential conflicts of interest",
    "Disclosure statement",
    "Conflict of interest",
    "Conflicts of interest",
    "Competing interests",
    "Funding",
    "Author contributions",
    "Acknowledgements",
    "Acknowledgments",
    "Front matter",
    "Article history",
    "Comprehensive review",
)

# Vocabulário deliberadamente curto de headings acadêmicos e clínicos. Os
# valores configurados no sidecar também entram no detector, o que permite
# tratar estruturas menos usuais sem editar o PDF ou recorrer a uma LLM.
KNOWN_SECTION_HEADINGS = (
    "Abstract",
    "Introduction",
    "Background",
    "Objectives",
    "Materials and methods",
    "Methods",
    "Results",
    "Discussion",
    "Epidemiology",
    "Risk factors",
    "Factors predisposing to heatstroke",
    "Pathogenesis",
    "Systemic outlook",
    "Neurological dysfunction and abnormalities",
    "Muscle damage and rhabdomyolysis",
    "Hemostatic derangement",
    "Acute kidney injury",
    "Acute respiratory distress syndrome",
    "Myocardial damage and cardiac arrhythmia",
    "Gastrointestinal tract lesions and bacterial translocation",
    "Clinical signs",
    "Clinical signs upon presentation",
    "Clinical presentation",
    "Diagnosis",
    "Differential diagnosis",
    "Prognosis",
    "Treatment",
    "Management",
    "Complications",
    "Novel molecular and biochemical biomarkers in canine heatstroke",
    "Preconditioning against heatstroke",
    "Conclusions",
    "Conclusion",
    "Abbreviations",
    "References",
    "Bibliography",
    "About the authors",
    "Author information",
    "Disclosure of potential conflicts of interest",
    "Disclosure statement",
    "Conflict of interest",
    "Conflicts of interest",
    "Competing interests",
    "Funding",
    "Author contributions",
    "Acknowledgements",
    "Acknowledgments",
    "Article history",
)

OPTIONAL_METADATA_FIELDS = (
    "authors",
    "year",
    "doi",
    "journal",
    "language",
    "source_url",
)

_DEHYPHENATION_PATTERN = re.compile(
    r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ])-\s*\n\s*(?=[a-zà-öø-ÿ])"
)
_SENTENCE_BOUNDARY = re.compile(
    r"(?<=[.!?])\s+(?=(?:[\"'“‘(\[]?[A-ZÀ-ÖØ-Þ0-9]))"
)
_CORRUPTED_SECTION_OPENER = re.compile(r"^\d{1,3}(?=[a-zà-öø-ÿ])")
_NEXT_COMPLETE_SENTENCE = re.compile(
    r"[.!?]\s*(?:\d+(?:[,\-]\d+)*)?\s+(?=[A-ZÀ-ÖØ-Þ])"
)
_NUMBERED_HEADING_PREFIX = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*[.)]?|[IVXLC]+[.)])\s+",
    re.IGNORECASE,
)
_EDITORIAL_LINE_PATTERNS = (
    re.compile(r"^TEMPERATURE(?:\s+\d+)?$", re.IGNORECASE),
    re.compile(r"^\d+\s+[A-Z][A-Z.\s]+\s+ET\s+AL\.?$"),
    re.compile(r"^CONTACT\b", re.IGNORECASE),
    re.compile(r"^©\s*\d{4}\b"),
    re.compile(r"^\d{4},\s+VOL\.", re.IGNORECASE),
    re.compile(r"^https?://doi\.org/", re.IGNORECASE),
    re.compile(r"^KEYWORDS$", re.IGNORECASE),
    re.compile(
        r"(?:©|copyright|reproduced by permission|permission to reuse|"
        r"rightsholder)",
        re.IGNORECASE,
    ),
)


class Tokenizer(Protocol):
    """Parte da interface Hugging Face usada pelo chunker."""

    model_max_length: int

    def encode(
        self,
        text: str,
        add_special_tokens: bool = True,
        truncation: bool = False,
    ) -> list[int]: ...


@dataclass(frozen=True)
class PageText:
    number: int
    text: str


@dataclass(frozen=True)
class TextUnit:
    text: str
    page_start: int
    page_end: int


@dataclass
class SectionText:
    title: str
    units: list[TextUnit] = field(default_factory=list)


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    section: str
    page_start: int
    page_end: int
    token_count: int
    # Corpo limpo, sem os rótulos contextuais usados somente no embedding.
    # O default preserva construtores posicionais e snapshots antigos.
    body: str = ""


@dataclass(frozen=True)
class ProcessingReport:
    document_name: str
    pages_extracted: int
    detected_sections: tuple[str, ...]
    included_sections: tuple[str, ...]
    excluded_sections: tuple[str, ...]
    chunks: tuple[DocumentChunk, ...]
    fallback_splits: int
    used_section_fallback: bool
    extraction_statistics: ExtractionStatistics | None = None
    corrupted_openers_removed: int = 0


@dataclass(frozen=True)
class ProcessedDocument:
    metadata: dict[str, Any]
    report: ProcessingReport


def normalize_text(text: str) -> str:
    """Normaliza whitespace apenas depois de a estrutura ter sido lida."""

    return re.sub(r"\s+", " ", text).strip()


def dehyphenate_line_breaks(text: str) -> str:
    """Recompõe palavras quebradas por hífen exatamente na mudança de linha."""

    return _DEHYPHENATION_PATTERN.sub("", text)


def clean_structured_text(text: str) -> str:
    """Limpeza conservadora que ainda preserva as quebras entre linhas."""

    normalized = unicodedata.normalize("NFKC", text).replace("\r\n", "\n")
    normalized = normalized.replace("\r", "\n")
    normalized = dehyphenate_line_breaks(normalized)

    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in normalized.split("\n")
    ]

    return "\n".join(lines).strip()


def _section_key(title: str) -> str:
    title = unicodedata.normalize("NFKD", title).casefold()
    title = "".join(
        character
        for character in title
        if not unicodedata.combining(character)
    )
    title = _NUMBERED_HEADING_PREFIX.sub("", title)
    return re.sub(r"[^a-z0-9]+", "", title)


def _metadata_list(indexing: dict[str, Any], field_name: str) -> list[str]:
    value = indexing.get(field_name, [])

    if value is None:
        return []

    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise ValueError(
            f"indexing.{field_name} deve ser uma lista de textos."
        )

    return [item.strip() for item in value if item.strip()]


def _excluded_pages(indexing: dict[str, Any]) -> set[int]:
    value = indexing.get("exclude_pages", [])

    if value is None:
        return set()

    if not isinstance(value, list) or not all(
        isinstance(item, int) and item >= 0 for item in value
    ):
        raise ValueError(
            "indexing.exclude_pages deve ser uma lista de páginas inteiras."
        )

    return set(value)


def load_metadata(document_path: Path) -> dict[str, Any]:
    """Carrega o sidecar e usa defaults neutros quando ele não existe."""

    metadata_path = document_path.with_suffix(".json")
    metadata: dict[str, Any] = {
        "title": document_path.stem.replace("_", " ").title(),
        "source": document_path.name,
        "document_type": "unknown",
        "validation_status": "not_informed",
        "species": "not_informed",
        "topic": "not_informed",
        "indexing": {},
    }

    if not metadata_path.exists():
        logger.warning(
            "Metadados não encontrados para %s. Use um sidecar JSON para "
            "registrar procedência e curadoria; defaults neutros serão usados.",
            document_path.name,
        )
        return metadata

    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        loaded_metadata = json.load(metadata_file)

    if not isinstance(loaded_metadata, dict):
        raise ValueError(f"{metadata_path.name} deve conter um objeto JSON.")

    metadata.update(loaded_metadata)

    indexing = metadata.get("indexing") or {}
    if not isinstance(indexing, dict):
        raise ValueError("O campo indexing deve ser um objeto JSON.")

    # Valida cedo para que erros de curadoria não apareçam no meio do upsert.
    _metadata_list(indexing, "include_sections")
    _metadata_list(indexing, "exclude_sections")
    _metadata_list(indexing, "retrieval_anchors")
    _excluded_pages(indexing)
    metadata["indexing"] = indexing

    return metadata


def _extract_pdf_pages_with_pypdf(document_path: Path) -> list[PageText]:
    """Extrator simples preservado como fallback do parser de layout."""

    reader = PdfReader(str(document_path))

    if reader.is_encrypted and reader.decrypt("") == 0:
        raise ValueError(f"O PDF {document_path.name} está protegido por senha.")

    pages: list[PageText] = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = clean_structured_text(page.extract_text() or "")

        if page_text:
            pages.append(PageText(page_number, page_text))
        else:
            logger.warning(
                "Página sem texto: %s, página %s. Ela pode ser uma imagem.",
                document_path.name,
                page_number,
            )

    return pages


def extract_pdf_pages_with_statistics(
    document_path: Path,
) -> tuple[list[PageText], ExtractionStatistics]:
    """Prefere layout/coordenadas e recua para pypdf em caso de falha."""

    try:
        result = extract_pdf_with_layout(document_path)
        pages = [
            PageText(page.number, clean_structured_text(page.text))
            for page in result.pages
            if page.text.strip()
        ]
        return pages, result.statistics
    except Exception as error:
        warning = (
            f"Extrator estruturado falhou ({type(error).__name__}: {error}); "
            "usando pypdf simples."
        )
        logger.warning("%s: %s", document_path.name, warning)
        pages = _extract_pdf_pages_with_pypdf(document_path)
        statistics = ExtractionStatistics(
            extractor="pypdf/simple-fallback",
            warnings=(warning,),
        )
        return pages, statistics


def extract_pdf_pages(document_path: Path) -> list[PageText]:
    """Compatibilidade para consumidores que precisam somente das páginas."""

    pages, _ = extract_pdf_pages_with_statistics(document_path)
    return pages


def extract_txt_pages(document_path: Path) -> list[PageText]:
    """Lê TXT; a página zero mantém a compatibilidade com arquivos sem páginas."""

    text = clean_structured_text(document_path.read_text(encoding="utf-8"))
    return [PageText(0, text)] if text else []


def extract_document_pages(document_path: Path) -> list[PageText]:
    suffix = document_path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_pages(document_path)
    if suffix == ".txt":
        return extract_txt_pages(document_path)

    raise ValueError(f"Formato não suportado: {document_path.suffix}")


def extract_document_pages_with_statistics(
    document_path: Path,
) -> tuple[list[PageText], ExtractionStatistics]:
    suffix = document_path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_pages_with_statistics(document_path)
    if suffix == ".txt":
        return (
            extract_txt_pages(document_path),
            ExtractionStatistics(extractor="plain-text"),
        )

    raise ValueError(f"Formato não suportado: {document_path.suffix}")


def _is_editorial_noise_line(line: str) -> bool:
    return any(pattern.search(line) for pattern in _EDITORIAL_LINE_PATTERNS)


def remove_repeated_margin_lines(pages: list[PageText]) -> list[PageText]:
    """Remove headers/footers idênticos repetidos em três ou mais páginas."""

    if len(pages) < 3:
        return pages

    margin_keys_by_page: list[set[str]] = []

    for page in pages:
        nonempty_lines = [line for line in page.text.splitlines() if line.strip()]
        margin_lines = [*nonempty_lines[:3], *nonempty_lines[-3:]]
        margin_keys_by_page.append(
            {normalize_text(line).casefold() for line in margin_lines}
        )

    occurrences = Counter(
        key for page_keys in margin_keys_by_page for key in page_keys
    )
    repeated_keys = {
        key
        for key, count in occurrences.items()
        if count >= 3 and 2 <= len(key) <= 160
    }

    cleaned_pages: list[PageText] = []

    for page in pages:
        lines = page.text.splitlines()
        nonempty_indexes = [
            index for index, line in enumerate(lines) if line.strip()
        ]
        margin_indexes = set(nonempty_indexes[:3]) | set(nonempty_indexes[-3:])
        kept_lines = [
            line
            for index, line in enumerate(lines)
            if not (
                index in margin_indexes
                and normalize_text(line).casefold() in repeated_keys
            )
        ]
        cleaned_pages.append(PageText(page.number, "\n".join(kept_lines).strip()))

    return cleaned_pages


def _heading_catalog(configured_sections: list[str]) -> dict[str, str]:
    catalog: dict[str, str] = {}

    for title in (*KNOWN_SECTION_HEADINGS, *configured_sections):
        catalog[_section_key(title)] = title

    return catalog


def _match_heading(
    lines: list[str],
    index: int,
    catalog: dict[str, str],
) -> tuple[str, int] | None:
    """Reconhece heading em uma linha ou quebrado em duas linhas consecutivas."""

    line = _NUMBERED_HEADING_PREFIX.sub("", lines[index]).strip(" :")
    key = _section_key(line)

    if key in catalog:
        return catalog[key], 1

    if index + 1 < len(lines):
        joined = f"{line} {lines[index + 1].strip(' :')}"
        joined_key = _section_key(joined)

        if joined_key in catalog:
            return catalog[joined_key], 2

    # ALL CAPS é um fallback seguro para headings acadêmicos curtos. Evita-se
    # inferir headings de qualquer linha em Title Case no corpo em colunas.
    letters = "".join(character for character in line if character.isalpha())
    if (
        letters
        and letters.isupper()
        and 2 <= len(line.split()) <= 8
        and len(line) <= 80
        and not line.endswith((".", ";", ","))
    ):
        return line.title(), 1

    return None


def detect_sections(
    pages: list[PageText],
    configured_sections: list[str] | None = None,
) -> tuple[list[SectionText], bool]:
    """Detecta seções mantendo a página associada a cada trecho."""

    catalog = _heading_catalog(configured_sections or [])
    sections: list[SectionText] = []
    current = SectionText("Front matter")
    found_heading = False

    for page in pages:
        lines = page.text.splitlines()
        line_index = 0

        while line_index < len(lines):
            line = lines[line_index].strip()

            if not line or _is_editorial_noise_line(line):
                line_index += 1
                continue

            # References/Bibliography são seções terminais na estrutura
            # suportada. Citações contêm muitas linhas curtas em maiúsculas
            # (PMID, DOI, siglas) que não podem reabrir seções clínicas.
            terminal_references = _section_key(current.title) in {
                _section_key("References"),
                _section_key("Bibliography"),
            }
            heading = None if terminal_references else _match_heading(
                lines,
                line_index,
                catalog,
            )

            # Entradas de glossário em Abbreviations podem coincidir com
            # headings clínicos conhecidos. Só uma nova seção editorial pode
            # encerrar esse bloco; assim AKI/ARDS não voltam ao corpus.
            if (
                heading
                and _section_key(current.title) == _section_key("Abbreviations")
                and _section_key(heading[0])
                not in {_section_key(title) for title in DEFAULT_EXCLUDED_SECTIONS}
            ):
                heading = None

            if heading:
                if current.units or found_heading:
                    sections.append(current)

                title, consumed_lines = heading
                current = SectionText(title)
                found_heading = True
                line_index += consumed_lines
                continue

            current.units.append(TextUnit(line, page.number, page.number))
            line_index += 1

    if current.units:
        sections.append(current)

    if not found_heading:
        logger.warning(
            "Documento sem section headings detectáveis; usando fallback "
            "de seção única."
        )
        all_units = [unit for section in sections for unit in section.units]
        return [SectionText("Document", all_units)], True

    return sections, False


def remove_corrupted_section_openers(
    sections: list[SectionText],
) -> int:
    """Descarta fragmentos inequivocamente incompletos após um heading.

    Um número de citação colado a uma palavra minúscula logo no início da
    seção indica que o próprio fluxo textual do PDF começou no meio de uma
    frase. Quando há uma sentença completa em seguida, preservamos essa
    sentença e descartamos somente o prefixo corrompido. Nenhum texto é
    completado, inferido ou reescrito.
    """

    removed = 0

    for section in sections:
        if not section.units:
            continue

        first_unit = section.units[0]
        if not _CORRUPTED_SECTION_OPENER.match(first_unit.text):
            continue

        boundary = _NEXT_COMPLETE_SENTENCE.search(first_unit.text)
        if not boundary:
            continue

        preserved_text = first_unit.text[boundary.end() :].strip()
        if not preserved_text:
            continue

        section.units[0] = TextUnit(
            preserved_text,
            first_unit.page_start,
            first_unit.page_end,
        )
        removed += 1

    return removed


def filter_sections(
    sections: list[SectionText],
    indexing: dict[str, Any],
) -> tuple[list[SectionText], list[str]]:
    """Aplica defaults, include whitelist opcional e exclusões do sidecar."""

    include_titles = _metadata_list(indexing, "include_sections")
    exclude_titles = _metadata_list(indexing, "exclude_sections")
    include_keys = {_section_key(title) for title in include_titles}
    exclude_keys = {
        _section_key(title)
        for title in (*DEFAULT_EXCLUDED_SECTIONS, *exclude_titles)
    }
    detected_keys = {_section_key(section.title) for section in sections}

    for configured_title in (*include_titles, *exclude_titles):
        if _section_key(configured_title) not in detected_keys:
            logger.warning(
                "Seção configurada e não encontrada: %s",
                configured_title,
            )

    included: list[SectionText] = []
    excluded: list[str] = []

    for section in sections:
        key = _section_key(section.title)
        allowed_by_include = not include_keys or key in include_keys

        if not allowed_by_include or key in exclude_keys:
            excluded.append(section.title)
        elif section.units:
            included.append(section)

    return included, excluded


def load_embedding_tokenizer() -> Tokenizer:
    """Carrega sob demanda para que `--inspect --help` não baixe o modelo."""

    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(
        EMBEDDING_MODEL_NAME,
        revision=EMBEDDING_MODEL_REVISION,
        use_fast=True,
    )


def tokenizer_safe_limit(tokenizer: Tokenizer) -> int:
    """Adota o menor limite confiável entre tokenizer e SentenceTransformer."""

    tokenizer_limit = getattr(tokenizer, "model_max_length", None)

    if not isinstance(tokenizer_limit, int) or tokenizer_limit <= 0:
        return EMBEDDING_MAX_TOKENS

    # Tokenizers sem limite conhecido usam sentinelas enormes.
    if tokenizer_limit > 1_000_000:
        return EMBEDDING_MAX_TOKENS

    return min(EMBEDDING_MAX_TOKENS, tokenizer_limit)


def count_tokens(
    tokenizer: Tokenizer,
    text: str,
    *,
    add_special_tokens: bool = True,
) -> int:
    return len(
        tokenizer.encode(
            text,
            add_special_tokens=add_special_tokens,
            truncation=False,
        )
    )


def _chunk_prefix(title: str, section: str) -> str:
    return f"Document title: {title}\nSection: {section}\n\n"


def _sentence_units(section: SectionText) -> list[TextUnit]:
    """Une linhas de layout por página e prefere frases como unidade."""

    page_lines: dict[int, list[str]] = {}
    page_order: list[int] = []

    for unit in section.units:
        if unit.page_start not in page_lines:
            page_lines[unit.page_start] = []
            page_order.append(unit.page_start)
        page_lines[unit.page_start].append(unit.text)

    units: list[TextUnit] = []

    for page_number in page_order:
        page_text = normalize_text(" ".join(page_lines[page_number]))

        for sentence in _SENTENCE_BOUNDARY.split(page_text):
            sentence = sentence.strip()
            if sentence:
                units.append(TextUnit(sentence, page_number, page_number))

    return units


def _split_unit_at_words(
    unit: TextUnit,
    prefix: str,
    tokenizer: Tokenizer,
    token_limit: int,
) -> list[TextUnit]:
    """Fallback de frase longa; jamais inicia uma parte no meio de palavra."""

    words = unit.text.split()
    parts: list[TextUnit] = []
    current_words: list[str] = []

    for word in words:
        candidate_words = [*current_words, word]
        candidate = " ".join(candidate_words)

        if count_tokens(tokenizer, prefix + candidate) <= token_limit:
            current_words = candidate_words
            continue

        if not current_words:
            raise ValueError(
                "Uma unidade sem espaços excede o limite seguro do embedding."
            )

        parts.append(
            TextUnit(
                " ".join(current_words),
                unit.page_start,
                unit.page_end,
            )
        )
        current_words = [word]

        if count_tokens(tokenizer, prefix + word) > token_limit:
            raise ValueError(
                "Uma unidade sem espaços excede o limite seguro do embedding."
            )

    if current_words:
        parts.append(
            TextUnit(
                " ".join(current_words),
                unit.page_start,
                unit.page_end,
            )
        )

    return parts


def _tail_overlap(
    units: list[TextUnit],
    tokenizer: Tokenizer,
    overlap_tokens: int,
) -> list[TextUnit]:
    if overlap_tokens <= 0 or not units:
        return []

    selected: list[TextUnit] = []

    for unit in reversed(units):
        candidate = [unit, *selected]
        candidate_text = " ".join(item.text for item in candidate)

        if count_tokens(
            tokenizer,
            candidate_text,
            add_special_tokens=False,
        ) <= overlap_tokens:
            selected = candidate
        else:
            break

    if selected:
        return selected

    # Se a última frase for maior que o overlap, reaproveita palavras inteiras
    # do seu final. A próxima janela continua começando em fronteira lexical.
    last = units[-1]
    tail_words: list[str] = []

    for word in reversed(last.text.split()):
        candidate_words = [word, *tail_words]
        candidate = " ".join(candidate_words)

        if count_tokens(
            tokenizer,
            candidate,
            add_special_tokens=False,
        ) > overlap_tokens:
            break
        tail_words = candidate_words

    if not tail_words:
        return []

    return [TextUnit(" ".join(tail_words), last.page_start, last.page_end)]


def chunk_section(
    section: SectionText,
    title: str,
    tokenizer: Tokenizer,
    target_tokens: int = CHUNK_TARGET_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
    safe_limit: int | None = None,
) -> tuple[list[DocumentChunk], int]:
    """Cria chunks por tokens, preservando frases e páginas quando possível."""

    safe_limit = safe_limit or tokenizer_safe_limit(tokenizer)

    if target_tokens <= 0 or target_tokens > safe_limit:
        raise ValueError("O target deve estar entre 1 e o limite seguro.")
    if overlap_tokens < 0 or overlap_tokens >= target_tokens:
        raise ValueError("O overlap deve ser menor que o target.")

    prefix = _chunk_prefix(title, section.title)
    if count_tokens(tokenizer, prefix) >= target_tokens:
        raise ValueError(
            "Título e seção consomem todo o target de tokens do chunk."
        )

    source_units = _sentence_units(section)
    units: list[TextUnit] = []
    fallback_splits = 0

    for unit in source_units:
        if count_tokens(tokenizer, prefix + unit.text) <= safe_limit:
            units.append(unit)
            continue

        split_units = _split_unit_at_words(
            unit,
            prefix,
            tokenizer,
            target_tokens - overlap_tokens,
        )
        units.extend(split_units)
        fallback_splits += 1

    chunks: list[DocumentChunk] = []
    next_index = 0
    carry: list[TextUnit] = []

    while next_index < len(units):
        current = list(carry)
        added_new_unit = False

        while next_index < len(units):
            candidate = [*current, units[next_index]]
            candidate_text = " ".join(unit.text for unit in candidate)
            candidate_tokens = count_tokens(tokenizer, prefix + candidate_text)

            if candidate_tokens <= target_tokens:
                current = candidate
                next_index += 1
                added_new_unit = True
                continue

            if not current and candidate_tokens <= safe_limit:
                current = candidate
                next_index += 1
                added_new_unit = True
            break

        # Um overlap pode não deixar espaço para a próxima frase. Nesse caso
        # ele é descartado; repetir somente o overlap criaria loop/duplicata.
        if not added_new_unit:
            current = []
            carry = []
            continue

        content = " ".join(unit.text for unit in current)
        chunk_text = prefix + content
        token_count = count_tokens(tokenizer, chunk_text)

        if token_count > safe_limit:
            raise AssertionError("Chunk excedeu o limite seguro de tokens.")

        chunks.append(
            DocumentChunk(
                text=chunk_text,
                section=section.title,
                page_start=min(unit.page_start for unit in current),
                page_end=max(unit.page_end for unit in current),
                token_count=token_count,
                body=content,
            )
        )

        carry = (
            _tail_overlap(current, tokenizer, overlap_tokens)
            if next_index < len(units)
            else []
        )

    return chunks, fallback_splits


def process_pages(
    document_name: str,
    pages: list[PageText],
    metadata: dict[str, Any],
    tokenizer: Tokenizer,
    target_tokens: int = CHUNK_TARGET_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
    extraction_statistics: ExtractionStatistics | None = None,
) -> ProcessingReport:
    """Executa filtragem, detecção e chunking sobre páginas já extraídas."""

    indexing = metadata.get("indexing") or {}
    excluded_page_numbers = _excluded_pages(indexing)
    usable_pages = [page for page in pages if page.number not in excluded_page_numbers]
    usable_pages = remove_repeated_margin_lines(usable_pages)

    configured_sections = [
        *_metadata_list(indexing, "include_sections"),
        *_metadata_list(indexing, "exclude_sections"),
    ]
    sections, used_fallback = detect_sections(
        usable_pages,
        configured_sections=configured_sections,
    )
    corrupted_openers_removed = remove_corrupted_section_openers(sections)
    if corrupted_openers_removed:
        logger.warning(
            "%s: %s fragmento(s) inicial(is) corrompido(s) foram "
            "descartados sem reconstrução de conteúdo.",
            document_name,
            corrupted_openers_removed,
        )
    included, excluded = filter_sections(sections, indexing)

    chunks: list[DocumentChunk] = []
    fallback_splits = 0
    safe_limit = tokenizer_safe_limit(tokenizer)

    for section in included:
        section_chunks, section_fallbacks = chunk_section(
            section,
            str(metadata["title"]),
            tokenizer,
            target_tokens=target_tokens,
            overlap_tokens=overlap_tokens,
            safe_limit=safe_limit,
        )
        chunks.extend(section_chunks)
        fallback_splits += section_fallbacks

    if fallback_splits:
        logger.warning(
            "%s: %s frase(s) excederam o limite e usaram fallback por palavras.",
            document_name,
            fallback_splits,
        )

    if not chunks:
        logger.warning("%s: conteúdo vazio após filtragem.", document_name)

    return ProcessingReport(
        document_name=document_name,
        pages_extracted=len(pages),
        detected_sections=tuple(section.title for section in sections),
        included_sections=tuple(section.title for section in included),
        excluded_sections=tuple(excluded),
        chunks=tuple(chunks),
        fallback_splits=fallback_splits,
        used_section_fallback=used_fallback,
        extraction_statistics=extraction_statistics,
        corrupted_openers_removed=corrupted_openers_removed,
    )


def process_document(
    document_path: Path,
    tokenizer: Tokenizer | None = None,
) -> ProcessedDocument:
    metadata = load_metadata(document_path)
    pages, extraction_statistics = extract_document_pages_with_statistics(
        document_path
    )
    active_tokenizer = tokenizer or load_embedding_tokenizer()
    report = process_pages(
        document_path.name,
        pages,
        metadata,
        active_tokenizer,
        extraction_statistics=extraction_statistics,
    )

    return ProcessedDocument(metadata=metadata, report=report)


def chunk_metadata(
    document_metadata: dict[str, Any],
    chunk: DocumentChunk,
    relative_path: str,
    file_type: str,
    chunk_index: int,
) -> dict[str, Any]:
    """Converte metadados para escalares aceitos pelo ChromaDB."""

    metadata: dict[str, Any] = {
        "title": str(document_metadata["title"]),
        "source": str(document_metadata["source"]),
        "document_type": str(document_metadata["document_type"]),
        "validation_status": str(document_metadata["validation_status"]),
        "species": str(document_metadata["species"]),
        "topic": str(document_metadata["topic"]),
        "source_file": relative_path,
        "file_type": file_type,
        "page": chunk.page_start,
        "page_start": chunk.page_start,
        "page_end": chunk.page_end,
        "section": chunk.section,
        "chunk_index": chunk_index,
        "token_count": chunk.token_count,
        "body": chunk.body or chunk.text,
    }

    retrieval_anchors = _metadata_list(
        document_metadata.get("indexing") or {},
        "retrieval_anchors",
    )
    if retrieval_anchors:
        metadata["retrieval_anchors"] = json.dumps(
            retrieval_anchors,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    for field_name in OPTIONAL_METADATA_FIELDS:
        value = document_metadata.get(field_name)
        if value is not None and value != "":
            metadata[field_name] = value if isinstance(value, int) else str(value)

    return metadata
