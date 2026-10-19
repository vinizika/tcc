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


class ChavesGemini:
    """
    As chaves do Gemini e quais estão com a cota do dia esgotada (deploy de
    19/10). A primeira é `GEMINI_API_KEY`; as seguintes, `GEMINI_API_KEYS`
    (separadas por vírgula). Uma chave marcada como esgotada volta a valer na
    virada da cota do Google, à meia-noite do Pacífico: 08:00 UTC no horário
    padrão e 07:00 no de verão — usamos 08:00, que serve aos dois, ao custo de
    esperar uma hora a mais no verão. O registro é do processo inteiro, para
    valer também para os clientes criados a cada chamada.

    Trocar de chave não troca de modelo: o modelo e o provedor continuam os
    mesmos, e a procedência da resposta não muda.
    """

    _esgotadas: dict[int, float] = {}
    _trava = threading.Lock()

    @staticmethod
    def lista(principal: str, extras: str) -> list[str]:
        chaves = [principal] + (extras or "").split(",")
        vistas, saida = set(), []
        for chave in (c.strip() for c in chaves):
            if chave and chave not in vistas:
                vistas.add(chave)
                saida.append(chave)
        return saida

    @staticmethod
    def proxima_virada(agora: float) -> float:
        dia = 86400
        virada = agora - (agora % dia) + 8 * 3600
        return virada if virada > agora else virada + dia

    @classmethod
    def marcar_esgotada(cls, indice: int, agora: float | None = None) -> None:
        agora = time.time() if agora is None else agora
        with cls._trava:
            cls._esgotadas[indice] = cls.proxima_virada(agora)

    @classmethod
    def disponivel(cls, indice: int, agora: float | None = None) -> bool:
        agora = time.time() if agora is None else agora
        with cls._trava:
            ate = cls._esgotadas.get(indice)
            if ate is not None and agora >= ate:
                del cls._esgotadas[indice]
                return True
            return ate is None

    @classmethod
    def esquecer(cls) -> None:
        with cls._trava:
            cls._esgotadas.clear()


def criar_cliente(api_key: str, timeout_s: float):
    from google import genai
    from google.genai import types

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
    )
