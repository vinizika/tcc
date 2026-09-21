import re

from app.clients.topic_router import normalize, tokens, topic_scores
from app.core.config import settings
from app.core.logger import setup_logger
from app.models.retrieved_document import RetrievedDocument

logger = setup_logger("RerankerClient")

# Um assunto reconhecido com alta confiança é um segundo sinal independente
# da distância vetorial. O piso só vale para o assunto mais provável e usa
# um corte conservador: abaixo dele, a nota continua sendo apenas a soma dos
# sinais vetorial, lexical e de assunto.
ROUTING_CONFIDENCE_MIN = 0.60
ROUTING_MARGIN_MIN = 0.30
ROUTING_SCORE_FLOOR = 0.721
CLINICAL_CONTENT_BONUS = 0.03
CLINICAL_CONTENT_MARKERS = (
    "clinical signs",
    "common signs",
    "signs include",
    "symptoms include",
    "sinais clinicos",
    "sinais incluem",
    "sintomas incluem",
)

class RerankerClient:

    _DOG_TERMS = {"dog", "cao", "cachorro", "cadela"}
    _CAT_TERMS = {"cat", "gato", "gata"}

    @staticmethod
    def _normalize(text: str) -> str:
        return normalize(text)

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        return tokens(text)

    @classmethod
    def _eligible(cls, query: str, document: RetrievedDocument) -> bool:
        normalized_query = cls._normalize(query)
        query_tokens = set(re.findall(r"[a-z0-9]+", normalized_query))

        species = cls._normalize(document.species)
        if query_tokens & cls._DOG_TERMS and species == "cat":
            return False
        if query_tokens & cls._CAT_TERMS and species == "dog":
            return False

        if not document.retrieval_anchors:
            return True

        # Âncoras são palavras/expressões completas. Comparação por substring
        # faria, por exemplo, "passa" casar com "passando mal" e liberaria
        # indevidamente uma fonte sobre uvas-passas.
        return any(
            re.search(
                rf"(?<![a-z0-9]){re.escape(cls._normalize(anchor))}"
                r"(?![a-z0-9])",
                normalized_query,
            )
            for anchor in document.retrieval_anchors
        )

    @staticmethod
    def _source_key(document: RetrievedDocument) -> str:
        return (
            document.source_file
            or document.topic
            or document.title
            or document.id
        )

    @classmethod
    def _routed_context(
        cls,
        ordered: list[RetrievedDocument],
        routed_topic: str | None,
        limit: int,
    ) -> list[RetrievedDocument]:
        """Mantém a continuação do melhor chunk do assunto roteado."""

        routed = [
            document for document in ordered
            if document.topic == routed_topic
        ]
        if not routed or limit <= 0:
            return []

        anchor = routed[0]
        selected = [anchor]
        if anchor.chunk_index is not None:
            same_source = {
                document.chunk_index: document
                for document in routed
                if cls._source_key(document) == cls._source_key(anchor)
                and document.chunk_index is not None
            }
            for delta in (1, 2, -1, -2):
                neighbor = same_source.get(anchor.chunk_index + delta)
                if neighbor is not None and neighbor not in selected:
                    selected.append(neighbor)
                if len(selected) == limit:
                    return selected

        for document in routed:
            if document not in selected:
                selected.append(document)
            if len(selected) == limit:
                break
        return selected

    @classmethod
    def rerank(
        cls,
        queries: list[str],
        documents: list[RetrievedDocument],
        *,
        eligibility_query: str | None = None,
    ) -> list[RetrievedDocument]:

        logger.info("Executando re-ranking lexical com âncoras")

        query = " ".join(query for query in queries if query).strip()
        eligibility_query = eligibility_query if eligibility_query is not None else query
        query_tokens = cls._tokens(query)
        scores_by_topic = topic_scores(eligibility_query)
        ordered_topic_scores = sorted(
            scores_by_topic.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        routed_topic, routing_confidence = (
            ordered_topic_scores[0]
            if ordered_topic_scores else (None, 0.0)
        )
        second_topic_score = (
            ordered_topic_scores[1][1]
            if len(ordered_topic_scores) > 1 else 0.0
        )
        routing_margin = routing_confidence - second_topic_score
        confident_route = (
            routing_confidence >= ROUTING_CONFIDENCE_MIN
            and routing_margin >= ROUTING_MARGIN_MIN
        )
        eligible = [
            document for document in documents
            if cls._eligible(eligibility_query, document)
        ]

        def ranking_score(document: RetrievedDocument) -> tuple[float, float]:
            document_tokens = cls._tokens(f"{document.title} {document.content}")
            lexical_coverage = (
                len(query_tokens & document_tokens) / len(query_tokens)
                if query_tokens else 0.0
            )
            ordering_score = (
                document.score
                + 0.08 * lexical_coverage
                + 0.20 * scores_by_topic.get(document.topic, 0.0)
            )
            routed_document = (
                confident_route and document.topic == routed_topic
            )
            normalized_content = cls._normalize(
                f"{document.title} {document.content}"
            )
            if routed_document and any(
                marker in normalized_content
                for marker in CLINICAL_CONTENT_MARKERS
            ):
                ordering_score += CLINICAL_CONTENT_BONUS

            # O piso decide se o trecho pode entrar no prompt, mas não pode
            # achatar a ordem interna do documento. A ordenação continua
            # usando a evidência real de cada chunk.
            context_score = (
                max(ordering_score, ROUTING_SCORE_FLOOR)
                if routed_document else ordering_score
            )
            document.ranking_score = min(context_score, 1.0)
            return ordering_score, document.score

        ordered = sorted(eligible, key=ranking_score, reverse=True)
        # Quando a rota é inequívoca, três chunks do assunto são mais úteis
        # que um único fragmento cortado no meio de uma explicação. Depois
        # disso a diversidade por fonte volta a valer para o restante.
        selected: list[RetrievedDocument] = (
            cls._routed_context(
                ordered,
                routed_topic,
                min(3, settings.TOP_K),
            ) if confident_route else []
        )
        repeated: list[RetrievedDocument] = []
        seen_sources = {
            cls._source_key(document) for document in selected
        }
        selected_ids = {document.id for document in selected}

        for document in ordered:
            if document.id in selected_ids:
                continue
            source = cls._source_key(document)
            if source in seen_sources:
                repeated.append(document)
            else:
                seen_sources.add(source)
                selected.append(document)
            if len(selected) == settings.TOP_K:
                return selected

        selected.extend(repeated[: settings.TOP_K - len(selected)])
        return selected
