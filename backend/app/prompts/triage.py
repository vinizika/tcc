"""
Prompts da classificação de urgência.

Duas versões convivem de propósito:

- `v0_legacy` reproduz o prompt que produziu a medição de 04/05 (70,41% de
  acurácia). Existe para que a comparação "antes e depois do RAG" meça a
  mesma coisa; não deve ser alterado.
- `v1_grounded` é o prompt em uso, que recebe os trechos recuperados.

Sobre o formato: o Ollama não mostra o schema ao modelo, apenas restringe a
decodificação. Então cada campo esperado precisa estar descrito aqui, mesmo
que o schema já o imponha.
"""

from app.models.retrieved_document import RetrievedDocument
from app.schemas.triage import EffectiveConfig


# Teto do bloco de contexto. O Ollama descarta silenciosamente o começo do
# prompt quando ele passa do tamanho da janela, e o começo é justamente
# onde estão as instruções.
CONTEXT_MAX_CHARS = 4000


PROMPT_LEGADO = """
Você é um assistente de apoio à triagem veterinária.

Sua tarefa não é diagnosticar.
Sua tarefa é analisar o relato do tutor e classificar o caso como:
- EMERGENCIA
- NAO_EMERGENCIA
- INCERTO

Responda obrigatoriamente em JSON válido.
Não escreva nada antes ou depois do JSON.

O JSON deve ter exatamente estes campos:
- classificacao
- justificativa
- sinais_de_alerta
- recomendacao

A classificação deve ser exatamente uma destas opções:
- EMERGENCIA
- NAO_EMERGENCIA
- INCERTO

Não use acentos nos nomes dos campos.
Não use "recomendação". Use "recomendacao".
Não use "NAO EMERGENCIA". Use "NAO_EMERGENCIA".

Dados do caso:
Espécie: {especie}
Idade: {idade}
Relato do tutor: {relato}
"""


# Bloco fixo, sem números nem datas: assim o Ollama reaproveita o prefixo
# já processado entre requisições, em vez de recalcular tudo.
SISTEMA_ANCORADO = """\
Você apoia a pré-triagem veterinária de cães e gatos, lendo o relato de um \
tutor leigo e indicando a urgência do caso.

Você não diagnostica, não prescreve medicamentos e não calcula doses.

Classifique em exatamente uma destas categorias:
- EMERGENCIA: há sinal que indica risco à vida ou sofrimento intenso, e o \
animal precisa de atendimento imediato.
- NAO_EMERGENCIA: os sinais relatados são leves e podem aguardar uma \
consulta comum.
- INCERTO: o relato não traz informação suficiente para decidir.

Regras de decisão:
- Considere apenas sinais que estejam no relato do tutor. Não suponha \
sintomas que não foram mencionados.
- Um único sinal grave basta para EMERGENCIA. A ausência de outros \
sintomas não torna o caso leve.
- Se um trecho técnico descrever a situação do relato e indicar risco, \
classifique como EMERGENCIA e cite esse trecho em fontes.
- Se um trecho tratar de outro problema, ignore-o. Um trecho fora do \
assunto não torna o caso uma emergência.
- Se o relato não trouxer informação suficiente para decidir, responda \
INCERTO.

Preencha os campos assim:
- classificacao: uma das três categorias, exatamente como escritas acima.
- justificativa: duas a três frases explicando a decisão, em linguagem \
que o tutor entenda.
- sinais_de_alerta: apenas os sinais preocupantes que aparecem no relato. \
Lista vazia se não houver nenhum.
- recomendacao: o que o tutor deve fazer agora. Sem nome de medicamento e \
sem dose. Em caso INCERTO, diga que informação ajudaria e oriente procurar \
atendimento na dúvida.
- fontes: os números dos trechos que embasaram a decisão. Lista vazia se \
nenhum trecho foi usado.

Responda em português."""


SISTEMA_ANCORADO_SEM_CONTEXTO = """\
Você apoia a pré-triagem veterinária de cães e gatos, lendo o relato de um \
tutor leigo e indicando a urgência do caso.

Você não diagnostica, não prescreve medicamentos e não calcula doses.

Classifique em exatamente uma destas categorias:
- EMERGENCIA: há sinal que indica risco à vida ou sofrimento intenso, e o \
animal precisa de atendimento imediato.
- NAO_EMERGENCIA: os sinais relatados são leves e podem aguardar uma \
consulta comum.
- INCERTO: o relato não traz informação suficiente para decidir.

Regras de decisão:
- Considere apenas sinais que estejam no relato do tutor. Não suponha \
sintomas que não foram mencionados.
- Um único sinal grave basta para EMERGENCIA. A ausência de outros \
sintomas não torna o caso leve.
- Se o relato não trouxer informação suficiente para decidir, responda \
INCERTO.

Preencha os campos assim:
- classificacao: uma das três categorias, exatamente como escritas acima.
- justificativa: duas a três frases explicando a decisão, em linguagem \
que o tutor entenda.
- sinais_de_alerta: apenas os sinais preocupantes que aparecem no relato. \
Lista vazia se não houver nenhum.
- recomendacao: o que o tutor deve fazer agora. Sem nome de medicamento e \
sem dose. Em caso INCERTO, diga que informação ajudaria e oriente procurar \
atendimento na dúvida.

Responda em português."""


def montar_bloco_de_contexto(
    documents: list[RetrievedDocument],
) -> str:
    """
    Numera os trechos recuperados. O número é como o modelo cita a fonte:
    pedir o identificador do trecho levaria a citações inventadas.
    """

    linhas = []
    total = 0

    for posicao, documento in enumerate(documents, start=1):
        conteudo = " ".join(documento.content.split())

        if total + len(conteudo) > CONTEXT_MAX_CHARS:
            conteudo = conteudo[: max(0, CONTEXT_MAX_CHARS - total)]

        if not conteudo:
            break

        total += len(conteudo)

        linhas.append(f"[{posicao}] {documento.title} — {conteudo}")

    return "\n\n".join(linhas)


def build_triage_messages(
    relato: str,
    documents: list[RetrievedDocument],
    config: EffectiveConfig,
    rewritten: str | None = None,
) -> list[dict]:
    """
    Monta as mensagens enviadas ao modelo.

    O relato original do tutor vai por último e delimitado: é entrada não
    confiável, e a posição final é a que o modelo pondera melhor.
    """

    if config.prompt_version == "v0_legacy":
        return [
            {
                "role": "user",
                "content": PROMPT_LEGADO.format(
                    especie="não informado",
                    idade="não informado",
                    relato=relato,
                ),
            }
        ]

    partes = []

    if documents:
        partes.append("Trechos de protocolos veterinários:")
        partes.append(montar_bloco_de_contexto(documents))

    # A reescrita da consulta acrescenta interpretação clínica, então por
    # padrão ela não chega ao classificador: isso misturaria a etapa de
    # consulta na decisão e confundiria o estudo de ablação.
    if config.rewritten_hint_enabled and rewritten:
        partes.append(f"Interpretação técnica auxiliar: {rewritten}")

    partes.append(f'Relato do tutor:\n"""\n{relato}\n"""')

    sistema = (
        SISTEMA_ANCORADO
        if documents
        else SISTEMA_ANCORADO_SEM_CONTEXTO
    )

    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": "\n\n".join(partes)},
    ]
