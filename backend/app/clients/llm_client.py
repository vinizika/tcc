"""
Cliente da classificação de urgência.

Responsável por chamar o modelo, validar a saída contra o formato esperado
e devolver, junto com o resultado, as informações que a avaliação precisa:
quantas tentativas foram necessárias, se a resposta era JSON, se seguia o
formato e quantos tokens foram gastos.
"""

import json
import time
from dataclasses import dataclass
from typing import Any, Optional, Type

import httpx
from ollama import ResponseError
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.logger import setup_logger
from app.core.ollama import default_options, get_ollama_client
from app.exceptions.attendant_exception import AttendantUnavailableException

logger = setup_logger("LLMClient")


MAX_ATTEMPTS = 2

# Trecho do erro de validação devolvido ao modelo na segunda tentativa.
# Mais que isso ocupa espaço do contexto sem ajudar.
ERROR_EXCERPT_CHARS = 300


@dataclass
class LLMCallResult:

    output: Optional[BaseModel]
    raw: str
    json_parsed: bool
    schema_valid: bool
    attempts: int
    done_reason: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    eval_duration_s: Optional[float] = None
    load_duration_s: Optional[float] = None
    # Procedência (rodada 25 do João): quem respondeu, desta vez.
    provider: str = "ollama"
    model: str = ""
    model_version: Optional[str] = None
    thinking: Optional[bool] = None
    # Preenchido pelo pipeline quando o provedor escolhido falhou e a troca
    # estava permitida: "gemini:gemini-3.5-flash-lite", por exemplo.
    fallback_from: Optional[str] = None


class LLMClient:

    provider = "ollama"

    def __init__(self, client=None):
        self._client = client or get_ollama_client()
        self._digests: dict[str, Optional[str]] = {}

    def model_version(self, model: str) -> Optional[str]:
        """O digest do modelo no Ollama, consultado uma vez por modelo."""

        if model not in self._digests:
            digest = None
            try:
                for item in self._client.list().models:
                    if item.model == model:
                        digest = item.digest
                        break
            except Exception as erro:  # a procedência não pode derrubar a triagem
                logger.warning(f"Não foi possível ler o digest de {model}: {erro}")
            self._digests[model] = digest
        return self._digests[model]

    def classify(
        self,
        messages: list[dict],
        output_model: Type[BaseModel],
        *,
        mode: str = "schema",
        options: Optional[dict[str, Any]] = None,
        keep_alive: Optional[str] = None,
        think: Optional[bool] = None,
        model: Optional[str] = None,
    ) -> LLMCallResult:

        options = dict(options or default_options())
        keep_alive = keep_alive or settings.LLM_KEEP_ALIVE
        modelo = model or settings.LLM_MODEL
        extra = {} if think is None else {"think": think}
        pensou = None

        # "schema" restringe a decodificação ao formato esperado, então os
        # nomes de campo e os valores de classificação saem exatos. "json"
        # garante apenas que a saída é um JSON, e existe para reproduzir a
        # medição antiga e para comparar as duas estratégias.
        formato = (
            output_model.model_json_schema()
            if mode == "schema"
            else "json"
        )

        mensagens = list(messages)

        bruto = ""
        json_parsed = False
        done_reason = None
        prompt_tokens = 0
        completion_tokens = 0
        eval_duration_s = None
        load_duration_s = None

        for tentativa in range(1, MAX_ATTEMPTS + 1):

            inicio = time.perf_counter()

            try:
                resposta = self._client.chat(
                    model=modelo,
                    messages=mensagens,
                    format=formato,
                    options=options,
                    keep_alive=keep_alive,
                    **extra,
                )

            except (httpx.ConnectError, httpx.ReadTimeout) as erro:
                raise AttendantUnavailableException(
                    f"Não foi possível falar com o Ollama em "
                    f"{settings.OLLAMA_HOST}: {erro}",
                    provider=self.provider,
                    model=modelo,
                    reason=type(erro).__name__,
                ) from erro

            except ResponseError as erro:
                raise AttendantUnavailableException(
                    f"O Ollama recusou a chamada ao modelo {modelo}: {erro}",
                    provider=self.provider,
                    model=modelo,
                    reason="ollama_response_error",
                ) from erro

            decorrido = time.perf_counter() - inicio

            bruto = (resposta["message"]["content"] or "").strip()
            done_reason = getattr(resposta, "done_reason", None)
            try:
                pensou = bool(resposta["message"].get("thinking"))
            except Exception:
                pensou = None

            prompt_tokens = getattr(resposta, "prompt_eval_count", 0) or 0
            completion_tokens = getattr(resposta, "eval_count", 0) or 0

            eval_duration_ns = getattr(resposta, "eval_duration", None)
            eval_duration_s = (
                eval_duration_ns / 1_000_000_000
                if eval_duration_ns
                else decorrido
            )

            load_duration_ns = getattr(resposta, "load_duration", None)
            load_duration_s = (
                load_duration_ns / 1_000_000_000
                if load_duration_ns
                else None
            )

            try:
                dados = json.loads(bruto)
                json_parsed = True
            except json.JSONDecodeError as erro:
                json_parsed = False
                erro_texto = f"A resposta não era um JSON válido: {erro}"
                dados = None

            if dados is not None:
                try:
                    validador = getattr(
                        output_model,
                        "model_validate_legado",
                        output_model.model_validate,
                    )

                    return LLMCallResult(
                        output=validador(dados),
                        raw=bruto,
                        json_parsed=True,
                        schema_valid=True,
                        attempts=tentativa,
                        done_reason=done_reason,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        eval_duration_s=eval_duration_s,
                        load_duration_s=load_duration_s,
                        provider=self.provider,
                        model=modelo,
                        model_version=self.model_version(modelo),
                        thinking=pensou,
                    )

                except ValidationError as erro:
                    erro_texto = (
                        f"A resposta não seguiu o formato: {erro}"
                    )

            if tentativa >= MAX_ATTEMPTS:
                break

            # Resposta cortada por limite de tokens: repetir com o mesmo
            # prompt e mais espaço. Anexar a mensagem de erro só faria a
            # segunda tentativa ser cortada no mesmo ponto.
            if done_reason == "length":
                logger.warning(
                    "Resposta truncada pelo limite de tokens; "
                    "repetindo com o dobro de espaço"
                )
                atual = options.get(
                    "num_predict",
                    settings.LLM_NUM_PREDICT,
                )
                if atual and atual > 0:
                    options["num_predict"] = atual * 2

            else:
                logger.warning(
                    f"Saída inválida na tentativa {tentativa}; "
                    "repetindo com o erro anexado"
                )
                mensagens = mensagens + [
                    {"role": "assistant", "content": bruto},
                    {
                        "role": "user",
                        "content": (
                            f"{erro_texto[:ERROR_EXCERPT_CHARS]}\n"
                            "Responda novamente apenas com o JSON no "
                            "formato pedido."
                        ),
                    },
                ]

        logger.error(
            "O modelo não devolveu uma resposta válida após "
            f"{MAX_ATTEMPTS} tentativas"
        )

        return LLMCallResult(
            output=None,
            raw=bruto,
            json_parsed=json_parsed,
            schema_valid=False,
            attempts=MAX_ATTEMPTS,
            done_reason=done_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            eval_duration_s=eval_duration_s,
            load_duration_s=load_duration_s,
            provider=self.provider,
            model=modelo,
            model_version=self.model_version(modelo),
            thinking=pensou,
        )
