from app.clients.query_client import QueryClient
from app.clients.retrieval_client import RetrievalClient
from app.clients.reranker_client import RerankerClient
from app.clients.llm_client import LLMClient

from app.core.config import settings
from app.core.logger import setup_logger

import time

logger = setup_logger("ChatPipeline")


class ChatPipeline:

    @staticmethod
    def execute(question: str):

        start = time.perf_counter()

        logger.info(f"Pergunta recebida: {question}")

        try:

            # 1 - Query Rewriting
            rewritten_question = QueryClient.rewrite(question)

            logger.info(f"Pergunta reescrita: {rewritten_question}")

            # 2 - Multi Query
            queries = QueryClient.generate_queries(rewritten_question)

            logger.info(f"{len(queries)} consultas geradas")

            # 2.1 - HyDE
            if settings.HYDE_ENABLED:

                hypothetical_document = (
                    QueryClient.generate_hypothetical_document(
                        rewritten_question
                    )
                )

                if hypothetical_document:
                    queries.append(hypothetical_document)

                logger.info(
                    "Documento hipotético (HyDE) adicionado às "
                    "consultas"
                )

            else:

                logger.info("HyDE desativado")

            # 3 - Busca Vetorial
            documents = RetrievalClient.retrieve(queries)

            logger.info(f"{len(documents)} documentos recuperados")

            # 4 - Re-ranking
            ranked_documents = RerankerClient.rerank(documents)

            logger.info("Re-ranking concluído")

            # 5 - LLM
            answer = LLMClient.generate(
                rewritten_question,
                ranked_documents
            )

            logger.info("Resposta gerada")

            # 6 - Self Correction
            answer = LLMClient.self_correct(answer)

            logger.info("Self Correction concluída")

            elapsed = time.perf_counter() - start

            logger.info(f"Pipeline finalizado em {elapsed:.2f}s")

            return {
                "answer": answer,
                "sources": ranked_documents
            }

        except Exception as e:

            logger.exception(f"Erro no pipeline: {e}")

            raise

        