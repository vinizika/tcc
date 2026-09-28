"""Configuração reproduzível do embedding e da receita de chunks.

Cada coleção do Chroma é construída por uma **receita** (modelo, revisão,
dimensões, limite de tokens e, na base acadêmica, o recorte em trechos). A
receita fica no manifesto da coleção, e é por ela que o cliente escolhe o
modelo que transforma a consulta em vetor: uma coleção indexada com um modelo
só pode ser consultada com o mesmo modelo.

Hoje há duas receitas (rodada 24 do João):

- ``minilm-academic-v1``: a base acadêmica em trechos, com o MiniLM. É a
  receita de todas as coleções versionadas até 20/09, e a serialização dela
  continua a mesma (hash ``1a93e1e7…``);
- ``bge-m3-fichas-v1``: as 61 fichas de triagem, uma por quadro do mapa, com o
  bge-m3, sem recorte (a ficha inteira é um vetor).

As constantes de módulo abaixo continuam descrevendo a receita acadêmica: é a
que o recorte em trechos usa (``document_processing``), e mudá-las mudaria os
trechos de uma reindexação da base acadêmica.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

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


@dataclass(frozen=True)
class EmbeddingRecipe:
    """Como o texto de uma coleção virou vetor."""

    key: str
    version: str
    model: str
    revision: str
    dimensions: int
    max_tokens: int
    target_tokens: int | None
    overlap_tokens: int | None
    embedding_text_fields: tuple[str, ...]

    def as_dict(self) -> dict:
        """A serialização que entra no manifesto e no hash.

        A chave (`key`) fica de fora de propósito: a receita acadêmica tem de
        continuar produzindo o hash das coleções já versionadas.
        """

        return {
            "version": self.version,
            "model": self.model,
            "revision": self.revision,
            "dimensions": self.dimensions,
            "max_tokens": self.max_tokens,
            "target_tokens": self.target_tokens,
            "overlap_tokens": self.overlap_tokens,
            "embedding_text_fields": list(self.embedding_text_fields),
        }

    def sha256(self) -> str:
        payload = json.dumps(
            self.as_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


MINILM_ACADEMIC = EmbeddingRecipe(
    key="minilm-academic-v1",
    version=EMBEDDING_RECIPE_VERSION,
    model=EMBEDDING_MODEL_NAME,
    revision=EMBEDDING_MODEL_REVISION,
    dimensions=EMBEDDING_DIMENSIONS,
    max_tokens=EMBEDDING_MAX_TOKENS,
    target_tokens=CHUNK_TARGET_TOKENS,
    overlap_tokens=CHUNK_OVERLAP_TOKENS,
    embedding_text_fields=EMBEDDING_TEXT_FIELDS,
)

# bge-m3 na revisão medida na autópsia 2 (rodada 16). O limite do modelo é
# 8.192 tokens; 512 é o teto que a ingestão impõe às fichas (a maior tem 485),
# para uma ficha nova e longa demais falhar alto em vez de ser truncada.
BGE_M3_FICHAS = EmbeddingRecipe(
    key="bge-m3-fichas-v1",
    version="triage-cards-v1",
    model="BAAI/bge-m3",
    revision="5617a9f61b028005a4858fdac845db406aefb181",
    dimensions=1024,
    max_tokens=512,
    target_tokens=None,
    overlap_tokens=None,
    embedding_text_fields=("search_text",),
)

RECIPES = {recipe.key: recipe for recipe in (MINILM_ACADEMIC, BGE_M3_FICHAS)}

# Perfil de ingestão -> receita. O perfil decide o que entra; a receita, como
# vira vetor.
PROFILE_RECIPES = {
    "curated": MINILM_ACADEMIC.key,
    "experimental": MINILM_ACADEMIC.key,
    "legacy_rechunk": MINILM_ACADEMIC.key,
    "fichas": BGE_M3_FICHAS.key,
}

# A coleção-base legada (sem manifesto) sempre foi MiniLM.
LEGACY_RECIPE_KEY = MINILM_ACADEMIC.key


def recipe_for(key: str) -> EmbeddingRecipe:
    try:
        return RECIPES[key]
    except KeyError as error:
        raise ValueError(f"Receita de embedding desconhecida: {key!r}") from error


def recipe_for_profile(profile: str) -> EmbeddingRecipe:
    return recipe_for(PROFILE_RECIPES.get(profile, LEGACY_RECIPE_KEY))


def recipe_from_manifest(manifest: dict | None) -> EmbeddingRecipe:
    """A receita que construiu a coleção descrita pelo manifesto.

    Manifestos anteriores a 25/09 não têm `recipe_key`; neles a receita se
    resolve pelo par modelo + revisão. Um manifesto que não corresponde a
    nenhuma receita conhecida é erro: abrir a coleção com o modelo errado
    devolveria vizinhos sem sentido, em silêncio.
    """

    if manifest is None:
        return recipe_for(LEGACY_RECIPE_KEY)
    embedding = manifest.get("embedding") or {}
    key = embedding.get("recipe_key")
    if key:
        return recipe_for(str(key))
    for recipe in RECIPES.values():
        if (
            embedding.get("model") == recipe.model
            and embedding.get("revision") == recipe.revision
        ):
            return recipe
    raise ValueError(
        "O manifesto não corresponde a nenhuma receita de embedding conhecida: "
        f"modelo={embedding.get('model')!r}, revisão={embedding.get('revision')!r}"
    )


def embedding_recipe() -> dict:
    """Retorna a receita acadêmica, persistida em manifestos/fingerprints."""

    return MINILM_ACADEMIC.as_dict()


def embedding_recipe_sha256() -> str:
    return MINILM_ACADEMIC.sha256()
