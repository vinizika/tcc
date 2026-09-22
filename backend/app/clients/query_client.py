import re

from app.core.config import settings
from app.core.logger import setup_logger
from app.core.ollama import default_options, get_ollama_client


logger = setup_logger("QueryClient")

# B-08: termos de urgência que a reescrita não pode introduzir por
# conta própria — são decisão do classificador, não da etapa de consulta.
_URGENCY_TERMS = (
    "imediata",
    "imediato",
    "urgente",
    "urgência",
    "emergência",
    "emergencial",
)


def _contains_unwarranted_urgency(original: str, rewritten: str) -> bool:
    original_lower = original.lower()
    rewritten_lower = rewritten.lower()

    return any(
        term in rewritten_lower and term not in original_lower
        for term in _URGENCY_TERMS
    )


# Prompts extraídos como constantes para que o comparador experimental
# Gemini x Ollama (gemini_query_client.py, 22/09) use exatamente o mesmo
# texto — a única variável do experimento deve ser o modelo, não o prompt.
REWRITE_SYSTEM_PROMPT = (
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
    "Nunca adicione julgamento de gravidade ou "
    "urgência (como 'urgente', 'imediata', "
    "'emergência') que não estava explícito no "
    "relato original — isso é decisão do "
    "classificador, não da reescrita. "
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
    "24 horas\n\n"
    "Exemplo do que NÃO fazer:\n"
    "Entrada: meu gato está espirrando\n"
    "Saída errada: gato apresentando espirro, "
    "sintoma que requer avaliação veterinária "
    "imediata (isto insere um juízo de urgência "
    "que o relato não tem)\n"
    "Saída correta: gato apresentando espirro"
)

MULTI_QUERY_SYSTEM_PROMPT = (
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
)

HYDE_SYSTEM_PROMPT = (
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
)


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
                    "content": REWRITE_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            options=default_options(),
        )

        rewritten_question = response["message"]["content"].strip()

        if _contains_unwarranted_urgency(question, rewritten_question):
            logger.warning(
                "Query Rewriting descartado (B-08): termo de urgência "
                "ausente do relato original apareceu na reescrita. "
                f"Reescrita descartada: {rewritten_question!r}"
            )
            return question

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
                    "content": MULTI_QUERY_SYSTEM_PROMPT,
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
                    "content": HYDE_SYSTEM_PROMPT,
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