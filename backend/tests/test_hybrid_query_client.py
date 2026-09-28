"""
HybridQueryClient é o que o pipeline de produção realmente chama: Gemini
primeiro, Ollama como plano B — exceto no HyDE, que não cai para o Ollama
(decisão do B-09, ver o docstring do próprio cliente).
"""

from app.clients.hybrid_query_client import HybridQueryClient
from app.exceptions.llm_exception import LLMException

import pytest


def test_rewrite_usa_gemini_quando_disponivel(monkeypatch):

    monkeypatch.setattr(
        "app.clients.hybrid_query_client.GeminiQueryClient.rewrite",
        lambda question: "reescrita do gemini",
    )

    resultado = HybridQueryClient.rewrite("meu cachorro comeu chocolate")

    assert resultado == "reescrita do gemini"


def test_rewrite_cai_para_ollama_quando_gemini_falha(monkeypatch):

    def gemini_falho(question):
        raise LLMException("limite atingido")

    monkeypatch.setattr(
        "app.clients.hybrid_query_client.GeminiQueryClient.rewrite",
        gemini_falho,
    )
    monkeypatch.setattr(
        "app.clients.hybrid_query_client.QueryClient.rewrite",
        lambda question: "reescrita do ollama",
    )

    resultado = HybridQueryClient.rewrite("meu cachorro comeu chocolate")

    assert resultado == "reescrita do ollama"


def test_generate_queries_cai_para_ollama_quando_gemini_falha(monkeypatch):

    def gemini_falho(question):
        raise LLMException("sem chave configurada")

    monkeypatch.setattr(
        "app.clients.hybrid_query_client.GeminiQueryClient.generate_queries",
        gemini_falho,
    )
    monkeypatch.setattr(
        "app.clients.hybrid_query_client.QueryClient.generate_queries",
        lambda question: ["consulta 1", "consulta 2"],
    )

    resultado = HybridQueryClient.generate_queries("relato do tutor")

    assert resultado == ["consulta 1", "consulta 2"]


def test_hyde_nao_cai_para_ollama_quando_gemini_falha(monkeypatch):
    """
    B-09: o HyDE do Ollama alucinava e nunca ajudou a recuperação. Se o
    Gemini falhar, a consulta segue sem documento hipotético — nunca
    reintroduz o Ollama nesta etapa especificamente.
    """

    chamou_ollama = []

    def gemini_falho(question):
        raise LLMException("limite atingido")

    def ollama_hyde(question):
        chamou_ollama.append(question)
        return "documento do ollama"

    monkeypatch.setattr(
        "app.clients.hybrid_query_client.GeminiQueryClient.generate_hypothetical_document",
        gemini_falho,
    )
    monkeypatch.setattr(
        "app.clients.hybrid_query_client.QueryClient.generate_hypothetical_document",
        ollama_hyde,
    )

    resultado = HybridQueryClient.generate_hypothetical_document("relato do tutor")

    assert resultado == ""
    assert chamou_ollama == []


def test_hyde_usa_gemini_quando_disponivel(monkeypatch):

    monkeypatch.setattr(
        "app.clients.hybrid_query_client.GeminiQueryClient.generate_hypothetical_document",
        lambda question: "documento do gemini",
    )

    resultado = HybridQueryClient.generate_hypothetical_document("relato do tutor")

    assert resultado == "documento do gemini"
