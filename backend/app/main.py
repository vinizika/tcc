from fastapi import FastAPI

from pydantic import BaseModel

from app.exceptions.handlers import (
    app_exception_handler,
    generic_exception_handler
)

from app.llm import chamar_llm_triagem
from app.core.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.exceptions.base_exception import BaseAppException

from app.api import health
from app.api import chat
from app.api import search

app = FastAPI(
    title=settings.API_NAME,
    version=settings.API_VERSION
)

app.add_middleware(LoggingMiddleware)

class TriagemRequest(BaseModel):
    relato: str
    especie: str | None = None
    idade: str | None = None

app.add_exception_handler(
    BaseAppException,
    app_exception_handler
)

app.add_exception_handler(
    Exception,
    generic_exception_handler
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(search.router)





# @app.post("/triagem")
# def triagem(payload: TriagemRequest):
#     resposta = chamar_llm_triagem(
#         relato=payload.relato,
#         especie=payload.especie,
#         idade=payload.idade,
#     )

#     return {
#         "entrada": payload.model_dump(),
#         "resposta_modelo": resposta,
#     }