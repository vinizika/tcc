import json

from app.core.config import settings
from app.core.logger import setup_logger
from app.clients.topic_router import likely_topics
from app.database.chroma_client import ChromaDBClient
from app.models.retrieved_document import RetrievedDocument


logger = setup_logger("RetrievalClient")


def _retrieval_anchors(metadata: dict) -> tuple[str, ...]:
    raw = metadata.get("retrieval_anchors")
    if not raw:
        return ()
    try:
        anchors = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, json.JSONDecodeError):
        logger.warning("retrieval_anchors inválido no chunk; ignorando")
        return ()
    if not isinstance(anchors, list):
        return ()
    return tuple(str(anchor).strip() for anchor in anchors if str(anchor).strip())


class RetrievalClient:

    @staticmethod
    def retrieve(
        queries: list[str],
        *,
        routing_query: str | None = None,
    ) -> list[RetrievedDocument]:

        logger.info("Consultando o ChromaDB")

        valid_queries = [
            query.strip()
            for query in queries
            if query and query.strip()
        ]

        if not valid_queries:
            logger.warning("Nenhuma consulta válida recebida")
            return []

        collection = ChromaDBClient.get_collection()

        document_count = collection.count()

        if document_count == 0:
            logger.warning("A coleção do ChromaDB está vazia")
            return []

        # Consult more candidates than the public TOP_K so repeated chunks
        # from one long source do not hide a second relevant source.
        number_of_results = min(
            max(settings.TOP_K * 10, settings.TOP_K),
            document_count
        )

        results = collection.query(
            query_texts=valid_queries,
            n_results=number_of_results,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        best_documents: dict[str, RetrievedDocument] = {}

        def merge_results(query_results: dict) -> None:
            """Funde lotes sem perder a melhor similaridade de cada chunk."""

            for query_index in range(len(query_results["ids"])):
                ids = query_results["ids"][query_index]
                documents = query_results["documents"][query_index]
                metadatas = query_results["metadatas"][query_index]
                distances = query_results["distances"][query_index]

                for document_id, content, metadata, distance in zip(
                    ids,
                    documents,
                    metadatas,
                    distances,
                ):
                    metadata = metadata or {}

                    # Quanto menor a distância, maior a similaridade.
                    score = 1 - float(distance)

                    retrieved_document = RetrievedDocument(
                        id=document_id,
                        chunk_id=document_id,
                        title=metadata.get(
                            "title",
                            "Documento sem título",
                        ),
                        # Coleções novas armazenam o texto contextualizado para
                        # embedding e o corpo limpo nos metadados. O fallback
                        # mantém snapshots legados legíveis.
                        content=metadata.get("body", content),
                        source=metadata.get(
                            "source",
                            "Fonte não informada",
                        ),
                        score=score,
                        topic=metadata.get("topic", ""),
                        source_file=metadata.get("source_file", ""),
                        species=metadata.get("species", ""),
                        chunk_index=metadata.get("chunk_index"),
                        retrieval_anchors=_retrieval_anchors(metadata),
                    )

                    previous_document = best_documents.get(document_id)

                    if (
                        previous_document is None
                        or retrieved_document.score > previous_document.score
                    ):
                        best_documents[document_id] = retrieved_document

        merge_results(results)

        # A busca geral pode deixar o assunto correto fora dos primeiros
        # candidatos. Quando o relato original aponta assuntos conhecidos,
        # fazemos uma segunda consulta limitada a eles e fundimos os chunks.
        # O relato original é usado de propósito: texto gerado por reescrita
        # ou HyDE não pode escolher sozinho um assunto clínico.
        routed_topics = likely_topics(routing_query or "")
        if routed_topics:
            routed_results = collection.query(
                query_texts=[routing_query],
                n_results=min(
                    # O artigo certo pode ter muitos chunks. Um lote curto
                    # achou o tópico Allium, mas deixou de fora justamente
                    # o trecho seguinte com anemia e gengiva pálida.
                    settings.TOP_K * len(routed_topics) * 10,
                    document_count,
                ),
                where={"topic": {"$in": routed_topics}},
                include=["documents", "metadatas", "distances"],
            )
            merge_results(routed_results)
            logger.info(
                "Rota lexical adicionou candidatos dos assuntos: %s",
                ", ".join(routed_topics),
            )

        documents = sorted(
            best_documents.values(),
            key=lambda document: document.score,
            reverse=True
        )

        logger.info(
            f"{len(documents)} candidatos recuperados"
        )

        return documents
