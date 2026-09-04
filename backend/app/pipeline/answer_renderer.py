"""
Transforma a classificação estruturada no texto que o tutor lê.

A renderização é feita em código, e não pedida ao modelo: assim o formato
da resposta é sempre o mesmo, e a única coisa que varia é o conteúdo
clínico. Isso também evita gastar tokens gerando cabeçalho e aviso legal.
"""

import re

from app.schemas.triage_output import TriageResult


AVISO = (
    "Este sistema apoia a pré-triagem e não substitui a avaliação de um "
    "médico-veterinário."
)

TITULOS = {
    "EMERGENCIA": "Emergência: procure atendimento agora",
    "NAO_EMERGENCIA": "Não parece emergência",
    "INCERTO": "Não foi possível determinar a urgência",
}

# O texto vem do modelo e é renderizado como markdown pela interface.
# Estes caracteres mudam a formatação em qualquer posição: um asterisco
# solto vira itálico, "R$ 50 ... $" vira fórmula, ":red[...]" vira
# diretiva de cor do Streamlit.
CARACTERES_INLINE = re.compile(r"([\\`*_\[\]<>|~$:])")

# Estes só viram estrutura no começo da linha: título, item de lista,
# citação ou lista numerada.
MARCADOR_SIMBOLO = re.compile(r"^([#>+-])(\s)")
MARCADOR_NUMERADO = re.compile(r"^(\d+)(\.)(\s)")


def escapar(texto: str) -> str:
    """
    Neutraliza a formatação sem sujar a leitura: escapa o que altera o
    markdown, e não toda a pontuação.
    """

    if not texto:
        return ""

    # Quebras de linha viram espaço para não partirem um item de lista.
    texto = " ".join(str(texto).split())

    texto = CARACTERES_INLINE.sub(r"\\\1", texto)

    texto = MARCADOR_SIMBOLO.sub(r"\\\1\2", texto)

    # Numa lista numerada, quem cria a estrutura é o ponto, não o dígito.
    return MARCADOR_NUMERADO.sub(r"\1\\\2\3", texto)


def render(triage: TriageResult, sources: list | None = None) -> str:

    titulo = TITULOS.get(triage.classificacao, triage.classificacao)

    linhas = [f"**{titulo}**"]

    if not triage.schema_valid:
        linhas.append(
            "Não foi possível estruturar a resposta do modelo. Por "
            "segurança, o caso não foi classificado."
        )

    if triage.justificativa:
        linhas.append(escapar(triage.justificativa))

    if triage.sinais_de_alerta:
        linhas.append("**Sinais observados no relato**")
        linhas.append(
            "\n".join(
                f"- {escapar(sinal)}"
                for sinal in triage.sinais_de_alerta
            )
        )

    if triage.recomendacao:
        linhas.append("**O que fazer**")
        linhas.append(escapar(triage.recomendacao))

    if triage.fontes:
        linhas.append("**Baseado em**")
        linhas.append(
            "\n".join(
                f"- {escapar(fonte.title)} ({escapar(fonte.source)})"
                for fonte in triage.fontes
            )
        )

    linhas.append(f"_{AVISO}_")

    return "\n\n".join(linhas)
