from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class AnimalInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    species: Literal["cao", "gato"]
    age: str | None = Field(default=None, max_length=80)
    weight_kg: float | None = Field(default=None, gt=0, le=150)
    breed: str | None = Field(default=None, max_length=100)
    relevant_history: str | None = Field(default=None, max_length=1000)


class ConversationInput(BaseModel):
    pet_id: str | None = None


class TurnInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=4000)
    request_id: str = Field(min_length=8, max_length=100)
    attendant_provider: Literal["gemini", "ollama"] | None = None


class LocationInput(BaseModel):
    consent: bool
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    accuracy_m: float | None = Field(default=None, ge=0, le=100000)
