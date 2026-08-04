class QueryClient:

    @staticmethod
    def rewrite(question: str) -> str:
        """
        Reescreve a pergunta do usuário.
        Atualmente apenas retorna a pergunta original.
        """
        return question

    @staticmethod
    def generate_queries(question: str) -> list[str]:
        """
        Futuramente utilizará Multi-Query + HyDE.
        """
        return [question]