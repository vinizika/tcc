from ollama import Client

from app.core.logger import setup_logger


logger = setup_logger("QueryClient")


class QueryClient:

    _client = Client(host="http://ollama:11434")

    @staticmethod
    def rewrite(question: str) -> str:
        """
        Reformula a pergunta do usuário para melhorar
        a recuperação de informações.
        """

        logger.info("Executando Query Rewriting")

        question = question.strip()

        if not question:
            return question

        response = QueryClient._client.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente responsável por reformular "
                        "perguntas para um sistema de busca veterinário. "
                        "Reescreva a pergunta de forma clara, objetiva "
                        "e adequada para recuperação de documentos. "
                        "Mantenha o significado original. "
                        "Responda apenas com a pergunta reformulada."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )

        rewritten_question = response["message"]["content"].strip()

        logger.info(
            f"Query Rewriting concluído: {rewritten_question}"
        )

        return rewritten_question

    @staticmethod
    def generate_queries(question: str) -> list[str]:

        logger.info("Gerando consultas Multi-Query")

        response = QueryClient._client.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente responsável por gerar "
                        "múltiplas consultas para um sistema de busca "
                        "veterinário. "
                        "A partir da pergunta fornecida, gere exatamente "
                        "3 consultas diferentes que abordem o mesmo "
                        "problema por perspectivas diferentes. "
                        "As consultas devem ser objetivas e adequadas "
                        "para recuperação de documentos veterinários. "
                        "Não responda à pergunta. "
                        "Retorne apenas uma consulta por linha."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )

        content = response["message"]["content"].strip()

        queries = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        queries = queries[:3]

        logger.info(
            f"Consultas Multi-Query geradas: {queries}"
        )

        return queries