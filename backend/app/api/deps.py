"""
Dependências das rotas.

O pipeline é construído sob demanda (não no import) e reaproveitado entre
requisições. Passar por Depends permite que os testes troquem o pipeline
real por um falso, sem subir Ollama nem banco vetorial.
"""

from functools import lru_cache

from app.pipeline.chat_pipeline import ChatPipeline


@lru_cache(maxsize=1)
def get_chat_pipeline() -> ChatPipeline:

    return ChatPipeline()
