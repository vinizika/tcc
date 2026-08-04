from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.chat import ChatResponse


class ChatService:

    @staticmethod
    def generate_response(question: str):

        result = ChatPipeline.execute(question)

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )