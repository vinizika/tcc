"""
Identificação da versão do sistema, para as rodadas de avaliação.

Cada rodada grava este retrato no manifesto. Ele responde à pergunta que
aparece quando duas rodadas discordam: mudou o que estávamos testando, ou
mudou o modelo, a base de conhecimento ou os prompts?

Nada aqui pode derrubar a requisição: se uma parte não responder, ela vira
`null` com o erro registrado, e o resto do retrato continua útil.
"""

import hashlib

import httpx

from app.core.config import settings
from app.core.logger import setup_logger
from app.core.ollama import get_ollama_client

logger = setup_logger("FingerprintService")


def _sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


class FingerprintService:

    @staticmethod
    def _modelo() -> dict:
        """
        Identidade do modelo: o digest é o que garante que duas rodadas
        usaram exatamente os mesmos pesos, já que uma etiqueta como
        "llama3.2:3b" pode ser reapontada para outra versão.
        """

        informacoes = {
            "name": settings.LLM_MODEL,
            "digest": None,
            "size_bytes": None,
            "parameter_size": None,
            "quantization": None,
            "loaded_in_vram_bytes": None,
        }

        try:
            cliente = get_ollama_client()

            for modelo in cliente.list().models:
                if modelo.model == settings.LLM_MODEL:
                    informacoes["digest"] = modelo.digest
                    informacoes["size_bytes"] = modelo.size

                    if modelo.details:
                        informacoes["parameter_size"] = (
                            modelo.details.parameter_size
                        )
                        informacoes["quantization"] = (
                            modelo.details.quantization_level
                        )
                    break

            # Se o modelo estiver carregado, size_vram > 0 indica GPU. Sem
            # isso, comparar tempos entre máquinas não faz sentido.
            for carregado in cliente.ps().models:
                if carregado.model == settings.LLM_MODEL:
                    informacoes["loaded_in_vram_bytes"] = carregado.size_vram
                    break

        except Exception as erro:
            logger.warning(f"Não foi possível consultar o modelo: {erro}")
            informacoes["error"] = str(erro)

        return informacoes

    @staticmethod
    def _ollama_version() -> str | None:

        try:
            resposta = httpx.get(
                f"{settings.OLLAMA_HOST}/api/version",
                timeout=5,
            )
            resposta.raise_for_status()

            return resposta.json().get("version")

        except Exception as erro:
            logger.warning(f"Não foi possível consultar a versão: {erro}")
            return None

    @staticmethod
    def _base_vetorial() -> dict:
        """
        Quantos trechos existem e quais são eles.

        O hash dos identificadores muda se a base for reindexada com outro
        recorte de texto, mesmo que a quantidade continue igual — é o que
        detecta uma reingestão silenciosa entre duas rodadas.
        """

        informacoes = {
            "collection": None,
            "chunk_count": None,
            "chunk_ids_sha256": None,
        }

        try:
            # Import local: o módulo abre o banco e carrega o modelo de
            # embeddings ao ser importado, e o endpoint de saúde não pode
            # depender disso para responder.
            from app.database.chroma_client import ChromaDBClient

            colecao = ChromaDBClient.get_collection()

            identificadores = sorted(colecao.get(include=[])["ids"])

            informacoes["collection"] = colecao.name
            informacoes["chunk_count"] = len(identificadores)
            informacoes["chunk_ids_sha256"] = _sha256(
                "\n".join(identificadores)
            )

        except Exception as erro:
            logger.warning(f"Não foi possível consultar a base: {erro}")
            informacoes["error"] = str(erro)

        return informacoes

    @staticmethod
    def _prompts() -> dict:
        """
        Hash do texto de cada prompt. Um ajuste de palavra muda o resultado
        da classificação, e sem isto a mudança fica invisível no manifesto.
        """

        try:
            from app.prompts import triage

            return {
                "v0_legacy_sha256": _sha256(triage.PROMPT_LEGADO),
                "v1_grounded_sha256": _sha256(triage.SISTEMA_ANCORADO),
                "v1_grounded_sem_contexto_sha256": _sha256(
                    triage.SISTEMA_ANCORADO_SEM_CONTEXTO
                ),
            }

        except Exception as erro:
            logger.warning(f"Não foi possível ler os prompts: {erro}")
            return {"error": str(erro)}

    @staticmethod
    def collect() -> dict:

        return {
            "api_version": settings.API_VERSION,
            "model": FingerprintService._modelo(),
            "ollama_version": FingerprintService._ollama_version(),
            "vector_store": FingerprintService._base_vetorial(),
            "prompts": FingerprintService._prompts(),
            "defaults": {
                "temperature": settings.LLM_TEMPERATURE,
                "seed": settings.LLM_SEED,
                "num_ctx": settings.LLM_NUM_CTX,
                "num_predict": settings.LLM_NUM_PREDICT,
                "structured_output_mode": settings.STRUCTURED_OUTPUT_MODE,
                "context_top_k": settings.CONTEXT_TOP_K,
                "context_min_score": settings.CONTEXT_MIN_SCORE,
                "prompt_version": settings.TRIAGE_PROMPT_VERSION,
            },
        }
