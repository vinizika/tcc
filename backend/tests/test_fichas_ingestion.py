"""
O perfil `fichas` da ingestão (rodada 24 do João).

As 61 fichas de triagem viram uma coleção com o bge-m3: o texto de busca é o
que vira vetor, e o texto de leitura vai nos metadados, porque é ele que o
atendente lê. Os testes usam o `backend/data/fichas.json` versionado e um
tokenizer falso (nada é baixado).
"""

import json

import pytest

from app.database import ingest_documents as ingest
from app.database.embedding_config import BGE_M3_FICHAS
from test_chroma_ingestion_integration import (  # noqa: F401
    DeterministicEmbedding,
    real_chroma_module,
)


class TokenizerFalso:

    def __init__(self, tokens_por_texto: int | None = None):
        self.tokens_por_texto = tokens_por_texto

    def encode(self, text, add_special_tokens=True, truncation=False):
        n = self.tokens_por_texto or len(text.split())
        return list(range(n))


def test_as_61_fichas_viram_61_registros_com_busca_e_leitura_separadas():
    preparado = ingest.prepare_fichas_ingestion(tokenizer=TokenizerFalso())
    fichas = json.loads(ingest.FICHAS_PATH.read_text(encoding="utf-8"))["fichas"]
    por_topico = {ficha["topic"]: ficha for ficha in fichas}

    assert len(preparado.ids) == 61
    assert preparado.recipe is BGE_M3_FICHAS
    for identificador, texto, metadado in zip(
        preparado.ids, preparado.documents, preparado.metadatas
    ):
        ficha = por_topico[metadado["topic"]]
        assert identificador == f"ficha__{ficha['topic']}"
        # O que vira vetor é o texto de busca, sem prefixo nenhum.
        assert texto == ficha["search_text"]
        # O que chega ao prompt (RetrievalClient: title + body) é a leitura.
        assert metadado["title"] == ficha["reading_title"]
        assert metadado["body"] == ficha["reading_text"]
        assert metadado["document_type"] == "triage_card"
        assert json.loads(metadado["references"]) == ficha["references"]
        assert all(
            isinstance(valor, (str, int, float, bool)) for valor in metadado.values()
        )


def test_ficha_acima_do_limite_da_receita_e_recusada():
    with pytest.raises(ingest.IngestionValidationError, match="acima do limite"):
        ingest.prepare_fichas_ingestion(
            tokenizer=TokenizerFalso(BGE_M3_FICHAS.max_tokens + 1)
        )


def test_texto_que_nao_bate_com_o_hash_e_recusado(tmp_path):
    payload = json.loads(ingest.FICHAS_PATH.read_text(encoding="utf-8"))
    payload["fichas"][0]["search_text"] += " frase acrescentada à mão"
    arquivo = tmp_path / "fichas.json"
    arquivo.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ingest.IngestionValidationError, match="search_text_sha256"):
        ingest.prepare_fichas_ingestion(
            tokenizer=TokenizerFalso(), fichas_path=arquivo
        )


def test_colecao_de_fichas_guarda_a_receita_e_abre_pelo_manifesto(
    real_chroma_module, tmp_path
):
    cliente = real_chroma_module.ChromaDBClient
    cliente.configure(
        path=tmp_path,
        collection_name="documents",
        embedding_function=DeterministicEmbedding(),
    )
    preparado = ingest.prepare_fichas_ingestion(tokenizer=TokenizerFalso())

    resultado = ingest.stage_fichas(preparado, activate=True)

    manifesto = resultado["manifest"]
    assert manifesto["profile"] == "fichas"
    assert manifesto["embedding"]["recipe_key"] == "bge-m3-fichas-v1"
    assert manifesto["chunking"]["recipe_sha256"] == BGE_M3_FICHAS.sha256()
    assert manifesto["chunks"]["count"] == 61
    assert cliente.active_recipe() is BGE_M3_FICHAS

    colecao = cliente.get_collection()
    assert colecao.count() == 61
    registro = colecao.get(ids=["ficha__chocolate_toxicosis"], include=["metadatas"])
    assert registro["metadatas"][0]["topic"] == "chocolate_toxicosis"
