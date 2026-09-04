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
