"""
Traduz o resultado do pipeline para o formato da API.

O pipeline trabalha com documentos recuperados; a resposta HTTP expõe um
recorte deles. Manter a tradução aqui evita que o pipeline precise conhecer
o schema da API.

Também é aqui, e não no pipeline, que o turno é gravado no histórico de
conversa: é preocupação da API (qual conversa é essa), não da orquestração
da triagem. O cadastro do pet, que já entrou aqui pelo Supabase, hoje vem só
do workspace do app (rodada 25 do Ryu).
"""

from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.chat import ChatRequest, ChatResponse, SourceResponse
from app.services.conversation_service import ConversationService


class ChatService:

    @staticmethod
    def process(
        request: ChatRequest,
        pipeline: ChatPipeline,
        principal_user_id: str | None = None,
    ) -> ChatResponse:

        if principal_user_id and request.conversation_id:
            ConversationService.get_owned(
                request.conversation_id,
                principal_user_id,
            )

        result = pipeline.execute(
            request.question,
            request.options,
        )

        conversation_id = request.conversation_id

        if request.conversation_id or request.save_history:
            # O histórico é acessório: se o Mongo não estiver configurado,
            # ConversationService.append_turn devolve None em vez de levantar
            # exceção, e a triagem em si já foi respondida normalmente.
            conversation_id = ConversationService.append_turn(
                tutor_message=request.question,
                assistant_message=result.answer,
                triage=result.triage,
                conversation_id=request.conversation_id,
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
                    topic=item.document.topic,
                    display_title=item.document.display_title,
                    references=[
                        referencia
                        for referencia in item.document.references
                        if referencia.get("title")
                    ],
                )
                for item in result.sources
            ],
            config=result.config,
            retrieval=result.retrieval,
            timings=result.timings,
            debug=result.debug,
            provenance=result.provenance,
            conversation_id=conversation_id,
        )
