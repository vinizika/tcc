"""
O retrato da versão do sistema é o que torna duas rodadas de avaliação
comparáveis. Estes testes cobrem o contrato dele e, principalmente, a
garantia de que nenhuma parte indisponível derruba a requisição.
"""

import sys

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.fingerprint_service import FingerprintService


@pytest.fixture
def cliente():
    return TestClient(app)


def test_health_continua_simples(cliente):
    """
    O healthcheck do docker compose depende desta resposta exata.
    """

    resposta = cliente.get("/health/")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_fingerprint_traz_as_quatro_partes(cliente):

    corpo = cliente.get("/health/fingerprint").json()

    assert corpo["model"]["name"]
    assert "ollama_version" in corpo
    assert "chunk_count" in corpo["vector_store"]
    assert "v0_legacy_sha256" in corpo["prompts"]
    assert corpo["defaults"]["seed"] == 42


def test_hash_do_prompt_muda_quando_o_texto_muda(monkeypatch):
    """
    É o que permite descobrir, meses depois, que dois números diferentes
    vieram de prompts diferentes e não da mudança que estava sendo testada.
    """

    from app.prompts import triage

    antes = FingerprintService._prompts()["v1_grounded_sha256"]

    monkeypatch.setattr(
        triage,
        "SISTEMA_ANCORADO",
        triage.SISTEMA_ANCORADO + " ajuste",
    )

    depois = FingerprintService._prompts()["v1_grounded_sha256"]

    assert antes != depois


def test_retrato_cobre_os_prompts_de_cot(monkeypatch):
    """
    O Chain-of-Thought é um prompt diferente, e o hash é o que permite
    descobrir, meses depois, que duas rodadas usaram textos diferentes.
    """

    prompts = FingerprintService._prompts()

    for chave in (
        "v1_grounded_cot_sha256",
        "v1_grounded_cot_sem_contexto_sha256",
        "v1_grounded_cot_posthoc_sha256",
    ):
        assert prompts[chave]

    # O braço de controle muda só a posição de um campo. Se os dois hashes
    # fossem iguais, o retrato não distinguiria os dois experimentos.
    assert (
        prompts["v1_grounded_cot_sha256"]
        != prompts["v1_grounded_cot_posthoc_sha256"]
    )


def test_ollama_indisponivel_nao_derruba_a_resposta(cliente, monkeypatch):
    """
    O retrato é informativo: se uma parte não responde, ela vira nulo com o
    erro registrado, e o resto continua servindo.
    """

    def explodir():
        raise ConnectionError("ollama fora do ar")

    monkeypatch.setattr(
        "app.services.fingerprint_service.get_ollama_client",
        explodir,
    )

    resposta = cliente.get("/health/fingerprint")

    assert resposta.status_code == 200
    assert resposta.json()["model"]["digest"] is None
    assert "ollama fora do ar" in resposta.json()["model"]["error"]


def test_hash_dos_ids_ignora_a_ordem_de_leitura(monkeypatch):
    """
    O banco vetorial não garante ordem. Sem ordenar, o hash mudaria entre
    rodadas sem nenhuma alteração real na base.
    """

    class ColecaoFalsa:
        name = "veterinary_documents"

        def __init__(self, ids):
            self._ids = ids

        def get(self, include=None):
            return {"ids": list(self._ids)}

    # O conftest instala o dublê do banco direto em sys.modules, sem criar
    # o pacote intermediário; é por lá que o serviço o encontra.
    modulo = sys.modules["app.database.chroma_client"]

    def usar(ids):
        monkeypatch.setattr(
            modulo.ChromaDBClient,
            "get_collection",
            staticmethod(lambda: ColecaoFalsa(ids)),
        )
        return FingerprintService._base_vetorial()

    primeiro = usar(["c1", "c2", "c3"])
    segundo = usar(["c3", "c1", "c2"])

    assert primeiro["chunk_ids_sha256"] == segundo["chunk_ids_sha256"]
    assert primeiro["chunk_count"] == 3


def test_base_diferente_muda_o_hash(monkeypatch):

    class ColecaoFalsa:
        name = "veterinary_documents"

        def __init__(self, ids):
            self._ids = ids

        def get(self, include=None):
            return {"ids": list(self._ids)}

    modulo = sys.modules["app.database.chroma_client"]

    def usar(ids):
        monkeypatch.setattr(
            modulo.ChromaDBClient,
            "get_collection",
            staticmethod(lambda: ColecaoFalsa(ids)),
        )
        return FingerprintService._base_vetorial()["chunk_ids_sha256"]

    assert usar(["c1", "c2"]) != usar(["c1", "c2", "c3"])


# ----------------------------------------------------------------------
# Identidade do conteúdo da base (evidencias/backlog.md#b-29)
# ----------------------------------------------------------------------


class ColecaoComConteudo:
    """
    Dublê que devolve texto e metadados, como o ChromaDB real.

    Os dublês acima devolvem só os ids, de propósito: eles cobrem o campo
    antigo, que não pode mudar de definição.
    """

    name = "veterinary_documents"

    def __init__(self, ids, documentos, metadados=None):
        self._ids = list(ids)
        self._documentos = list(documentos)
        self._metadados = list(metadados or [{} for _ in ids])

    def get(self, include=None):
        return {
            "ids": list(self._ids),
            "documents": list(self._documentos),
            "metadatas": list(self._metadados),
        }


def _base_com(monkeypatch, colecao) -> dict:

    modulo = sys.modules["app.database.chroma_client"]

    monkeypatch.setattr(
        modulo.ChromaDBClient,
        "get_collection",
        staticmethod(lambda: colecao),
    )

    return FingerprintService._base_vetorial()


def test_texto_reescrito_muda_o_hash_de_conteudo(monkeypatch):
    """
    O critério do B-29. O id é derivado de arquivo, página e índice, então
    reescrever um protocolo sem mudar o recorte mantinha o retrato idêntico
    — e duas rodadas pareciam ter usado a mesma base.
    """

    antes = _base_com(
        monkeypatch,
        ColecaoComConteudo(["c1", "c2"], ["convulsão focal", "dose de O2"]),
    )

    depois = _base_com(
        monkeypatch,
        ColecaoComConteudo(["c1", "c2"], ["convulsão FOCAL", "dose de O2"]),
    )

    assert antes["chunk_ids_sha256"] == depois["chunk_ids_sha256"]
    assert antes["content_sha256"] != depois["content_sha256"]


def test_metadado_reescrito_muda_o_hash_de_conteudo(monkeypatch):
    """
    Título e fonte vão ao prompt do classificador; os demais descrevem a
    procedência do trecho. Mudança em qualquer um é mudança de base.
    """

    antes = _base_com(
        monkeypatch,
        ColecaoComConteudo(
            ["c1"], ["texto"], [{"title": "Convulsões", "species": "dog"}]
        ),
    )

    depois = _base_com(
        monkeypatch,
        ColecaoComConteudo(
            ["c1"], ["texto"], [{"title": "Convulsões", "species": "cat"}]
        ),
    )

    assert antes["content_sha256"] != depois["content_sha256"]


def test_hash_de_conteudo_ignora_a_ordem_de_leitura(monkeypatch):
    """
    Pelo mesmo motivo do hash dos ids: o banco não garante ordem, e um hash
    que dependesse dela acusaria mudança a cada reinício.
    """

    primeiro = _base_com(
        monkeypatch,
        ColecaoComConteudo(["c1", "c2"], ["alfa", "beta"]),
    )

    segundo = _base_com(
        monkeypatch,
        ColecaoComConteudo(["c2", "c1"], ["beta", "alfa"]),
    )

    assert primeiro["content_sha256"] == segundo["content_sha256"]


def test_ordem_dos_metadados_nao_muda_o_hash(monkeypatch):

    primeiro = _base_com(
        monkeypatch,
        ColecaoComConteudo(["c1"], ["texto"], [{"a": "1", "b": "2"}]),
    )

    segundo = _base_com(
        monkeypatch,
        ColecaoComConteudo(["c1"], ["texto"], [{"b": "2", "a": "1"}]),
    )

    assert primeiro["content_sha256"] == segundo["content_sha256"]


def test_base_sem_conteudo_no_dublê_nao_quebra(monkeypatch):
    """
    Um banco que não devolva documentos (ou um dublê antigo) precisa seguir
    respondendo: o retrato é informativo e não pode derrubar a rota.
    """

    class SoIds:
        name = "veterinary_documents"

        def get(self, include=None):
            return {"ids": ["c1", "c2"]}

    base = _base_com(monkeypatch, SoIds())

    assert base["chunk_count"] == 2
    assert base["content_sha256"] is not None


def test_retrato_descreve_o_embedder_e_o_chunking(monkeypatch):
    """
    Mesmo texto com embedder diferente recupera outra coisa. Sem isto, duas
    rodadas podem declarar a mesma base e não serem o mesmo sistema.
    """

    base = _base_com(
        monkeypatch,
        ColecaoComConteudo(["c1"], ["texto"]),
    )

    assert "MiniLM" in base["embedding_model"]
    assert len(base["embedding_revision"]) == 40
    assert len(base["recipe_sha256"]) == 64
    assert base["chunking"]["target_tokens"] > 0
    assert base["chunking"]["max_tokens"] > 0


def test_retrato_preserva_inventario_e_manifesto_da_rodada(monkeypatch):
    modulo = sys.modules["app.database.chroma_client"]
    collection = ColecaoComConteudo(
        ["c1", "c2"],
        ["texto 1", "texto 2"],
        [
            {
                "topic": "heatstroke",
                "species": "dog",
                "source_file": "paper.pdf",
                "validation_status": "pending_specialist",
            },
            {
                "topic": "heatstroke",
                "species": "dog",
                "source_file": "paper.pdf",
                "validation_status": "pending_specialist",
            },
        ],
    )
    monkeypatch.setattr(
        modulo.ChromaDBClient,
        "get_collection",
        staticmethod(lambda: collection),
    )
    monkeypatch.setattr(
        modulo.ChromaDBClient,
        "load_manifest",
        staticmethod(
            lambda name, required=False: {
                "profile": "experimental",
                "sources": {"source_set_sha256": "fontes"},
            }
        ),
        raising=False,
    )

    base = FingerprintService._base_vetorial()

    assert base["document_count"] == 1
    assert base["topic_counts"] == {"heatstroke": 2}
    assert base["species_counts_by_topic"] == {"heatstroke": {"dog": 2}}
    assert base["source_set_sha256"] == "fontes"
    assert base["profile"] == "experimental"


def test_base_indisponivel_nao_derruba_a_resposta(cliente, monkeypatch):

    modulo = sys.modules["app.database.chroma_client"]

    def explodir():
        raise RuntimeError("banco fora do ar")

    monkeypatch.setattr(
        modulo.ChromaDBClient,
        "get_collection",
        staticmethod(explodir),
    )

    resposta = cliente.get("/health/fingerprint")

    assert resposta.status_code == 200
    assert resposta.json()["vector_store"]["chunk_count"] is None
    assert "banco fora do ar" in resposta.json()["vector_store"]["error"]


def test_fingerprint_prefere_inspecao_sem_embedding(monkeypatch):
    """A rota de saúde não pode carregar modelo nem tocar a rede."""

    modulo = sys.modules["app.database.chroma_client"]
    collection = ColecaoComConteudo(["c1"], ["texto"], [{"topic": "demo"}])

    def consulta_vetorial_indevida():
        raise AssertionError("o fingerprint tentou abrir a coleção para query")

    monkeypatch.setattr(
        modulo.ChromaDBClient,
        "get_collection",
        staticmethod(consulta_vetorial_indevida),
    )
    monkeypatch.setattr(
        modulo.ChromaDBClient,
        "get_collection_for_inspection",
        staticmethod(lambda: collection),
        raising=False,
    )

    base = FingerprintService._base_vetorial()

    assert base["chunk_count"] == 1
    assert "error" not in base
