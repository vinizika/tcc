from app.pipeline.chat_pipeline import ChatPipeline


class ChatService:

    @staticmethod
    def process(question: str):

        return ChatPipeline.execute(question)