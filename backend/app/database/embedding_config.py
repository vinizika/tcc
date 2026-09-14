"""Configuração reproduzível do embedding e da receita de chunks."""

from __future__ import annotations

import hashlib
import json

# Este nome é o mesmo já usado pela coleção. Mantê-lo aqui evita que o
# tokenizer do ingestor e o modelo que gera os embeddings divirjam.
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Commit imutável publicado no repositório do modelo. Nomear somente o
# modelo permitiria que uma atualização remota mudasse vetores entre máquinas.
EMBEDDING_MODEL_REVISION = (
    "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
)
EMBEDDING_DIMENSIONS = 384

# O SentenceTransformer publicado para este modelo usa max_seq_length=128.
# O ingestor ainda confere o model_max_length exposto pelo tokenizer e adota
# sempre o menor dos dois valores.
EMBEDDING_MAX_TOKENS = 128

# Baseline experimental. Não são valores considerados ótimos: devem ser
# comparados posteriormente na régua de recuperação do trilho A.
CHUNK_TARGET_TOKENS = 96
CHUNK_OVERLAP_TOKENS = 16

# A reconstrução não afirma possuir a serialização literal da receita
# perdida. Uma identidade nova evita fingir equivalência com o hash histórico.
EMBEDDING_RECIPE_VERSION = "vector-ingestion-recovery-v1"
EMBEDDING_TEXT_FIELDS = ("title", "section", "body")


def embedding_recipe() -> dict:
    """Retorna a receita canônica persistida em manifestos/fingerprints."""

    return {
        "version": EMBEDDING_RECIPE_VERSION,
        "model": EMBEDDING_MODEL_NAME,
        "revision": EMBEDDING_MODEL_REVISION,
        "dimensions": EMBEDDING_DIMENSIONS,
        "max_tokens": EMBEDDING_MAX_TOKENS,
        "target_tokens": CHUNK_TARGET_TOKENS,
        "overlap_tokens": CHUNK_OVERLAP_TOKENS,
        "embedding_text_fields": list(EMBEDDING_TEXT_FIELDS),
    }


def embedding_recipe_sha256() -> str:
    payload = json.dumps(
        embedding_recipe(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
