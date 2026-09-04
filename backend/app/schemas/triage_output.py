"""
Modelos da saída clínica do LLM.

Estes modelos são convertidos em schema JSON e enviados ao Ollama no
parâmetro `format`, o que restringe a decodificação: os nomes dos campos e
os valores de classificação saem exatos, em vez de depender de o modelo
seguir a instrução do prompt. Na medição de 04/05, 97 das 98 respostas
vieram como JSON inválido antes de existir qualquer restrição de formato.

Duas regras valem para todo modelo que o LLM preenche:

1. Nenhum campo pode ser opcional nem ter valor padrão. O conversor de
   gramática do Ollama emite primeiro os campos obrigatórios, e um valor
   padrão tira o campo da lista de obrigatórios — o que mudaria a ordem em
   que o modelo escreve, algo que importa quando o raciocínio precisa vir
   antes da conclusão.
2. Listas têm tamanho máximo. Modelos pequenos com temperatura zero tendem
   a repetir itens até estourar o limite de tokens.
"""

import re
import unicodedata
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


Classificacao = Literal[
    "EMERGENCIA",
    "NAO_EMERGENCIA",
    "INCERTO",
]


def normalizar_classificacao(valor: Any) -> Any:
    """
    Aceita variações de escrita da classificação.

    No modo restrito por schema isto não é necessário, mas o modo JSON puro
    (usado para reproduzir a medição antiga) devolve coisas como
    "Nao Emergencia" ou "NÃO_EMERGENCIA".
    """

    if not isinstance(valor, str):
        return valor

    texto = unicodedata.normalize("NFKD", valor.strip().upper())
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return re.sub(r"[\s\-]+", "_", texto)


def normalizar_lista_de_texto(valor: Any) -> Any:
    """
    O modelo às vezes devolve um texto único onde se espera uma lista, ou
    nulo onde se espera lista vazia.
    """

    if valor is None:
        return []

    if isinstance(valor, str):
        valor = valor.strip()
        return [valor] if valor else []

    return valor


def normalizar_indices(valor: Any) -> Any:
    """
    As fontes são citadas por índice. No modo JSON puro o modelo pode
    devolver "1", "doc 2" ou repetir o mesmo índice.
    """

    if valor is None:
        return []

    if not isinstance(valor, list):
        valor = [valor]

    indices: list[int] = []

    for item in valor:
        if isinstance(item, bool):
            continue

        if isinstance(item, int):
            numero = item
        elif isinstance(item, str):
            encontrado = re.search(r"\d+", item)
            if not encontrado:
                continue
            numero = int(encontrado.group())
        else:
            continue

        if numero > 0 and numero not in indices:
            indices.append(numero)

    return indices


class TriageLLMOutput(BaseModel):
    """
    Saída da classificação quando há trechos recuperados no prompt.
    """

    classificacao: Classificacao
    justificativa: str
    sinais_de_alerta: list[str] = Field(max_length=8)
    recomendacao: str
    fontes: list[int] = Field(max_length=5)

    _normalizar_classificacao = field_validator(
        "classificacao",
        mode="before",
    )(normalizar_classificacao)

    _normalizar_sinais = field_validator(
        "sinais_de_alerta",
        mode="before",
    )(normalizar_lista_de_texto)

    _normalizar_fontes = field_validator(
        "fontes",
        mode="before",
    )(normalizar_indices)


class TriageLLMOutputSemContexto(BaseModel):
    """
    Saída quando o prompt não traz trechos.

    Sem o campo de fontes de propósito: não havendo o que citar, a
    restrição de formato impede o modelo de inventar um índice.
    """

    classificacao: Classificacao
    justificativa: str
    sinais_de_alerta: list[str] = Field(max_length=8)
    recomendacao: str

    _normalizar_classificacao = field_validator(
        "classificacao",
        mode="before",
    )(normalizar_classificacao)

    _normalizar_sinais = field_validator(
        "sinais_de_alerta",
        mode="before",
    )(normalizar_lista_de_texto)


class LegacyTriageLLMOutput(BaseModel):
    """
    Saída do modo legado, usado para reproduzir a medição de 04/05.

    Tolerante de propósito: das 98 respostas daquela rodada, 5 não tinham o
    campo de recomendação (4 delas por causa de um erro de digitação do
    próprio modelo), uma não tinha sinais de alerta e duas o traziam em
    formato diferente. O runner antigo lia apenas a classificação, e é isso
    que precisa ser reproduzido — exigir o resto transformaria em erro
    respostas que na época contaram como acerto.
    """

    classificacao: Classificacao
    justificativa: str = ""
    sinais_de_alerta: list[str] = []
    recomendacao: str = ""

    _normalizar_classificacao = field_validator(
        "classificacao",
        mode="before",
    )(normalizar_classificacao)

    _normalizar_sinais = field_validator(
        "sinais_de_alerta",
        mode="before",
    )(normalizar_lista_de_texto)

    @field_validator("justificativa", "recomendacao", mode="before")
    @classmethod
    def texto_ausente_vira_vazio(cls, valor: Any) -> Any:
        return "" if valor is None else valor

    @classmethod
    def model_validate_legado(cls, dados: dict) -> "LegacyTriageLLMOutput":
        """
        Aceita o erro de digitação "recomendaacao", observado em 4 das 98
        respostas da medição original.
        """

        if isinstance(dados, dict) and "recomendacao" not in dados:
            for chave in ("recomendaacao", "recomendação"):
                if chave in dados:
                    dados = {**dados, "recomendacao": dados[chave]}
                    break

        return cls.model_validate(dados)


class CitedSource(BaseModel):
    """
    Um trecho citado pelo modelo, já resolvido para o documento real.
    """

    index: int
    chunk_id: str
    title: str
    source: str


class TriageResult(BaseModel):
    """
    O que a API expõe: a classificação mais o que permite auditá-la.
    """

    classificacao: Classificacao
    justificativa: str
    sinais_de_alerta: list[str] = []
    recomendacao: str
    fontes: list[CitedSource] = []
    raciocinio: Optional[str] = None

    # Instrumentação: separa "o modelo devolveu um JSON" de "o JSON tinha o
    # formato esperado". As duas coisas foram problema na medição antiga e
    # viram métricas distintas no runner.
    json_parsed: bool = True
    schema_valid: bool = True
    attempts: int = 1
    done_reason: Optional[str] = None

    # Índices citados que não existiam no contexto enviado.
    invalid_source_indices: list[int] = []
