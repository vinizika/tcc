import pytest

from conftest import MongoDatabaseFalso

from app.exceptions.conversation_exception import ConversationNotFoundException
from app.exceptions.persistence_exception import MongoNotConfiguredException
from app.schemas.triage_output import TriageResult
from app.services import conversation_service
from app.services.conversation_service import ConversationService


@pytest.fixture(autouse=True)
def _mongo_falso(monkeypatch):
    """
    `conversation_service` importa `get_mongo_database` por nome, então o
    dublê substitui o nome dentro do próprio módulo (mesmo padrão de
    `test_tutor_service.py`/`test_pet_service.py` para o Supabase).
    """

    database = MongoDatabaseFalso()

    monkeypatch.setattr(
        conversation_service, "get_mongo_database", lambda: database
    )

    return database


def test_append_turn_sem_conversation_id_cria_uma_nova():

    conversation_id = ConversationService.append_turn(
        tutor_message="meu cão vomitou",
        assistant_message="Entendido.",
    )

    assert conversation_id

    conversa = ConversationService.get(conversation_id)

    assert len(conversa.messages) == 2
    assert conversa.messages[0].role == "tutor"
    assert conversa.messages[0].content == "meu cão vomitou"
    assert conversa.messages[1].role == "assistente"


def test_append_turn_continua_a_mesma_conversa():

    primeiro = ConversationService.append_turn(
        tutor_message="oi", assistant_message="olá"
    )

    segundo = ConversationService.append_turn(
        tutor_message="ele vomitou de novo",
        assistant_message="entendido",
        conversation_id=primeiro,
    )

    assert segundo == primeiro

    conversa = ConversationService.get(primeiro)

    assert len(conversa.messages) == 4


def test_append_turn_grava_a_triagem_no_turno_do_assistente():

    triagem = TriageResult(
        classificacao="EMERGENCIA",
        justificativa="sinais graves",
        recomendacao="procure atendimento",
    )

    conversation_id = ConversationService.append_turn(
        tutor_message="convulsão",
        assistant_message="resposta",
        triage=triagem,
    )

    conversa = ConversationService.get(conversation_id)

    assert conversa.messages[1].triage.classificacao == "EMERGENCIA"
    assert conversa.messages[0].triage is None


def test_append_turn_guarda_tutor_id_e_pet_id():

    conversation_id = ConversationService.append_turn(
        tutor_message="oi",
        assistant_message="olá",
        tutor_id="tutor-1",
        pet_id="pet-1",
    )

    conversa = ConversationService.get(conversation_id)

    assert conversa.tutor_id == "tutor-1"
    assert conversa.pet_id == "pet-1"


def test_get_de_conversa_inexistente_leva_a_404():

    with pytest.raises(ConversationNotFoundException):
        ConversationService.get("nao-existe")


def test_append_turn_sem_mongo_configurado_nao_derruba_a_chamada(monkeypatch):

    def sem_mongo():
        raise MongoNotConfiguredException()

    monkeypatch.setattr(conversation_service, "get_mongo_database", sem_mongo)

    conversation_id = ConversationService.append_turn(
        tutor_message="oi", assistant_message="olá"
    )

    assert conversation_id is None
