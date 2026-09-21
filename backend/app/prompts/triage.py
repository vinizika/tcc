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

EMERGENCY_EVIDENCE_MARKERS = (
    "emergency facility",
    "emergency referral",
    "emergency evaluation",
    "immediate medical attention",
    "atendimento emergencial",
    "encaminhamento emergencial",
    "avaliacao emergencial",
    "atendimento imediato",
)


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
- justificativa: uma única frase, com no máximo 20 palavras, explicando a \
decisão em linguagem que o tutor entenda. Não liste procedimentos.
- sinais_de_alerta: no máximo três sinais preocupantes que aparecem no \
relato. Lista vazia se não houver nenhum.
- recomendacao: uma única frase, com no máximo 15 palavras, dizendo o que o \
tutor deve fazer agora. Sem nome de medicamento e sem dose. Em caso INCERTO, \
oriente procurar atendimento na dúvida.
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
- justificativa: uma única frase, com no máximo 20 palavras, explicando a \
decisão em linguagem que o tutor entenda. Não liste procedimentos.
- sinais_de_alerta: no máximo três sinais preocupantes que aparecem no \
relato. Lista vazia se não houver nenhum.
- recomendacao: uma única frase, com no máximo 15 palavras, dizendo o que o \
tutor deve fazer agora. Sem nome de medicamento e sem dose. Em caso INCERTO, \
oriente procurar atendimento na dúvida.

Responda em português."""


# ----------------------------------------------------------------------
# Chain-of-Thought
# ----------------------------------------------------------------------
#
# O checklist é estruturado, e não "analise passo a passo", por dois
# motivos medidos. Primeiro, num teste direto com este modelo o raciocínio
# livre chegou a escrever "condição médica grave, risco de choque" e ainda
# assim classificar como NAO_EMERGENCIA — pensar antes, sozinho, não aplica
# a regra. Segundo, o erro que se quer atacar tem forma conhecida: nas oito
# linhas erradas da linha de base, o modelo listou o sinal grave e depois
# rebaixou o caso por "faltam informações sobre gravidade ou duração".
# Tratar falta de informação como prova de leveza é exatamente o que o
# passo 1 e a regra final proíbem.
#
# O limite é estrutural (uma linha por sinal), e não "até N frases": um
# modelo de 3 bilhões de parâmetros não conta frases de forma confiável.

PASSOS_COT_SEM_CONTEXTO = """\
Antes de classificar, preencha o campo raciocinio assim:

1. Uma linha para cada sinal citado no relato, no formato \
"sinal — risco à vida? sim / não / não sei". Use "não sei" quando o relato \
não trouxer informação suficiente sobre aquele sinal; "não sei" nunca \
significa "não".
2. Uma linha final começando por "Conclusão:", aplicando esta regra: algum \
sinal com "sim" leva a EMERGENCIA; nenhum "sim" e algum "não sei" leva a \
INCERTO; todos "não" levam a NAO_EMERGENCIA.

O campo raciocinio contém apenas essas linhas. Não repita dentro dele os \
outros campos: cada um é preenchido no seu próprio lugar.

A classificação tem de ser a que a regra produziu, mesmo que pareça \
exagerada."""


PASSOS_COT = """\
Antes de classificar, preencha o campo raciocinio assim:

1. Uma linha para cada sinal citado no relato, no formato \
"sinal — risco à vida? sim / não / não sei". Use "não sei" quando o relato \
não trouxer informação suficiente sobre aquele sinal; "não sei" nunca \
significa "não".
2. Uma linha para cada trecho técnico numerado, no formato \
"[n] — descreve o caso deste relato? sim / não". Um trecho sobre outro \
problema recebe "não" e é ignorado daí em diante: ele não torna o caso \
leve nem grave.
3. Uma linha final começando por "Conclusão:", aplicando esta regra: algum \
sinal com "sim" leva a EMERGENCIA; nenhum "sim" e algum "não sei" leva a \
INCERTO; todos "não" levam a NAO_EMERGENCIA.

O campo raciocinio contém apenas essas linhas. Não repita dentro dele os \
outros campos: cada um é preenchido no seu próprio lugar.

A classificação tem de ser a que a regra produziu, mesmo que pareça \
exagerada."""


# A descrição do campo muda de lugar conforme o braço: no principal ele é o
# primeiro a ser escrito, no controle é o último. O texto precisa dizer
# isso porque o modelo não vê o schema — ele só sente a gramática
# restringindo a saída, e uma instrução que a contradissesse atrapalharia.
CAMPO_RACIOCINIO_PRIMEIRO = """\
- raciocinio: a análise descrita acima, uma linha por item. Escreva este \
campo primeiro, antes de decidir."""

CAMPO_RACIOCINIO_DEPOIS = """\
- raciocinio: a análise descrita acima, uma linha por item, registrada \
depois da classificação."""

_MARCADOR_CAMPOS = "Preencha os campos assim:"
_FECHAMENTO = "Responda em português."


def _com_cot(
    sistema: str,
    passos: str,
    campo: str,
    primeiro: bool,
) -> str:
    """
    Monta a versão CoT de um prompt de sistema.

    Os passos entram logo antes da lista de campos, e a descrição de
    `raciocinio` entra na posição correspondente à do schema: primeiro no
    braço principal, por último no controle. Se as duas discordassem, o
    modelo receberia uma instrução que a gramática contradiz.
    """

    antes, depois = sistema.split(_MARCADOR_CAMPOS, 1)

    campos = depois.replace(_FECHAMENTO, "").strip("\n")

    corpo = (
        f"{campo}\n{campos}"
        if primeiro
        else f"{campos}\n{campo}"
    )

    return (
        f"{antes}{passos}\n\n"
        f"{_MARCADOR_CAMPOS}\n{corpo}\n\n{_FECHAMENTO}"
    )


SISTEMA_ANCORADO_COT = _com_cot(
    SISTEMA_ANCORADO,
    PASSOS_COT,
    CAMPO_RACIOCINIO_PRIMEIRO,
    primeiro=True,
)

SISTEMA_ANCORADO_COT_SEM_CONTEXTO = _com_cot(
    SISTEMA_ANCORADO_SEM_CONTEXTO,
    PASSOS_COT_SEM_CONTEXTO,
    CAMPO_RACIOCINIO_PRIMEIRO,
    primeiro=True,
)

SISTEMA_ANCORADO_COT_POSTHOC = _com_cot(
    SISTEMA_ANCORADO,
    PASSOS_COT,
    CAMPO_RACIOCINIO_DEPOIS,
    primeiro=False,
)

SISTEMA_ANCORADO_COT_POSTHOC_SEM_CONTEXTO = _com_cot(
    SISTEMA_ANCORADO_SEM_CONTEXTO,
    PASSOS_COT_SEM_CONTEXTO,
    CAMPO_RACIOCINIO_DEPOIS,
    primeiro=False,
)


def _sistema_para(config: EffectiveConfig, com_documentos: bool) -> str:
    """
    Escolhe o prompt de sistema pelo braço que está rodando.
    """

    if not config.cot_enabled:
        return (
            SISTEMA_ANCORADO
            if com_documentos
            else SISTEMA_ANCORADO_SEM_CONTEXTO
        )

    if config.cot_position == "last":
        return (
            SISTEMA_ANCORADO_COT_POSTHOC
            if com_documentos
            else SISTEMA_ANCORADO_COT_POSTHOC_SEM_CONTEXTO
        )

    return (
        SISTEMA_ANCORADO_COT
        if com_documentos
        else SISTEMA_ANCORADO_COT_SEM_CONTEXTO
    )


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

        conteudo_normalizado = conteudo.casefold()
        marcador = (
            " [O TRECHO MENCIONA EXPLICITAMENTE ENCAMINHAMENTO EMERGENCIAL]"
            if any(
                termo in conteudo_normalizado
                for termo in EMERGENCY_EVIDENCE_MARKERS
            )
            else ""
        )
        linhas.append(
            f"[{posicao}]{marcador} {documento.title} — {conteudo}"
        )

    return "\n\n".join(linhas)


def build_triage_messages(
    relato: str,
    documents: list[RetrievedDocument],
    config: EffectiveConfig,
    rewritten: str | None = None,
    animal_context: str | None = None,
) -> list[dict]:
    """
    Monta as mensagens enviadas ao modelo.

    O relato original do tutor vai por último e delimitado: é entrada não
    confiável, e a posição final é a que o modelo pondera melhor.
    """

    if config.prompt_version == "v0_legacy":
        # Reproduz a medição de 04/05 ao pé da letra — `animal_context` não
        # entra aqui de propósito, mesmo quando o pet está cadastrado.
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

    # Vem do cadastro do pet (app/schemas/pet.py), não do relato — por isso
    # fica separado, como "dado de cadastro" e não como sinal clínico do
    # tutor. Um pet sem cadastro simplesmente não gera este bloco.
    if animal_context:
        partes.append(
            f"Dados cadastrais do animal, informados previamente pelo "
            f"tutor:\n{animal_context}"
        )

    # A reescrita da consulta acrescenta interpretação clínica, então por
    # padrão ela não chega ao classificador: isso misturaria a etapa de
    # consulta na decisão e confundiria o estudo de ablação.
    if config.rewritten_hint_enabled and rewritten:
        partes.append(f"Interpretação técnica auxiliar: {rewritten}")

    partes.append(f'Relato do tutor:\n"""\n{relato}\n"""')

    return [
        {"role": "system", "content": _sistema_para(config, bool(documents))},
        {"role": "user", "content": "\n\n".join(partes)},
    ]
