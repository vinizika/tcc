from app.core.logger import setup_logger

logger = setup_logger("QueryClient")


class QueryClient:

    @staticmethod
    def rewrite(question: str) -> str:
        """
        Simula o Query Rewriting.
        Futuramente será substituído pela implementação real.
        """

        logger.info("Executando Query Rewriting")

        return question.strip()

    @staticmethod
    def generate_queries(question: str) -> list[str]:
        """
        Simula Multi-Query + HyDE.
        """

        logger.info("Gerando consultas")

        return [
            question,
            f"Informações veterinárias sobre: {question}",
            f"Emergência veterinária relacionada a: {question}",
        ]