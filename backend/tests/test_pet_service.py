import pytest

from conftest import SupabaseClientFalso

from app.exceptions.pet_exception import PetNotFoundException
from app.schemas.pet import PetCreate, PetUpdate, Species
from app.services import pet_service
from app.services.pet_service import PetService


@pytest.fixture(autouse=True)
def _supabase_falso(monkeypatch):

    cliente = SupabaseClientFalso()

    monkeypatch.setattr(
        pet_service, "get_supabase_client", lambda: cliente
    )

    return cliente


def _criar_pet(**overrides) -> dict:

    dados = {
        "tutor_id": "tutor-1",
        "name": "Bidu",
        "species": Species.CAO,
    }
    dados.update(overrides)

    return dados


def test_create_devolve_o_pet_com_id_e_datas():

    pet = PetService.create(PetCreate(**_criar_pet()))

    assert pet.id
    assert pet.tutor_id == "tutor-1"
    assert pet.name == "Bidu"
    assert pet.species == Species.CAO
    assert pet.created_at
    assert pet.updated_at


def test_get_de_pet_inexistente_leva_a_404():

    with pytest.raises(PetNotFoundException):
        PetService.get("nao-existe")


def test_list_by_tutor_so_traz_pets_daquele_tutor():

    PetService.create(PetCreate(**_criar_pet(tutor_id="t1", name="Bidu")))
    PetService.create(PetCreate(**_criar_pet(tutor_id="t2", name="Mia")))

    pets_t1 = PetService.list_by_tutor("t1")

    assert len(pets_t1) == 1
    assert pets_t1[0].name == "Bidu"


def test_update_altera_so_os_campos_enviados():

    criado = PetService.create(PetCreate(**_criar_pet(name="Bidu")))

    atualizado = PetService.update(
        criado.id, PetUpdate(weight_kg=12.5, neutered=True)
    )

    assert atualizado.weight_kg == 12.5
    assert atualizado.neutered is True
    assert atualizado.name == "Bidu"  # não mexeu no que não foi enviado


def test_update_de_pet_inexistente_leva_a_404():

    with pytest.raises(PetNotFoundException):
        PetService.update("nao-existe", PetUpdate(weight_kg=10))


def test_update_sem_nenhum_campo_devolve_o_pet_como_esta():

    criado = PetService.create(PetCreate(**_criar_pet()))

    devolvido = PetService.update(criado.id, PetUpdate())

    assert devolvido.id == criado.id
