"""
Métricas da régua de recuperação: a busca traz o protocolo certo?

Módulo puro — sem HTTP, sem banco. Recebe o que a busca devolveu por caso e
devolve números. É o irmão de `evaluation_metrics.py`, que mede o sistema
inteiro; aqui só a busca é julgada.

A diferença de fundo entre os dois: lá a nota é acurácia ("classificou
certo?"), aqui é **posição** ("o protocolo certo veio em primeiro?"). Medir
por posição foi decisão do trilho A, e é a certa — a nota de semelhança
deste embedder não separa relevância (evidencias/backlog.md#b-11), então
qualquer métrica baseada nela herdaria o problema.

Os casos vêm em três naturezas, e elas **não** se misturam nas contas:

- **com protocolo**: a base tem o documento certo; medem Precision@1, MRR e
  Recall@5;
- **caso leve**: a resposta certa é não trazer protocolo de emergência;
- **sem cobertura**: é emergência, mas a base não tem o assunto. Separado
  do anterior de propósito: "a busca acertou ao ficar quieta" e "a base não
  tem o que buscar" são diagnósticos diferentes, e o segundo é dado de
  curadoria, não nota da busca.
"""

from collections import Counter
from typing import Any, Optional


def _divisao(numerador: int, denominador: int) -> Optional[float]:
    """
    Sem denominador não existe taxa. Devolver zero seria mentir: diria
    "nenhum acerto" onde o certo é "não havia o que medir".
    """

    if not denominador:
        return None

    return round(numerador / denominador, 4)


def posicao_do_acerto(
    topicos_recuperados: list[str],
    esperados: list[str],
) -> Optional[int]:
    """
    Em que lugar da lista apareceu o primeiro protocolo aceitável (1 é o
    topo). None se não apareceu.

    O gabarito aceita um **conjunto** de protocolos porque um relato pode
    ter mais de uma resposta legítima — um cão atropelado e ofegante casa
    com trauma e com dificuldade respiratória.
    """

    aceitos = set(esperados)

    for posicao, topico in enumerate(topicos_recuperados, start=1):
        if topico in aceitos:
            return posicao

    return None


def avaliar_caso(caso: dict, recuperados: list[dict]) -> dict:
    """
    Julga um caso. `recuperados` é a lista ordenada que a busca devolveu,
    cada item com `topic`, `score` e, nas versões híbridas,
    `ranking_score`. O último é a nota realmente usada pelo corte do chat;
    snapshots antigos continuam comparáveis pelo fallback vetorial.
    """

    topicos = [documento.get("topic", "") for documento in recuperados]
    notas = [
        float(
            documento.get("ranking_score")
            if documento.get("ranking_score") is not None
            else documento.get("score", 0.0)
        )
        for documento in recuperados
    ]

    esperados = [
        topico
        for topico in (caso.get("expected_topics") or "").split(";")
        if topico
    ]

    motivo_vazio = (caso.get("expected_none_reason") or "").strip()

    resultado: dict[str, Any] = {
        "id": caso.get("id"),
        "natureza": motivo_vazio or "com protocolo",
        "expected_topics": esperados,
        "topics": topicos,
        "top1": topicos[0] if topicos else None,
        "max_score": max(notas) if notas else None,
        "n_returned": len(recuperados),
    }

    if esperados:
        posicao = posicao_do_acerto(topicos, esperados)
        resultado["posicao"] = posicao
        resultado["acertou_top1"] = posicao == 1
        resultado["reciproco"] = 1 / posicao if posicao else 0.0

    return resultado


def compute_retrieval_metrics(
    avaliados: list[dict],
    limiar: float = 0.70,
    recall_k: int = 5,
) -> dict:
    """
    Agrega os casos avaliados.

    `limiar` define o que conta como "a busca trouxe algo relevante" — é o
    mesmo corte que o classificador aplica desde 12/09
    (evidencias/joao/2026-09-12-10-corte-de-relevancia.md), e é provisório
    até esta régua dizer qual é o certo.
    """

    com_protocolo = [c for c in avaliados if c["natureza"] == "com protocolo"]
    leves = [c for c in avaliados if c["natureza"] == "caso leve"]
    sem_cobertura = [c for c in avaliados if c["natureza"] == "sem cobertura"]

    metricas: dict[str, Any] = {
        "n_casos": len(avaliados),
        "n_com_protocolo": len(com_protocolo),
        "n_caso_leve": len(leves),
        "n_sem_cobertura": len(sem_cobertura),
        "limiar": limiar,
    }

    # --- os casos que têm resposta na base
    acertos = sum(1 for c in com_protocolo if c.get("acertou_top1"))
    metricas["precision_at_1"] = _divisao(acertos, len(com_protocolo))

    if com_protocolo:
        soma = sum(c.get("reciproco", 0.0) for c in com_protocolo)
        metricas["mrr"] = round(soma / len(com_protocolo), 4)

        no_topo_k = sum(
            1
            for c in com_protocolo
            if c.get("posicao") and c["posicao"] <= recall_k
        )
        metricas[f"recall_at_{recall_k}"] = _divisao(
            no_topo_k, len(com_protocolo)
        )
    else:
        metricas["mrr"] = None
        metricas[f"recall_at_{recall_k}"] = None

    # --- silêncio: a busca soube não trazer nada?
    def silenciou(caso: dict) -> bool:
        return caso["max_score"] is None or caso["max_score"] < limiar

    metricas["silence_rate_on_mild"] = _divisao(
        sum(1 for c in leves if silenciou(c)), len(leves)
    )
    metricas["silence_rate_on_uncovered"] = _divisao(
        sum(1 for c in sem_cobertura if silenciou(c)), len(sem_cobertura)
    )

    # Quantos casos, no conjunto todo, tiveram algo acima do limiar. É o
    # número que diz se o silêncio acima é mérito ou acidente: se a busca
    # nunca passa do corte, ela "acerta" os leves sem saber por quê.
    metricas["share_cases_above_threshold"] = _divisao(
        sum(1 for c in avaliados if not silenciou(c)), len(avaliados)
    )

    # --- o protocolo-ímã
    #
    # Não estava no plano do trilho A, e é o achado do ensaio: um documento
    # aparecendo em primeiro lugar para assuntos que não são dele. Nenhuma
    # das três métricas clássicas mostra isso — todas olham o caso, não o
    # conjunto.
    primeiros = Counter(
        c["top1"] for c in avaliados if c.get("top1")
    )

    if primeiros:
        topico, vezes = primeiros.most_common(1)[0]
        metricas["top1_concentration"] = {
            "topic": topico,
            "cases": vezes,
            "share": _divisao(vezes, len(avaliados)),
            "distribution": dict(primeiros.most_common()),
        }

    # --- baselines triviais
    #
    # O mesmo cuidado que o runner de classificação tem desde setembro: sem
    # uma referência, "Precision@1 = 0,55" é um número solto. Duas
    # estratégias que não usam busca nenhuma:
    #
    # - escolher um documento ao acaso entre os da base;
    # - responder sempre o documento que mais aparece em primeiro lugar
    #   (o "protocolo-ímã", se houver).
    #
    # E a ressalva do Recall@k: ele só é informativo quando k for bem menor
    # que o número de documentos da base. Com uma base pequena, devolver k
    # trechos já mostra boa parte do acervo, e o recall vira quase
    # geométrico.
    documentos_na_base = {
        topico for c in avaliados for topico in c["topics"] if topico
    }
    metricas["n_documentos_vistos"] = len(documentos_na_base)

    if com_protocolo and documentos_na_base:
        # Acaso: a chance de sortear um aceitável, média sobre os casos.
        chance = sum(
            len(set(c["expected_topics"]) & documentos_na_base)
            / len(documentos_na_base)
            for c in com_protocolo
        ) / len(com_protocolo)

        baselines = {"documento_ao_acaso": round(chance, 4)}

        if metricas.get("top1_concentration"):
            ima = metricas["top1_concentration"]["topic"]
            baselines["sempre_o_mesmo_documento"] = _divisao(
                sum(
                    1
                    for c in com_protocolo
                    if ima in c["expected_topics"]
                ),
                len(com_protocolo),
            )

        # Quantos documentos distintos a busca mostra por caso. Se for
        # perto do total da base, o Recall@k não está medindo quase nada.
        distintos = [
            len({t for t in c["topics"] if t}) for c in avaliados
        ]
        if distintos:
            baselines["documentos_distintos_por_caso"] = round(
                sum(distintos) / len(distintos), 2
            )

        metricas["baselines"] = baselines

    metricas["mean_max_score"] = (
        round(
            sum(c["max_score"] for c in avaliados if c["max_score"] is not None)
            / max(1, sum(1 for c in avaliados if c["max_score"] is not None)),
            4,
        )
        if any(c["max_score"] is not None for c in avaliados)
        else None
    )

    return metricas
