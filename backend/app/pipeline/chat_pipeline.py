"""
Orquestração da triagem: do relato do tutor até a resposta.

O pipeline recebe os clientes por parâmetro para poder ser testado sem
Ollama e sem banco vetorial. Os padrões são os clientes reais, então quem
usa em produção não precisa saber disso.
"""

import time

from app.clients.llm_client import LLMClient
from app.clients.query_client import QueryClient
from app.clients.reranker_client import RerankerClient
from app.clients.retrieval_client import RetrievalClient
from app.constants.pipeline import DEFAULT_SCORE_THRESHOLD
from app.core.config import settings
from app.core.logger import setup_logger
from app.models.retrieved_document import RetrievedDocument
from app.pipeline.config_resolver import resolve
from app.pipeline.result import ContextDocument, PipelineResult, QueryPlan
from app.schemas.triage import (
    DebugInfo,
    DebugSource,
    EffectiveConfig,
    PipelineOptions,
    RetrievalInfo,
    Timings,
)

logger = setup_logger("ChatPipeline")


class ChatPipeline:

    def __init__(
        self,
        query_client=QueryClient,
        retrieval_client=RetrievalClient,
        reranker=RerankerClient,
        llm_client=LLMClient,
    ):
        self.query_client = query_client
        self.retrieval_client = retrieval_client
        self.reranker = reranker
        self.llm_client = llm_client

    # ------------------------------------------------------------------
    # Etapa de consulta (fronteira com o trilho B1)
    # ------------------------------------------------------------------

    def _build_queries(
        self,
        question: str,
        config: EffectiveConfig,
    ) -> QueryPlan:
        """
        Transforma o relato do tutor nas consultas que vão à busca vetorial.

        É o único ponto que conhece a interface do QueryClient, para que uma
        mudança daquele trilho tenha um lugar só para ser absorvida.
        """

        if config.query_rewriting_enabled:
            rewritten = self.query_client.rewrite(question)
            logger.info(f"Pergunta reescrita: {rewritten}")
        else:
            rewritten = question
            logger.info("Query Rewriting desativado")

        # Sem reescrita útil, a busca ainda precisa de algo para procurar.
        rewritten = (rewritten or "").strip() or question

        if config.multi_query_enabled:
            queries = self.query_client.generate_queries(rewritten)
            logger.info(f"{len(queries)} consultas geradas")
        else:
            queries = []
            logger.info("Multi-Query desativado")

        queries = [
            query.strip()
            for query in queries
            if query and query.strip()
        ]

        # O Multi-Query pode devolver nada; nesse caso a própria consulta
        # reescrita vai à busca, em vez de pesquisar uma lista vazia.
        if not queries:
            queries = [rewritten]

        hypothetical_document = None

        if config.hyde_enabled:
            hypothetical_document = (
                self.query_client.generate_hypothetical_document(
                    rewritten
                )
            )

            if hypothetical_document:
                queries.append(hypothetical_document)
                logger.info("Documento hipotético (HyDE) adicionado")
        else:
            logger.info("HyDE desativado")

        return QueryPlan(
            rewritten=rewritten,
            queries=queries,
            hypothetical_document=hypothetical_document,
        )

    # ------------------------------------------------------------------
    # Etapa de recuperação
    # ------------------------------------------------------------------

    def _retrieve(
        self,
        queries: list[str],
        config: EffectiveConfig,
    ):
        """
        Devolve (tudo que a busca trouxe, o que vai ao prompt, estatísticas).

        As estatísticas ficam fora do bloco de debug porque o runner de
        avaliação precisa delas em toda linha: sem o score máximo não dá
        para distinguir "a geração errou" de "a busca não trouxe nada útil".
        """

        retrieved = self.retrieval_client.retrieve(queries)

        logger.info(f"{len(retrieved)} documentos recuperados")

        ranked = self.reranker.rerank(retrieved)

        for_context = [
            document
            for document in ranked
            if document.score >= config.context_min_score
        ][: config.context_top_k]

        info = RetrievalInfo(
            returned_count=len(retrieved),
            used_count=len(for_context),
            above_threshold_count=len(
                [
                    document
                    for document in retrieved
                    if document.score >= DEFAULT_SCORE_THRESHOLD
                ]
            ),
            max_score=(
                max(document.score for document in retrieved)
                if retrieved
                else None
            ),
            threshold=DEFAULT_SCORE_THRESHOLD,
        )

        return ranked, for_context, info

    # ------------------------------------------------------------------

    def execute(
        self,
        question: str,
        options: PipelineOptions | None = None,
    ) -> PipelineResult:

        start = time.perf_counter()

        config = resolve(settings, options)

        logger.info(f"Pergunta recebida: {question}")

        question = question.strip()

        plan = QueryPlan(rewritten=question)
        ranked: list[RetrievedDocument] = []
        for_context: list[RetrievedDocument] = []
        retrieval_info = RetrievalInfo(threshold=DEFAULT_SCORE_THRESHOLD)

        query_seconds = 0.0
        retrieval_seconds = 0.0

        try:

            if config.retrieval_enabled:

                query_start = time.perf_counter()
                plan = self._build_queries(question, config)
                query_seconds = time.perf_counter() - query_start

                retrieval_start = time.perf_counter()
                ranked, for_context, retrieval_info = self._retrieve(
                    plan.queries,
                    config,
                )
                retrieval_seconds = time.perf_counter() - retrieval_start

            else:
                logger.info(
                    "Recuperação desativada: rodando como LLM puro"
                )

            generation_start = time.perf_counter()

            answer = self.llm_client.generate(
                plan.rewritten,
                for_context,
            )

            generation_seconds = time.perf_counter() - generation_start

            total_seconds = time.perf_counter() - start

            logger.info(f"Pipeline finalizado em {total_seconds:.2f}s")

            debug = None

            if options is not None and options.include_debug:
                debug = DebugInfo(
                    rewritten_question=plan.rewritten,
                    queries=plan.queries,
                    hypothetical_document=plan.hypothetical_document,
                    all_sources=[
                        DebugSource(
                            chunk_id=document.chunk_id,
                            title=document.title,
                            source=document.source,
                            score=document.score,
                        )
                        for document in ranked
                    ],
                )

            return PipelineResult(
                answer=answer,
                sources=[
                    ContextDocument(document=document)
                    for document in for_context
                ],
                config=config,
                timings=Timings(
                    query_s=round(query_seconds, 3),
                    retrieval_s=round(retrieval_seconds, 3),
                    generation_s=round(generation_seconds, 3),
                    total_s=round(total_seconds, 3),
                ),
                retrieval=retrieval_info,
                debug=debug,
            )

        except Exception as error:

            logger.exception(f"Erro no pipeline: {error}")

            raise
