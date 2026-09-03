from app.constants.pipeline import DEFAULT_SCORE_THRESHOLD
from app.core.config import settings
from app.core.logger import setup_logger
from app.database.chroma_client import ChromaDBClient
from app.models.retrieved_document import RetrievedDocument


logger = setup_logger("RetrievalClient")


class RetrievalClient:

    @staticmethod
    def retrieve(
        queries: list[str]
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

        number_of_results = min(
            settings.TOP_K,
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

        for query_index in range(len(results["ids"])):

            ids = results["ids"][query_index]
            documents = results["documents"][query_index]
            metadatas = results["metadatas"][query_index]
            distances = results["distances"][query_index]

            for document_id, content, metadata, distance in zip(
                ids,
                documents,
                metadatas,
                distances
            ):
                metadata = metadata or {}

                # Quanto menor a distância, maior a similaridade.
                score = 1 - float(distance)

                retrieved_document = RetrievedDocument(
                    id=document_id,
                    chunk_id=document_id,
                    title=metadata.get(
                        "title",
                        "Documento sem título"
                    ),
                    content=content,
                    source=metadata.get(
                        "source",
                        "Fonte não informada"
                    ),
                    score=score
                )

                previous_document = best_documents.get(
                    document_id
                )

                if (
                    previous_document is None
                    or retrieved_document.score
                    > previous_document.score
                ):
                    best_documents[document_id] = (
                        retrieved_document
                    )

        documents = sorted(
            best_documents.values(),
            key=lambda document: document.score,
            reverse=True
        )

        above_threshold = [
            document
            for document in documents
            if document.score >= DEFAULT_SCORE_THRESHOLD
        ]

        if above_threshold:
            documents = above_threshold
        else:
            logger.warning(
                "Nenhum documento atingiu o score mínimo de "
                f"{DEFAULT_SCORE_THRESHOLD}; mantendo o(s) mais "
                "próximo(s) disponível(is) mesmo assim."
            )

        documents = documents[:settings.TOP_K]

        logger.info(
            f"{len(documents)} documentos recuperados"
        )

        return documents