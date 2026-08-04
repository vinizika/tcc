from app.clients.query_client import QueryClient
from app.clients.retrieval_client import RetrievalClient
from app.clients.reranker_client import RerankerClient
from app.clients.llm_client import LLMClient
from app.core.logger import setup_logger
import time

logger = setup_logger("ChatPipeline")

class ChatPipeline:

    @staticmethod
    def execute(question: str):

        start = time.perf_counter()

        logger.info(f"Pergunta recebida: {question}")

        try:

            rewritten_question = QueryClient.rewrite(question)

            logger.info(f"Pergunta reescrita: {rewritten_question}")

            queries = QueryClient.generate_queries(rewritten_question)

            logger.info(f"{len(queries)} consultas geradas")

            documents = RetrievalClient.retrieve(queries)

            logger.info(f"{len(documents)} documentos recuperados")

            documents = RerankerClient.rerank(documents)

            logger.info("Re-ranking concluído")

            answer = LLMClient.generate(
                rewritten_question,
                documents
            )

            logger.info("Resposta gerada")

            answer = LLMClient.self_correct(answer)

            logger.info("Self Correction concluída")

            elapsed = time.perf_counter() - start

            logger.info(f"Pipeline finalizado em {elapsed:.2f} segundos")

            return {
                "answer": answer,
                "sources": documents
            }

        except Exception as e:

            logger.exception(f"Erro durante o pipeline: {e}")

            raise