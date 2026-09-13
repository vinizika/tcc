"""
Cadastro do pet.

O campo mais importante deste arquivo não é uma coluna: é
`to_triage_context`, que traduz o cadastro estruturado em um parágrafo que
vai ao prompt do classificador. Cada campo existe porque muda uma decisão
clínica real, já registrada no mapa de assuntos do trilho B2
(data/curadoria/mapa-de-assuntos.csv) — não é ficha de cadastro por
completude.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Species(str, Enum):

    CAO = "cao"
    GATO = "gato"


class Sex(str, Enum):

    MACHO = "macho"
    FEMEA = "femea"


class PetBase(BaseModel):

    name: str = Field(min_length=1, max_length=100)
    species: Species
    breed: Optional[str] = Field(default=None, max_length=100)
    sex: Optional[Sex] = None

    # None é "não sei", diferente de False ("sei que não é castrado") — a
    # distinção importa para piometra e cio normal (mapa-de-assuntos.csv),
    # que dependem de saber que a fêmea é inteira, não só presumir.
    neutered: Optional[bool] = None

    birth_date: Optional[date] = None
    weight_kg: Optional[float] = Field(default=None, gt=0, le=150)

    vaccination_up_to_date: Optional[bool] = None
    last_vaccination_date: Optional[date] = None

    # Texto livre curto, não uma lista fechada: condições crônicas variam
    # demais para um enum, e o objetivo aqui é dar contexto ao classificador
    # ("cardiopata conhecido"), não estruturar um prontuário completo.
    chronic_conditions: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=500)


class PetCreate(PetBase):

    tutor_id: str


class PetUpdate(BaseModel):
    """
    Todos os campos opcionais: só o que vier na requisição é atualizado.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    species: Optional[Species] = None
    breed: Optional[str] = Field(default=None, max_length=100)
    sex: Optional[Sex] = None
    neutered: Optional[bool] = None
    birth_date: Optional[date] = None
    weight_kg: Optional[float] = Field(default=None, gt=0, le=150)
    vaccination_up_to_date: Optional[bool] = None
    last_vaccination_date: Optional[date] = None
    chronic_conditions: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=500)


class PetResponse(PetBase):

    id: str
    tutor_id: str
    created_at: str
    updated_at: str

    def _idade_aproximada(self) -> Optional[str]:

        if not self.birth_date:
            return None

        dias = (date.today() - self.birth_date).days

        if dias < 0:
            return None

        if dias < 60:
            return f"{dias // 7} semana(s) de vida (filhote)"

        if dias < 365:
            return f"{dias // 30} mes(es)"

        anos = dias // 365
        return f"{anos} ano(s)"

    def to_triage_context(self) -> str:
        """
        Um parágrafo curto, em português, para o prompt de triagem.

        Só inclui o que foi de fato preenchido — campo vazio não vira
        "não informado" no texto, para não inflar o prompt com ausências.
        """

        linhas = [f"Espécie: {'cão' if self.species == Species.CAO else 'gato'}."]

        idade = self._idade_aproximada()
        if idade:
            linhas.append(f"Idade aproximada: {idade}.")

        if self.breed:
            linhas.append(f"Raça: {self.breed}.")

        if self.sex:
            sexo = "macho" if self.sex == Sex.MACHO else "fêmea"
            if self.neutered is True:
                linhas.append(f"Sexo: {sexo}, castrado(a).")
            elif self.neutered is False:
                linhas.append(f"Sexo: {sexo}, não castrado(a).")
            else:
                linhas.append(f"Sexo: {sexo}.")

        if self.vaccination_up_to_date is True:
            linhas.append("Vacinação em dia.")
        elif self.vaccination_up_to_date is False:
            linhas.append("Vacinação atrasada ou incompleta.")

        if self.chronic_conditions:
            linhas.append(f"Condições crônicas conhecidas: {self.chronic_conditions}.")

        return " ".join(linhas)
