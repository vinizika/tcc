"""
O Gemini como atendente (rodada 26 do João).

Mesma interface do `LLMClient` (Ollama): recebe as mensagens e o formato de
saída, devolve um `LLMCallResult` com a saída validada, as tentativas, os
tokens e a procedência. Porte do cliente usado na autópsia 2
(rodadas 18 a 21), com três regras:

1. **Nunca troca de modelo e nunca chama o Ollama.** Se o Gemini falha, a
   chamada falha com `AttendantUnavailableException`; quem decide se há troca
   é o pipeline, pela configuração, e a troca fica registrada.
2. **Limite por minuto (429) e falta de capacidade (503)**: espera e tenta de
   novo, com recuo crescente, até um teto.
3. **Cota do dia esgotada**: passa na hora para a próxima chave configurada
   (`GEMINI_API_KEYS`, deploy de 19/10); quando não sobra nenhuma,
   `QuotaExhaustedException`, sem gastar tentativas. Trocar de chave não troca
   de modelo.

Saída inválida duas vezes (JSON quebrado ou fora do formato, inclusive
resposta vazia) devolve `output=None`, e o pipeline responde INCERTO, como
com o Ollama.
"""

import json
import time
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from app.clients.gemini_common import ChavesGemini, Ritmo, criar_cliente, eh_cota_diaria, sem_chave
from app.clients.llm_client import LLMCallResult
from app.core.config import settings
from app.core.logger import setup_logger
from app.exceptions.attendant_exception import (
    AttendantUnavailableException,
    QuotaExhaustedException,
)

logger = setup_logger("GeminiLLMClient")

MAX_ATTEMPTS = 2
MIN_OUTPUT_TOKENS = 600
LEMBRETE_DE_FORMATO = (
    "\n\nA resposta anterior não seguiu o formato. Responda só com o JSON pedido."
)


class GeminiLLMClient:

    provider = "gemini"

    def __init__(
        self,
        client=None,
        model: Optional[str] = None,
        dormir=time.sleep,
        fabrica=criar_cliente,
    ):
        # `client` fixo (testes) desliga a troca de chave; sem ele, um cliente
        # por chave, criado pela `fabrica` quando a chave é usada pela 1ª vez.
        self._client = client
        self._clientes: dict[int, Any] = {}
        self._fabrica = fabrica
        self.model = model or settings.GEMINI_MODEL
        self._ritmo = Ritmo(settings.GEMINI_MIN_INTERVAL_S)
        self._dormir = dormir

    def _chaves(self) -> list[str]:
        return ChavesGemini.lista(settings.GEMINI_API_KEY, settings.GEMINI_API_KEYS)

    def _cliente(self, indice: int):
        if self._client is not None:
            return self._client
        if indice not in self._clientes:
            self._clientes[indice] = self._fabrica(
                self._chaves()[indice], settings.GEMINI_TIMEOUT_S
            )
        return self._clientes[indice]

    def _escolher(self) -> int:
        """A primeira chave com cota no dia."""

        if self._client is not None:
            return 0
        chaves = self._chaves()
        if not chaves:
            raise AttendantUnavailableException(
                "GEMINI_API_KEY não configurada: o atendente padrão é o "
                "Gemini. Defina a chave no .env ou escolha o atendente "
                "local (ATTENDANT_PROVIDER=ollama ou o preset local_qwen).",
                provider=self.provider,
                model=self.model,
                reason="missing_api_key",
            )
        for indice in range(len(chaves)):
            if ChavesGemini.disponivel(indice):
                return indice
        raise QuotaExhaustedException(
            "A cota diária do Gemini acabou em todas as chaves configuradas.",
            provider=self.provider,
            model=self.model,
            reason="daily_quota",
        )

    def _gerar(self, sistema, usuario, schema, temperatura, seed, max_tokens):
        """Uma chamada, com as esperas do 429 por minuto e do 503."""

        from google.genai import errors as genai_errors
        from google.genai import types

        config: dict[str, Any] = {
            "temperature": temperatura,
            "max_output_tokens": max_tokens,
            "response_mime_type": "application/json",
            "response_json_schema": schema,
        }
        if seed is not None:
            config["seed"] = seed
        if sistema:
            config["system_instruction"] = sistema

        espera_429, espera_503 = 5.0, 20.0
        n_429 = n_503 = 0
        while True:
            indice = self._escolher()
            self._ritmo.esperar()
            try:
                return self._cliente(indice).models.generate_content(
                    model=self.model,
                    contents=usuario,
                    config=types.GenerateContentConfig(**config),
                )
            except genai_errors.ClientError as erro:
                if getattr(erro, "code", None) != 429:
                    raise AttendantUnavailableException(
                        f"O Gemini recusou a chamada: {sem_chave(erro)[:300]}",
                        provider=self.provider,
                        model=self.model,
                        reason=f"http_{getattr(erro, 'code', 'erro')}",
                    ) from erro
                if eh_cota_diaria(erro):
                    if self._client is not None:
                        raise QuotaExhaustedException(
                            "A cota diária do Gemini acabou para esta chave.",
                            provider=self.provider,
                            model=self.model,
                            reason="daily_quota",
                        ) from erro
                    # Passa para a próxima chave na hora; se não houver,
                    # `_escolher` levanta a cota esgotada na volta seguinte.
                    ChavesGemini.marcar_esgotada(indice)
                    logger.warning(
                        f"Gemini: cota do dia esgotada na chave {indice + 1} de "
                        f"{len(self._chaves())}; passando para a seguinte"
                    )
                    continue
                n_429 += 1
                if n_429 > settings.GEMINI_MAX_RETRIES_429:
                    raise AttendantUnavailableException(
                        "O Gemini seguiu no limite por minuto depois de "
                        f"{n_429 - 1} esperas.",
                        provider=self.provider,
                        model=self.model,
                        reason="rate_limit",
                    ) from erro
                logger.warning(f"Gemini 429 (por minuto); esperando {espera_429:.0f}s")
                self._dormir(espera_429)
                espera_429 = min(espera_429 * 2, 120.0)
            except genai_errors.ServerError as erro:
                n_503 += 1
                if n_503 > settings.GEMINI_MAX_RETRIES_503:
                    raise AttendantUnavailableException(
                        "O Gemini seguiu sem capacidade depois de "
                        f"{n_503 - 1} esperas.",
                        provider=self.provider,
                        model=self.model,
                        reason="server_unavailable",
                    ) from erro
                logger.warning(f"Gemini {getattr(erro, 'code', None) or '5xx'}; esperando {espera_503:.0f}s")
                self._dormir(espera_503)
                espera_503 = min(espera_503 * 2, 300.0)
            except (AttendantUnavailableException, QuotaExhaustedException):
                raise
            except Exception as erro:  # rede, timeout: falha explícita, sem troca
                raise AttendantUnavailableException(
                    f"Não foi possível falar com o Gemini: {sem_chave(erro)[:300]}",
                    provider=self.provider,
                    model=self.model,
                    reason=type(erro).__name__,
                ) from erro

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

        del mode, keep_alive, think, model  # o modelo do Gemini é o da configuração
        options = dict(options or {})
        sistema = "\n\n".join(m["content"] for m in messages if m["role"] == "system") or None
        usuario = "\n\n".join(m["content"] for m in messages if m["role"] != "system")
        schema = output_model.model_json_schema()

        bruto, json_parsed, versao = "", False, None
        prompt_tokens = completion_tokens = 0
        inicio = time.perf_counter()
        for tentativa in range(1, MAX_ATTEMPTS + 1):
            resposta = self._gerar(
                sistema,
                usuario if tentativa == 1 else usuario + LEMBRETE_DE_FORMATO,
                schema,
                options.get("temperature", settings.LLM_TEMPERATURE),
                options.get("seed", settings.LLM_SEED),
                max(int(options.get("num_predict") or MIN_OUTPUT_TOKENS), MIN_OUTPUT_TOKENS),
            )
            bruto = (getattr(resposta, "text", None) or "").strip()
            versao = getattr(resposta, "model_version", None) or versao
            uso = getattr(resposta, "usage_metadata", None)
            prompt_tokens = getattr(uso, "prompt_token_count", 0) or 0
            completion_tokens = getattr(uso, "candidates_token_count", 0) or 0
            try:
                dados = json.loads(bruto)
                json_parsed = True
                saida = output_model.model_validate(dados)
            except (json.JSONDecodeError, ValidationError):
                logger.warning(f"Gemini: saída inválida na tentativa {tentativa}")
                continue
            return LLMCallResult(
                output=saida,
                raw=bruto,
                json_parsed=True,
                schema_valid=True,
                attempts=tentativa,
                done_reason="stop",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                eval_duration_s=time.perf_counter() - inicio,
                provider=self.provider,
                model=self.model,
                model_version=versao,
                thinking=None,
            )

        return LLMCallResult(
            output=None,
            raw=bruto,
            json_parsed=json_parsed,
            schema_valid=False,
            attempts=MAX_ATTEMPTS,
            done_reason="invalid",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            eval_duration_s=time.perf_counter() - inicio,
            provider=self.provider,
            model=self.model,
            model_version=versao,
            thinking=None,
        )
