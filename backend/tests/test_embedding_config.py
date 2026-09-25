"""
As receitas de embedding (rodada 24 do João).

Cada coleção guarda no manifesto a receita que a construiu, e o cliente do
Chroma escolhe o modelo da consulta por ela. Estes testes travam os dois
pontos em que um descuido quebraria a ablação em silêncio: o hash da receita
acadêmica (que identifica as 13 coleções já versionadas) e a resolução de um
manifesto antigo, sem o campo novo.
"""

import pytest

from app.database.embedding_config import (
    BGE_M3_FICHAS,
    MINILM_ACADEMIC,
    PROFILE_RECIPES,
    RECIPES,
    embedding_recipe,
    embedding_recipe_sha256,
    recipe_for,
    recipe_for_profile,
    recipe_from_manifest,
)

HASH_DA_RECEITA_ACADEMICA = (
    "1a93e1e7db9a5b5a7766ca11b54162cb74cb76bb4d4c2c02b2dc0d5c4319682b"
)


def test_a_receita_academica_preserva_o_hash_das_colecoes_versionadas():
    assert MINILM_ACADEMIC.sha256() == HASH_DA_RECEITA_ACADEMICA
    assert embedding_recipe_sha256() == HASH_DA_RECEITA_ACADEMICA
    assert embedding_recipe() == MINILM_ACADEMIC.as_dict()
    assert "key" not in MINILM_ACADEMIC.as_dict()


def test_a_receita_das_fichas_e_o_bge_m3_medido_na_autopsia():
    assert BGE_M3_FICHAS.model == "BAAI/bge-m3"
    assert BGE_M3_FICHAS.revision == "5617a9f61b028005a4858fdac845db406aefb181"
    assert BGE_M3_FICHAS.dimensions == 1024
    assert BGE_M3_FICHAS.max_tokens == 512
    assert BGE_M3_FICHAS.sha256() != MINILM_ACADEMIC.sha256()


def test_cada_perfil_tem_a_sua_receita():
    assert recipe_for_profile("fichas") is BGE_M3_FICHAS
    for perfil in ("curated", "experimental", "legacy_rechunk"):
        assert recipe_for_profile(perfil) is MINILM_ACADEMIC
    assert set(PROFILE_RECIPES.values()) <= set(RECIPES)


def test_manifesto_antigo_resolve_pelo_modelo_e_pela_revisao():
    manifesto = {
        "embedding": {
            "model": MINILM_ACADEMIC.model,
            "revision": MINILM_ACADEMIC.revision,
            "dimensions": 384,
        }
    }

    assert recipe_from_manifest(manifesto) is MINILM_ACADEMIC


def test_manifesto_novo_resolve_pela_chave():
    manifesto = {"embedding": {"recipe_key": "bge-m3-fichas-v1"}}

    assert recipe_from_manifest(manifesto) is BGE_M3_FICHAS


def test_sem_manifesto_vale_a_colecao_legada():
    assert recipe_from_manifest(None) is MINILM_ACADEMIC


def test_manifesto_de_modelo_desconhecido_falha_alto():
    with pytest.raises(ValueError):
        recipe_from_manifest({"embedding": {"model": "outro", "revision": "x"}})
    with pytest.raises(ValueError):
        recipe_for("receita-inexistente")
