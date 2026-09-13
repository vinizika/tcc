import pytest

from conftest import SupabaseClientFalso

from app.exceptions.tutor_exception import TutorNotFoundException
from app.schemas.tutor import TutorCreate
from app.services import tutor_service
from app.services.tutor_service import TutorService


@pytest.fixture(autouse=True)
def _supabase_falso(monkeypatch):
    """
    `tutor_service` importa `get_supabase_client` por nome
    (`from ... import`), então o dublê precisa substituir o nome dentro do
    próprio módulo — substituir em `app.clients.supabase_client` não
    alcançaria a referência já importada (mesmo padrão de
    `test_api_health.py` com `get_ollama_client`).
    """

    cliente = SupabaseClientFalso()

    monkeypatch.setattr(
        tutor_service, "get_supabase_client", lambda: cliente
    )

    return cliente


def test_create_devolve_o_tutor_com_id_gerado():

    tutor = TutorService.create(TutorCreate(name="Ana"))

    assert tutor.name == "Ana"
    assert tutor.id
    assert tutor.phone is None


def test_get_encontra_o_tutor_criado():

    criado = TutorService.create(TutorCreate(name="Bruno", phone="11999999999"))

    encontrado = TutorService.get(criado.id)

    assert encontrado.id == criado.id
    assert encontrado.phone == "11999999999"


def test_get_de_tutor_inexistente_leva_a_404():

    with pytest.raises(TutorNotFoundException):
        TutorService.get("nao-existe")
