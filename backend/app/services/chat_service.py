"""
Traduz o resultado do pipeline para o formato da API.

O pipeline trabalha com documentos recuperados; a resposta HTTP expõe um
recorte deles. Manter a tradução aqui evita que o pipeline precise conhecer
o schema da API.
"""

from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.chat import ChatRequest, ChatResponse, SourceResponse


class ChatService:

    @staticmethod
    def process(
        request: ChatRequest,
        pipeline: ChatPipeline,
    ) -> ChatResponse:

        result = pipeline.execute(
            request.question,
            request.options,
        )

        return ChatResponse(
            answer=result.answer,
            triage=result.triage,
            sources=[
                SourceResponse(
                    title=item.document.title,
                    source=item.document.source,
                    score=round(item.document.score, 4),
                    chunk_id=item.document.chunk_id,
                    cited=item.cited,
                )
                for item in result.sources
            ],
            config=result.config,
            retrieval=result.retrieval,
            timings=result.timings,
            debug=result.debug,
        )
