"""
`to_triage_context` traduz o cadastro do pet em texto de prompt. Cada campo
testado aqui corresponde a um discriminador real do mapa de assuntos do
trilho B2 (data/curadoria/mapa-de-assuntos.csv) — não é cobertura por
completude.
"""

from datetime import date, timedelta

from app.schemas.pet import PetResponse, Sex, Species


def pet(**overrides) -> PetResponse:

    dados = {
        "id": "pet-1",
        "tutor_id": "tutor-1",
        "name": "Rex",
        "species": Species.CAO,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    dados.update(overrides)

    return PetResponse(**dados)


def test_contexto_minimo_traz_so_a_especie():

    assert pet().to_triage_context() == "Espécie: cão."


def test_especie_gato():

    assert "gato" in pet(species=Species.GATO).to_triage_context()


def test_idade_em_anos():

    nascimento = date.today() - timedelta(days=800)

    assert "2 ano(s)" in pet(birth_date=nascimento).to_triage_context()


def test_idade_de_filhote_em_semanas():

    nascimento = date.today() - timedelta(days=30)

    texto = pet(birth_date=nascimento).to_triage_context()

    assert "semana(s) de vida (filhote)" in texto


def test_data_de_nascimento_no_futuro_nao_vira_idade():
    """
    Cadastro com erro de digitação não deve produzir uma idade negativa no
    prompt — melhor omitir do que mandar informação absurda ao modelo.
    """

    nascimento = date.today() + timedelta(days=5)

    assert "Idade" not in pet(birth_date=nascimento).to_triage_context()


def test_sexo_e_castracao_sabida():

    texto = pet(sex=Sex.FEMEA, neutered=False).to_triage_context()

    assert "fêmea, não castrado(a)" in texto


def test_sexo_sem_informacao_de_castracao():

    texto = pet(sex=Sex.MACHO, neutered=None).to_triage_context()

    assert "Sexo: macho." in texto
    assert "castrado" not in texto


def test_vacinacao_em_dia_e_atrasada():

    assert "Vacinação em dia." in pet(
        vaccination_up_to_date=True
    ).to_triage_context()

    assert "Vacinação atrasada ou incompleta." in pet(
        vaccination_up_to_date=False
    ).to_triage_context()


def test_condicoes_cronicas_entram_no_texto():

    texto = pet(chronic_conditions="cardiopata conhecida").to_triage_context()

    assert "cardiopata conhecida" in texto


def test_campos_vazios_nao_aparecem_como_nao_informado():
    """
    Cadastro incompleto não deve inflar o prompt com "não informado" — só o
    que foi de fato preenchido vira texto.
    """

    texto = pet().to_triage_context()

    assert "não informado" not in texto.lower()
