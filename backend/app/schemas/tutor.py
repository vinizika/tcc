from typing import Optional

from pydantic import BaseModel, Field


class TutorCreate(BaseModel):

    name: str = Field(min_length=1, max_length=200)

    # Nenhum dos dois é obrigatório: nesta fase de desenvolvimento, a
    # identidade do tutor não depende de autenticação, e nem todo tutor quer
    # dar telefone e e-mail. Validação de formato de e-mail fica para quando
    # existir login de verdade — hoje é só um dado de contato.
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=200)


class TutorResponse(BaseModel):

    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: str
