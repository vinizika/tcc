"""
Espelho experimental do QueryClient, usando a API do Gemini em vez do
Ollama local — mesma interface (rewrite/generate_queries/
generate_hypothetical_document), mesmos prompts (importados de
query_client.py, nunca reescritos aqui), só o provedor do modelo muda.

Existe para responder uma pergunta do grupo (22/09): um modelo maior ajuda
a etapa de consulta o suficiente para justificar a complexidade de
depender de uma API externa? Ver
backend/app/database/compare_query_providers.py, o script que roda os
dois lado a lado.

Não é chamado por nada em produção. `ChatPipeline` continua usando só o
QueryClient (Ollama) até essa pergunta ser respondida com número, não
opinião.
"""

import re

from app.clients.query_client import (
    HYDE_SYSTEM_PROMPT,
    MULTI_QUERY_SYSTEM_PROMPT,
    REWRITE_SYSTEM_PROMPT,
    _contains_unwarranted_urgency,
)
from app.core.config import settings
from app.core.logger import setup_logger
from app.exceptions.llm_exception import LLMException

logger = setup_logger("GeminiQueryClient")


def _get_gemini_client():
    """
    Import tardio: quem nunca usa o comparador não precisa que
    `google-genai` esteja instalado nem configurado para rodar o resto do
    backend.
    """

    if not settings.GEMINI_API_KEY:
        raise LLMException(
            "GEMINI_API_KEY não configurada. Defina no .env local (nunca "
            "no .env.example) para usar o GeminiQueryClient."
        )

    from google import genai

    return genai.Client(api_key=settings.GEMINI_API_KEY)


class GeminiQueryClient:

    _client = None

    @classmethod
    def _chat(cls, system_prompt: str, question: str) -> str:

        if cls._client is None:
            cls._client = _get_gemini_client()

        try:
            resposta = cls._client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=question,
                config={
                    "system_instruction": system_prompt,
                    "temperature": settings.LLM_TEMPERATURE,
                },
            )
        except Exception as erro:
            # Captura ampla de propósito: a exceção de limite excedido do
            # SDK (google.genai.errors.ClientError, código 429) não precisa
            # ser importada aqui só para essa checagem — evita que testar
            # este cliente exija o pacote `google-genai` instalado.
            codigo = getattr(erro, "code", None)
            if codigo == 429:
                raise LLMException(
                    f"Limite gratuito do Gemini atingido: {erro}"
                ) from erro
            raise LLMException(f"A API do Gemini recusou a chamada: {erro}") from erro

        return (resposta.text or "").strip()

    @staticmethod
    def rewrite(question: str) -> str:

        logger.info("Executando Query Rewriting (Gemini)")

        question = question.strip()

        if not question:
            return question

        rewritten_question = GeminiQueryClient._chat(REWRITE_SYSTEM_PROMPT, question)

        if _contains_unwarranted_urgency(question, rewritten_question):
            logger.warning(
                "Query Rewriting descartado (B-08): termo de urgência "
                "ausente do relato original apareceu na reescrita. "
                f"Reescrita descartada: {rewritten_question!r}"
            )
            return question

        logger.info(f"Query Rewriting concluído: {rewritten_question}")

        return rewritten_question

    @staticmethod
    def generate_queries(question: str) -> list[str]:

        logger.info("Gerando consultas Multi-Query (Gemini)")

        content = GeminiQueryClient._chat(MULTI_QUERY_SYSTEM_PROMPT, question)

        queries = [
            re.sub(r"^[\-\*\d\.\)]+\s*", "", line).strip()
            for line in content.splitlines()
            if line.strip()
        ]

        queries = [query for query in queries if query][:3]

        logger.info(f"Consultas Multi-Query geradas: {queries}")

        return queries

    @staticmethod
    def generate_hypothetical_document(question: str) -> str:

        logger.info("Gerando documento hipotético (Gemini)")

        question = question.strip()

        if not question:
            return question

        hypothetical_document = GeminiQueryClient._chat(HYDE_SYSTEM_PROMPT, question)

        logger.info(
            f"Documento hipotético (HyDE) gerado: {hypothetical_document}"
        )

        return hypothetical_document
