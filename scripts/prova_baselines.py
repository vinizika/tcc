"""
Baselines triviais da prova nova — os substitutos que a seção 5.4 do plano
(docs/plano-base-e-prova.md) pede para o antigo "conta sintomas" do B-05,
que não funciona mais com texto livre.

Módulo puro — sem HTTP, sem banco, sem I/O de arquivo. Recebe a lista de
casos (dicts com pelo menos `text` e `expected_class`) e devolve números.
É o instrumento que denuncia se a prova nova também é trivialmente
separável (critério do B-05: nenhuma regra sem modelo passa de 0,90).

Três baselines, do mais simples ao mais forte:

- **palavra de alarme**: regra fixa, sem treino — contém uma palavra da
  lista de sinais de alerta? Prediz EMERGENCIA.
- **comprimento do relato**: um único limiar (em número de palavras),
  escolhido por validação cruzada para não relatar um número otimista
  ajustado nos mesmos dados que ele é avaliado.
- **saco de palavras**: Naive Bayes multinomial simples (contagem de
  palavras por classe, suavização de Laplace), também por validação
  cruzada. É o mais forte dos três porque pode aprender qualquer
  vocabulário que vaze entre as classes — inclusive o tipo de tique de
  escrita que a rodada 12 já registrou ("agora"/"comendo").

Todos os três ignoram casos `INCERTO`: as duas classes binárias
(EMERGENCIA/NAO_EMERGENCIA) são o que esses baselines tentam separar: prever
"incerto" sem nenhum critério do que isso significa não faz sentido para
uma regra de saco de palavras.
"""

import math
import re
from collections import Counter
from typing import Any

# Vocabulário de sinais de alerta, escolhido por conhecimento geral de
# triagem — não ajustado nem lido do resultado desta prova. É a mesma
# disciplina de "resultado esperado antes de medir": se a lista fosse
# escolhida depois de olhar os casos, a medição perderia o sentido.
PALAVRAS_DE_ALARME = frozenset(
    {
        "sangue", "sangrando", "sangramento", "convulsao", "convulsionando",
        "convulsoes", "desmaiou", "desmaio", "morrendo", "morte", "veneno",
        "envenenado", "atropelado", "atropelou", "gritando", "grito",
        "roxa", "roxo", "arroxeada", "arroxeado", "palida", "palido",
        "inchando", "inchado", "engasgado", "engasgando", "urgente",
        "emergencia", "socorro", "gelado", "gelada",
    }
)

CLASSES_BINARIAS = ("EMERGENCIA", "NAO_EMERGENCIA")


def normaliza_palavras(texto: str) -> list[str]:
    return re.findall(r"[a-zà-ú0-9]+", texto.lower())


def _casos_binarios(casos: list[dict]) -> list[dict]:
    return [caso for caso in casos if caso["expected_class"] in CLASSES_BINARIAS]


def _dobras_estratificadas(casos: list[dict], k: int) -> list[list[dict]]:
    """
    k dobras, cada classe distribuída round-robin depois de ordenar por id
    — determinístico (sem embaralhar com semente), e mantém as duas classes
    representadas em toda dobra mesmo com k grande.
    """

    dobras: list[list[dict]] = [[] for _ in range(k)]

    for classe in CLASSES_BINARIAS:
        da_classe = sorted(
            (caso for caso in casos if caso["expected_class"] == classe),
            key=lambda caso: caso["id"],
        )
        for indice, caso in enumerate(da_classe):
            dobras[indice % k].append(caso)

    return dobras


def baseline_palavra_de_alarme(casos: list[dict]) -> dict[str, Any]:

    binarios = _casos_binarios(casos)
    acertos = 0

    for caso in binarios:
        palavras = set(normaliza_palavras(caso["text"]))
        previsto = (
            "EMERGENCIA"
            if palavras & PALAVRAS_DE_ALARME
            else "NAO_EMERGENCIA"
        )
        acertos += previsto == caso["expected_class"]

    total = len(binarios)

    return {
        "nome": "palavra_de_alarme",
        "acuracia": round(acertos / total, 4) if total else None,
        "n": total,
    }


def _melhor_limiar_comprimento(casos_treino: list[dict]) -> int:
    """
    Testa todo limiar possível (cada comprimento observado no treino) e
    fica com o que mais acerta — "acima do limiar é emergência" ou o
    inverso, o que for melhor nesta dobra de treino.
    """

    comprimentos = sorted(
        {len(normaliza_palavras(caso["text"])) for caso in casos_treino}
    )

    melhor_limiar = comprimentos[0]
    melhor_acerto = -1
    melhor_direcao = True

    for limiar in comprimentos:
        for direcao in (True, False):
            acertos = 0
            for caso in casos_treino:
                tamanho = len(normaliza_palavras(caso["text"]))
                acima = tamanho >= limiar
                previsto = (
                    "EMERGENCIA" if (acima == direcao) else "NAO_EMERGENCIA"
                )
                acertos += previsto == caso["expected_class"]
            if acertos > melhor_acerto:
                melhor_acerto = acertos
                melhor_limiar = limiar
                melhor_direcao = direcao

    return melhor_limiar, melhor_direcao


def baseline_comprimento_cv(casos: list[dict], k: int = 5) -> dict[str, Any]:

    binarios = _casos_binarios(casos)
    dobras = _dobras_estratificadas(binarios, k)

    acertos_totais = 0
    total = 0

    for indice_teste in range(k):
        teste = dobras[indice_teste]
        treino = [
            caso
            for indice_treino, dobra in enumerate(dobras)
            if indice_treino != indice_teste
            for caso in dobra
        ]

        limiar, direcao = _melhor_limiar_comprimento(treino)

        for caso in teste:
            tamanho = len(normaliza_palavras(caso["text"]))
            acima = tamanho >= limiar
            previsto = "EMERGENCIA" if (acima == direcao) else "NAO_EMERGENCIA"
            acertos_totais += previsto == caso["expected_class"]
            total += 1

    return {
        "nome": "comprimento_do_relato",
        "acuracia": round(acertos_totais / total, 4) if total else None,
        "n": total,
        "k_dobras": k,
    }


def _treinar_saco_de_palavras(casos_treino: list[dict]):

    contagem = {classe: Counter() for classe in CLASSES_BINARIAS}
    total_palavras = {classe: 0 for classe in CLASSES_BINARIAS}
    total_casos = {classe: 0 for classe in CLASSES_BINARIAS}

    for caso in casos_treino:
        classe = caso["expected_class"]
        palavras = normaliza_palavras(caso["text"])
        contagem[classe].update(palavras)
        total_palavras[classe] += len(palavras)
        total_casos[classe] += 1

    vocabulario = set(contagem["EMERGENCIA"]) | set(contagem["NAO_EMERGENCIA"])
    n_total = sum(total_casos.values())
    prior = {
        classe: total_casos[classe] / n_total for classe in CLASSES_BINARIAS
    }

    return contagem, total_palavras, vocabulario, prior


def _prever_saco_de_palavras(texto, contagem, total_palavras, vocabulario, prior):

    palavras = normaliza_palavras(texto)
    tam_vocab = max(len(vocabulario), 1)
    log_prob = {}

    for classe in CLASSES_BINARIAS:
        logp = math.log(prior[classe]) if prior[classe] > 0 else float("-inf")
        for palavra in palavras:
            freq = contagem[classe].get(palavra, 0)
            logp += math.log(
                (freq + 1) / (total_palavras[classe] + tam_vocab)
            )
        log_prob[classe] = logp

    return max(log_prob, key=log_prob.get)


def baseline_saco_de_palavras_cv(casos: list[dict], k: int = 5) -> dict[str, Any]:
    """
    Naive Bayes multinomial, validado por k dobras. É o baseline mais forte
    dos três: se ele também ficar abaixo de 0,90, a prova resiste até a
    tentativa mais direta de "aprender" as classes só pelo vocabulário.
    """

    binarios = _casos_binarios(casos)
    dobras = _dobras_estratificadas(binarios, k)

    acertos_totais = 0
    total = 0

    for indice_teste in range(k):
        teste = dobras[indice_teste]
        treino = [
            caso
            for indice_treino, dobra in enumerate(dobras)
            if indice_treino != indice_teste
            for caso in dobra
        ]

        contagem, total_palavras, vocabulario, prior = _treinar_saco_de_palavras(
            treino
        )

        for caso in teste:
            previsto = _prever_saco_de_palavras(
                caso["text"], contagem, total_palavras, vocabulario, prior
            )
            acertos_totais += previsto == caso["expected_class"]
            total += 1

    return {
        "nome": "saco_de_palavras_naive_bayes",
        "acuracia": round(acertos_totais / total, 4) if total else None,
        "n": total,
        "k_dobras": k,
    }


def compute_baselines(casos: list[dict], k: int = 5) -> dict[str, dict]:

    return {
        "palavra_de_alarme": baseline_palavra_de_alarme(casos),
        "comprimento_do_relato": baseline_comprimento_cv(casos, k=k),
        "saco_de_palavras": baseline_saco_de_palavras_cv(casos, k=k),
    }
