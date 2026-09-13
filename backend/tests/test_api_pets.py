import pytest
from fastapi.testclient import TestClient

from app.exceptions.pet_exception import PetNotFoundException
from app.main import app
from app.schemas.pet import PetResponse, Species
from app.services.pet_service import PetService


@pytest.fixture
def client():
    return TestClient(app)


def _pet(**overrides) -> PetResponse:

    dados = {
        "id": "pet-1",
        "tutor_id": "tutor-1",
        "name": "Bidu",
        "species": Species.CAO,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    dados.update(overrides)

    return PetResponse(**dados)


def test_criar_pet(client, monkeypatch):

    monkeypatch.setattr(PetService, "create", lambda data: _pet(name=data.name))

    resposta = client.post(
        "/pets/",
        json={"tutor_id": "tutor-1", "name": "Bidu", "species": "cao"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["name"] == "Bidu"
    assert resposta.json()["species"] == "cao"


def test_criar_pet_com_especie_invalida_e_recusado(client):

    resposta = client.post(
        "/pets/",
        json={"tutor_id": "tutor-1", "name": "Bidu", "species": "hamster"},
    )

    assert resposta.status_code == 422


def test_buscar_pet(client, monkeypatch):

    monkeypatch.setattr(PetService, "get", lambda pet_id: _pet(id=pet_id))

    resposta = client.get("/pets/pet-1")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == "pet-1"


def test_buscar_pet_inexistente_devolve_404(client, monkeypatch):

    def nao_encontrado(pet_id):
        raise PetNotFoundException(pet_id)

    monkeypatch.setattr(PetService, "get", nao_encontrado)

    resposta = client.get("/pets/nao-existe")

    assert resposta.status_code == 404


def test_atualizar_pet(client, monkeypatch):

    capturado = {}

    def atualizar(pet_id, data):
        capturado["pet_id"] = pet_id
        capturado["data"] = data
        return _pet(id=pet_id, weight_kg=data.weight_kg)

    monkeypatch.setattr(PetService, "update", atualizar)

    resposta = client.patch("/pets/pet-1", json={"weight_kg": 12.5})

    assert resposta.status_code == 200
    assert resposta.json()["weight_kg"] == 12.5
    assert capturado["pet_id"] == "pet-1"


def test_peso_negativo_e_recusado(client):

    resposta = client.patch("/pets/pet-1", json={"weight_kg": -5})

    assert resposta.status_code == 422
