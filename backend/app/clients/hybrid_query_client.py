"""
Cliente de produção da etapa de consulta: tenta o Gemini primeiro e cai
para o Ollama automaticamente quando o Gemini falhar — por qualquer
motivo (chave não configurada, limite gratuito atingido, erro de rede).
Nunca deixa o tutor esperando uma API externa que não responde.

Decisão do dono do trilho B1 (22-23/09), depois da comparação nas rodadas
14-15 (evidencias/ryu/): em 25 casos revisados, o Ollama (llama3.2:3b)
produziu 5 erros factuais claros na reescrita, no Multi-Query e no HyDE —
um termo inventado ("hipotirese"), uma palavra errada no lugar de
"taquipneia" ("tachímetro"), um diagnóstico humano inexistente em cães
("doença de Huntington"), um sintoma não relatado pelo tutor injetado na
busca ("paralisia") e uma contaminação cruzada entre casos (menção a
teobromina/chocolate numa convulsão sem nenhuma relação com comida). O
Gemini não repetiu nenhum desses erros nos mesmos 25 casos.

O HyDE é o único caso especial: seu histórico com Ollama já reprovou duas
vezes (B-09) — nunca melhorou Precision@1/MRR e alucinava. Por isso, se o
Gemini falhar especificamente na chamada do HyDE, **não cai para o
Ollama** — simplesmente não gera documento hipotético nesta consulta. Cair
para o Ollama reintroduziria em silêncio o problema que o B-09 já tinha
fechado. Reescrita e Multi-Query, ao contrário, caem para o Ollama sem
receio: nunca foram desativados por qualidade, só têm uma versão mais
precisa disponível agora.
"""

from app.clients.gemini_query_client import GeminiQueryClient
from app.clients.query_client import QueryClient
from app.core.logger import setup_logger
from app.exceptions.llm_exception import LLMException

logger = setup_logger("HybridQueryClient")


class HybridQueryClient:

    @staticmethod
    def rewrite(question: str) -> str:

        try:
            return GeminiQueryClient.rewrite(question)
        except LLMException as erro:
            logger.warning(
                f"Gemini falhou na reescrita, caindo para Ollama: {erro}"
            )
            return QueryClient.rewrite(question)

    @staticmethod
    def generate_queries(question: str) -> list[str]:

        try:
            return GeminiQueryClient.generate_queries(question)
        except LLMException as erro:
            logger.warning(
                f"Gemini falhou no Multi-Query, caindo para Ollama: {erro}"
            )
            return QueryClient.generate_queries(question)

    @staticmethod
    def generate_hypothetical_document(question: str) -> str:

        try:
            return GeminiQueryClient.generate_hypothetical_document(question)
        except LLMException as erro:
            logger.warning(
                "Gemini falhou no HyDE — seguindo sem documento hipotético "
                f"nesta consulta (não cai para o Ollama, ver B-09): {erro}"
            )
            return ""
