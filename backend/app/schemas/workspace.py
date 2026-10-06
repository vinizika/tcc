from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

# O que do cadastro vai à IA (decisão e seleção de pergunta), nesta ordem. Sexo,
# castração e gestação entraram na rodada 24 do Ryu: na rodada 20 dele,
# decidiram 4 de 8 pares de casos e não tinham campo no cadastro.
ANIMAL_CONTEXT_FIELDS = ("name", "species", "age", "weight_kg", "breed", "relevant_history",
                         "sex", "neutered", "reproductive_status")


class AnimalInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    species: Literal["cao", "gato"]
    age: str | None = Field(default=None, max_length=80)
    weight_kg: float | None = Field(default=None, gt=0, le=150)
    breed: str | None = Field(default=None, max_length=100)
    relevant_history: str | None = Field(default=None, max_length=1000)
    sex: Literal["macho", "femea"] | None = None
    neutered: bool | None = None
    reproductive_status: Literal["prenhe", "amamentando"] | None = None

    @model_validator(mode="after")
    def gestacao_so_em_femea(self):
        if self.reproductive_status and self.sex == "macho":
            raise ValueError("Gestação ou amamentação só se aplica a fêmeas.")
        return self


class ConversationInput(BaseModel):
    pet_id: str | None = None


class TurnInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=4000)
    request_id: str = Field(min_length=8, max_length=100)
    origin: Literal["text", "form"] = "text"
    question_id: str | None = None
    selected_option: str | None = Field(default=None, max_length=150)
    attendant_provider: Literal["gemini", "ollama"] | None = None


class LocationInput(BaseModel):
    consent: bool
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    accuracy_m: float | None = Field(default=None, ge=0, le=100000)
