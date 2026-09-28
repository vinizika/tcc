"""
Peças comuns aos clientes do Gemini (rodada 26 do João).

O SDK `google-genai` é importado tarde, para quem nunca usa o Gemini não
precisar dele instalado. A chave vem só do ambiente (`GEMINI_API_KEY`) e
nunca aparece em log nem em mensagem de erro.
"""

import re
import threading
import time

_CHAVE = re.compile(r"(AIza[0-9A-Za-z_\-]{20,}|AQ\.[A-Za-z0-9_\-]+)")


def sem_chave(texto: str) -> str:
    """Tira de um texto qualquer coisa com formato de chave do Google."""

    return _CHAVE.sub("<chave>", str(texto))


def eh_cota_diaria(erro: Exception) -> bool:
    """
    O 429 do Gemini vem por limite por minuto ou por dia. Só é "cota do dia"
    quando todos os limites violados que a mensagem cita são diários: o
    limite por minuto passa com uma espera, o diário não.
    """

    texto = str(erro)
    ids = re.findall(r"quotaId'?\"?:\s*'?\"?([A-Za-z0-9_\-]+)", texto)
    if ids:
        return all("PerDay" in identificador for identificador in ids)
    return "per day" in texto.lower()


class Ritmo:
    """Espaça as chamadas para não estourar o limite por minuto."""

    def __init__(self, intervalo_s: float):
        self.intervalo_s = intervalo_s
        self._ultimo = 0.0
        self._trava = threading.Lock()

    def esperar(self) -> None:
        with self._trava:
            falta = self._ultimo + self.intervalo_s - time.monotonic()
            if falta > 0:
                time.sleep(falta)
            self._ultimo = time.monotonic()


def criar_cliente(api_key: str, timeout_s: float):
    from google import genai
    from google.genai import types

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
    )
