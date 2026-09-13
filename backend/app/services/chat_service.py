"""
Traduz o resultado do pipeline para o formato da API.

O pipeline trabalha com documentos recuperados; a resposta HTTP expõe um
recorte deles. Manter a tradução aqui evita que o pipeline precise conhecer
o schema da API.

Também é aqui, e não no pipeline, que o cadastro do pet vira contexto de
prompt e que o turno é gravado no histórico de conversa: são preocupações da
API (quem é o tutor, qual conversa é essa), não da orquestração da triagem.
"""

from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.chat import ChatRequest, ChatResponse, SourceResponse
from app.services.conversation_service import ConversationService
from app.services.pet_service import PetService


class ChatService:

    @staticmethod
    def process(
        request: ChatRequest,
        pipeline: ChatPipeline,
    ) -> ChatResponse:

        animal_context = None

        if request.pet_id:
            # Pet inexistente ou Supabase fora do ar: propaga como erro da
            # requisição. Diferente do histórico de conversa, o tutor
            # referenciou um pet explicitamente — se não existe, é melhor
            # avisar do que triar em silêncio sem o contexto que ele esperava.
            pet = PetService.get(request.pet_id)
            animal_context = pet.to_triage_context()

        result = pipeline.execute(
            request.question,
            request.options,
            animal_context=animal_context,
        )

        conversation_id = request.conversation_id

        if request.tutor_id or request.pet_id or request.conversation_id:
            # O histórico é acessório: se o Mongo não estiver configurado,
            # ConversationService.append_turn devolve None em vez de levantar
            # exceção, e a triagem em si já foi respondida normalmente.
            conversation_id = ConversationService.append_turn(
                tutor_message=request.question,
                assistant_message=result.answer,
                triage=result.triage,
                conversation_id=request.conversation_id,
                tutor_id=request.tutor_id,
                pet_id=request.pet_id,
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
            conversation_id=conversation_id,
        )
