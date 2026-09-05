import re

from app.core.config import settings
from app.core.logger import setup_logger
from app.core.ollama import default_options, get_ollama_client


logger = setup_logger("QueryClient")


class QueryClient:

    _client = get_ollama_client()

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
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você reformula relatos de tutores de animais "
                        "em consultas técnicas para um sistema de "
                        "busca veterinário. "
                        "A entrada pode ser uma afirmação, uma "
                        "descrição de sintomas ou uma pergunta — "
                        "reescreva-a sempre no mesmo formato (uma "
                        "afirmação continua sendo uma afirmação). "
                        "Troque termos coloquiais por terminologia "
                        "clínica veterinária equivalente. "
                        "Nunca faça perguntas de volta ao tutor. "
                        "Nunca peça mais informações. "
                        "Nunca responda ou dê conselhos. "
                        "Nunca adicione informações que não estavam "
                        "no relato original. "
                        "Responda apenas com a frase reformulada, "
                        "sem comentários.\n\n"
                        "Exemplos:\n"
                        "Entrada: meu cachorro está ofegante e com a "
                        "língua azul\n"
                        "Saída: cão apresentando taquipneia e "
                        "cianose de mucosas\n\n"
                        "Entrada: meu cachorro comeu chocolate\n"
                        "Saída: cão com histórico de ingestão de "
                        "chocolate, possível intoxicação por "
                        "teobromina\n\n"
                        "Entrada: minha gata não consegue fazer xixi "
                        "desde ontem\n"
                        "Saída: gata com suspeita de obstrução "
                        "urinária, ausência de micção há mais de "
                        "24 horas"
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            options=default_options(),
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
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você gera consultas de busca para um sistema "
                        "de recuperação de documentos veterinários. "
                        "A partir do relato fornecido, gere exatamente "
                        "3 consultas curtas, cada uma abordando um "
                        "aspecto clínico diferente do mesmo caso "
                        "(por exemplo: sintomas, causa provável, "
                        "conduta/tratamento). "
                        "Cada consulta deve ser uma frase curta e "
                        "técnica, não uma pergunta. "
                        "Nunca responda ao relato. "
                        "Nunca dê conselhos, opiniões ou ressalvas. "
                        "Nunca explique as consultas. "
                        "Retorne apenas as 3 consultas, uma por linha, "
                        "sem numeração, sem marcadores e sem texto "
                        "antes ou depois.\n\n"
                        "Exemplo:\n"
                        "Relato: cão com histórico de ingestão de "
                        "chocolate, possível intoxicação por "
                        "teobromina\n"
                        "Saída:\n"
                        "sintomas de intoxicação por teobromina em "
                        "cães\n"
                        "quantidade de chocolate tóxica para cães "
                        "por peso corporal\n"
                        "conduta de emergência para intoxicação por "
                        "chocolate em cães"
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            options=default_options(),
        )

        content = response["message"]["content"].strip()

        queries = [
            re.sub(r"^[\-\*\d\.\)]+\s*", "", line).strip()
            for line in content.splitlines()
            if line.strip()
        ]

        queries = [query for query in queries if query]

        queries = queries[:3]

        logger.info(
            f"Consultas Multi-Query geradas: {queries}"
        )

        return queries

    @staticmethod
    def generate_hypothetical_document(question: str) -> str:
        """
        Gera um documento hipotético a partir da pergunta do
        usuário (técnica HyDE - Hypothetical Document Embeddings).

        O documento não precisa ser factualmente correto: seu
        único objetivo é aproximar o vocabulário da consulta da
        terminologia técnica presente na base veterinária,
        servindo como âncora adicional para a busca vetorial.
        Ele nunca é exibido ao tutor nem usado como fonte de
        verdade pelo restante do pipeline.
        """

        logger.info("Gerando documento hipotético (HyDE)")

        question = question.strip()

        if not question:
            return question

        response = QueryClient._client.chat(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você escreve trechos de protocolos clínicos "
                        "veterinários. "
                        "A partir do relato de um tutor sobre seu "
                        "animal, escreva um trecho curto, como se "
                        "fosse retirado de um manual ou protocolo "
                        "veterinário, descrevendo o quadro clínico "
                        "correspondente, possíveis causas e a conduta "
                        "esperada. "
                        "Use terminologia técnica veterinária. "
                        "Não se dirija ao tutor, não faça perguntas, "
                        "não dê disclaimers. "
                        "Responda apenas com o trecho do protocolo, "
                        "em um único parágrafo curto."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            options=default_options(),
        )

        hypothetical_document = response["message"]["content"].strip()

        logger.info(
            f"Documento hipotético (HyDE) gerado: "
            f"{hypothetical_document}"
        )

        return hypothetical_document