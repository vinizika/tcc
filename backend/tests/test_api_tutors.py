"""
Contrato HTTP de /tutors/. A camada de dados (Supabase) já está coberta por
test_tutor_service.py; aqui o que importa é a tradução requisição → resposta
e os códigos de erro.
"""

import pytest
from fastapi.testclient import TestClient

from app.exceptions.tutor_exception import TutorNotFoundException
from app.main import app
from app.schemas.pet import PetResponse, Species
from app.schemas.tutor import TutorResponse
from app.services.pet_service import PetService
from app.services.tutor_service import TutorService


@pytest.fixture
def client():
    return TestClient(app)


def _tutor(**overrides) -> TutorResponse:

    dados = {
        "id": "tutor-1",
        "name": "Ana",
        "phone": None,
        "email": None,
        "created_at": "2026-01-01T00:00:00Z",
    }
    dados.update(overrides)

    return TutorResponse(**dados)


def test_criar_tutor(client, monkeypatch):

    monkeypatch.setattr(TutorService, "create", lambda data: _tutor(name=data.name))

    resposta = client.post("/tutors/", json={"name": "Ana"})

    assert resposta.status_code == 200
    assert resposta.json()["name"] == "Ana"


def test_buscar_tutor(client, monkeypatch):

    monkeypatch.setattr(TutorService, "get", lambda tutor_id: _tutor(id=tutor_id))

    resposta = client.get("/tutors/tutor-1")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == "tutor-1"


def test_buscar_tutor_inexistente_devolve_404(client, monkeypatch):

    def nao_encontrado(tutor_id):
        raise TutorNotFoundException(tutor_id)

    monkeypatch.setattr(TutorService, "get", nao_encontrado)

    resposta = client.get("/tutors/nao-existe")

    assert resposta.status_code == 404


def test_nome_vazio_e_recusado(client):

    resposta = client.post("/tutors/", json={"name": ""})

    assert resposta.status_code == 422


def test_listar_pets_do_tutor(client, monkeypatch):

    monkeypatch.setattr(TutorService, "get", lambda tutor_id: _tutor(id=tutor_id))
    monkeypatch.setattr(
        PetService,
        "list_by_tutor",
        lambda tutor_id: [
            PetResponse(
                id="pet-1",
                tutor_id=tutor_id,
                name="Bidu",
                species=Species.CAO,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ],
    )

    resposta = client.get("/tutors/tutor-1/pets")

    assert resposta.status_code == 200
    assert resposta.json()[0]["name"] == "Bidu"


def test_listar_pets_de_tutor_inexistente_devolve_404(client, monkeypatch):

    def nao_encontrado(tutor_id):
        raise TutorNotFoundException(tutor_id)

    monkeypatch.setattr(TutorService, "get", nao_encontrado)

    resposta = client.get("/tutors/nao-existe/pets")

    assert resposta.status_code == 404
