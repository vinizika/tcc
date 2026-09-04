from functools import lru_cache
from typing import Any

from ollama import Client

from app.core.config import settings


@lru_cache(maxsize=1)
def get_ollama_client() -> Client:
    """
    Cliente compartilhado do Ollama.

    Existe para que o endereço do servidor fique em um lugar só: dentro do
    docker compose ele aponta para o container, fora dele para a máquina
    local. Antes, o endereço estava escrito à mão em cada arquivo, e o
    projeto só funcionava em um dos dois cenários por vez.
    """

    return Client(
        host=settings.OLLAMA_HOST,
        timeout=settings.LLM_TIMEOUT_S,
    )


def default_options(**overrides: Any) -> dict[str, Any]:
    """
    Opções padrão de geração.

    Temperatura e seed fixas mantêm as rodadas de avaliação comparáveis
    entre si. Os valores podem ser sobrescritos por chamada, o que é usado
    pelo runner de avaliação para variar um parâmetro por vez.
    """

    options: dict[str, Any] = {
        "temperature": settings.LLM_TEMPERATURE,
        "seed": settings.LLM_SEED,
        "num_ctx": settings.LLM_NUM_CTX,
        "num_predict": settings.LLM_NUM_PREDICT,
    }

    options.update(
        {
            key: value
            for key, value in overrides.items()
            if value is not None
        }
    )

    return options
