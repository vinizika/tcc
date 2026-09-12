"""
Compara duas rodadas da régua de recuperação: o que mudou entre elas.

A ampliação da base acontece em lotes, e a pergunta a cada lote é sempre a
mesma — melhorou, piorou, ou não mudou? O risco concreto não é deixar de ver
uma melhora: é **deixar de ver uma piora**. Uma base maior pode espalhar o
assunto certo e empurrar o documento correto para baixo, e a rodada 10 mediu
quanto custa ruído recuperado (22 emergências classificadas como leves).

Módulo puro: recebe dicionários, devolve dicionários. Sem HTTP, sem disco —
quem lê arquivo é `run_retrieval_eval.py compare`.

**A régua é determinística**, e isso muda a leitura em relação ao compare da
classificação. Duas rodadas sobre a mesma base devolvem posições e notas
idênticas (verificado em `20260911-201429` × `20260911-202505`). Não há ruído
de sessão para separar do sinal: um caso que piorou, piorou. Por isso aqui
não há McNemar nem bootstrap — só contagens e diferenças.
"""

import json
import math
from pathlib import Path
from typing import Any, Optional

from retrieval_metrics import avaliar_caso, compute_retrieval_metrics

# Quanto o protocolo-ímã pode ocupar do primeiro lugar antes de a porta de
# decisão reprovar. Está em data/curadoria/README.md; hoje "trauma" ocupa
# metade dos casos, o que reprova.
LIMITE_IMA = 1 / 3

# Fração dos quadros recém-indexados que precisa aparecer no top-5 do próprio
# caso. Documento que entrou na base e nunca é recuperado é cobertura no
# papel — e o critério da porta existe para separar as duas coisas.
MINIMO_COBERTURA_REAL = 0.70

# As três grafias de espécie que as fichas da base usam hoje (B-53). O trilho
# A fecha o vocabulário; até lá o compare normaliza e avisa.
ESPECIES = {
    "dog": "cao",
    "dogs": "cao",
    "cao": "cao",
    "cat": "gato",
    "cats": "gato",
    "gato": "gato",
    "dogs_and_cats": "ambos",
    "dog_and_cat": "ambos",
    "ambos": "ambos",
}


def normalizar_especie(valor: str) -> str:
    """
    Traduz a espécie da ficha para o vocabulário do mapa.

    Sem isto, `cats` da ficha nunca casaria com `gato` do mapa e a cobertura
    por espécie sairia errada **em silêncio** — que é exatamente o risco que
    o B-53 descreve.
    """

    return ESPECIES.get((valor or "").strip().lower(), "")


def ordenar_posicao(posicao: Optional[int]) -> float:
    """
    `None` é "não apareceu entre os cinco devolvidos", e isso é pior que
    qualquer posição — não melhor que todas.

    Tratar `None` como zero faria "sumiu da lista" ser contado como
    "melhorou", que é a leitura mais perigosa que este arquivo poderia
    produzir.
    """

    return math.inf if posicao is None else float(posicao)


def carregar_rodada(diretorio: Path) -> dict:
    """
    Lê uma rodada do disco e reconstrói o que o `results.jsonl` não grava.

    A rodada guarda `posicao` e a lista de documentos, mas não `top1`,
    `max_score` nem `topics` — eles ficavam só em memória. Recalcular com
    `avaliar_caso` garante que o compare usa exatamente a mesma definição que
    a régua usou, em vez de uma paralela que poderia divergir com o tempo.
    """

    manifesto = json.loads(
        (diretorio / "manifest.json").read_text(encoding="utf-8")
    )

    casos = []
    avaliados = []

    for linha in (diretorio / "results.jsonl").read_text(
        encoding="utf-8"
    ).splitlines():
        if not linha.strip():
            continue

        registro = json.loads(linha)
        casos.append(registro)

        # `avaliar_caso` espera o formato do CSV, com os tópicos separados
        # por `;`; o results.jsonl já gravou uma lista. Sem reserializar, um
        # `"".join` partiria a string caractere a caractere, sem erro.
        avaliados.append(
            avaliar_caso(
                {
                    "id": registro["id"],
                    "expected_topics": ";".join(registro["expected_topics"]),
                    "expected_none_reason": registro["expected_none_reason"],
                },
                registro["documents"],
            )
        )

    return {
        "diretorio": diretorio,
        "run_id": manifesto.get("run_id", diretorio.name),
        "manifesto": manifesto,
        "casos": {c["id"]: c for c in casos},
        "avaliados": {a["id"]: a for a in avaliados},
    }


def parear(a: dict, b: dict) -> dict:
    """
    Decide quais casos entram na comparação.

    A regra é a interseção dos ids, e não a igualdade do `cases.csv`. O
    motivo é concreto: cada lote de fontes traz relatos de régua novos, então
    o arquivo muda a cada lote — uma trava por hash do arquivo abortaria
    sempre, e o instrumento nasceria inútil.

    O que **aborta** é outra coisa: um caso com o mesmo id ter mudado de
    texto ou de gabarito entre as duas rodadas. Aí "antes e depois" deixaria
    de ser sobre a mesma pergunta.
    """

    limiar_a = a["manifesto"].get("limiar")
    limiar_b = b["manifesto"].get("limiar")

    if limiar_a != limiar_b:
        raise SystemExit(
            f"As rodadas usaram limiares diferentes ({limiar_a} e "
            f"{limiar_b}). Os blocos de ruído dependem do corte: comparar "
            "mediria a mudança de limiar, não a de base."
        )

    comuns = sorted(set(a["casos"]) & set(b["casos"]))

    if not comuns:
        raise SystemExit("As rodadas não têm nenhum caso em comum.")

    for caso_id in comuns:
        caso_a, caso_b = a["casos"][caso_id], b["casos"][caso_id]

        if caso_a["text"] != caso_b["text"]:
            raise SystemExit(
                f"O caso {caso_id} tem textos diferentes nas duas rodadas. "
                "O gabarito mudou: refaça a rodada antiga sobre os casos "
                "atuais, ou compare com outra."
            )

        if caso_a["expected_topics"] != caso_b["expected_topics"]:
            raise SystemExit(
                f"O caso {caso_id} espera protocolos diferentes nas duas "
                "rodadas. O gabarito mudou, e antes/depois não mede a base."
            )

    return {
        "comuns": comuns,
        "so_em_a": sorted(set(a["casos"]) - set(b["casos"])),
        "so_em_b": sorted(set(b["casos"]) - set(a["casos"])),
        "limiar": limiar_b,
    }


def _delta(antes: Optional[float], depois: Optional[float]) -> Optional[float]:
    """Diferença que tolera `None` dos dois lados — sem taxa não há delta."""

    if antes is None or depois is None:
        return None

    return round(depois - antes, 4)


def comparar_base(a: dict, b: dict) -> dict:
    """
    O que mudou na base vetorial entre as duas rodadas.

    Aqui o compare da régua se separa do da classificação. Lá, base diferente
    é suspeita ("o sistema não era o mesmo"); aqui é **o evento medido** — a
    rodada existe justamente para dizer o efeito de indexar. O que merece
    aviso é o contrário: base **igual**, porque então não se indexou nada e
    tudo deveria dar zero.
    """

    loja_a = (a["manifesto"].get("backend_fingerprint") or {}).get(
        "vector_store"
    ) or {}
    loja_b = (b["manifesto"].get("backend_fingerprint") or {}).get(
        "vector_store"
    ) or {}

    mesma = loja_a.get("chunk_ids_sha256") == loja_b.get("chunk_ids_sha256")

    avisos = []

    for chave, rotulo in (
        ("embedding_model", "o modelo de embedding"),
        ("chunking", "a receita de chunking"),
    ):
        if chave in loja_a and chave in loja_b and loja_a[chave] != loja_b[chave]:
            avisos.append(
                f"{rotulo} mudou entre as rodadas ({loja_a[chave]} → "
                f"{loja_b[chave]}). A diferença medida abaixo não é só dos "
                "documentos novos."
            )

    return {
        "chunk_count": [loja_a.get("chunk_count"), loja_b.get("chunk_count")],
        "chunk_ids_sha256": [
            loja_a.get("chunk_ids_sha256"),
            loja_b.get("chunk_ids_sha256"),
        ],
        "content_sha256": [
            loja_a.get("content_sha256"),
            loja_b.get("content_sha256"),
        ],
        "mesma_base": mesma,
        "avisos": avisos,
    }


def comparar_ordenacao(a: dict, b: dict, comuns: list[str]) -> dict:
    """
    A tabela pareada: onde cada caso estava e onde foi parar.

    É o bloco que o B-51 chama de guarda de regressão. A média pode subir
    enquanto um caso específico piora, e é o caso que importa quando o
    assunto é triagem.
    """

    metricas_a = compute_retrieval_metrics(
        [a["avaliados"][i] for i in comuns], limiar=a["manifesto"]["limiar"]
    )
    metricas_b = compute_retrieval_metrics(
        [b["avaliados"][i] for i in comuns], limiar=b["manifesto"]["limiar"]
    )

    casos = []

    for caso_id in comuns:
        avaliado_a, avaliado_b = a["avaliados"][caso_id], b["avaliados"][caso_id]

        if not avaliado_b["expected_topics"]:
            continue

        antes = avaliado_a.get("posicao")
        depois = avaliado_b.get("posicao")

        if antes is None and depois is None:
            situacao = "igual"
        elif antes is None:
            situacao = "entrou"
        elif depois is None:
            situacao = "saiu"
        elif depois < antes:
            situacao = "melhorou"
        elif depois > antes:
            situacao = "piorou"
        else:
            situacao = "igual"

        casos.append(
            {
                "id": caso_id,
                "esperado": avaliado_b["expected_topics"],
                "antes": antes,
                "depois": depois,
                "situacao": situacao,
            }
        )

    def conta(*situacoes):
        return sum(1 for c in casos if c["situacao"] in situacoes)

    return {
        "metricas": {
            chave: [metricas_a.get(chave), metricas_b.get(chave)]
            for chave in ("precision_at_1", "mrr", "recall_at_5")
        },
        "deltas": {
            chave: _delta(metricas_a.get(chave), metricas_b.get(chave))
            for chave in ("precision_at_1", "mrr", "recall_at_5")
        },
        "casos": casos,
        # "Saiu do top-5" é piora: o protocolo certo deixou de ser
        # recuperado. "Entrou" é melhora pelo mesmo motivo.
        "melhoraram": conta("melhorou", "entrou"),
        "pioraram": conta("piorou", "saiu"),
        "iguais": conta("igual"),
    }


def comparar_ruido(a: dict, b: dict, comuns: list[str], limiar: float) -> dict:
    """
    O mecanismo que custou 22 falsos não urgentes, vigiado a cada lote.

    Três coisas: o protocolo-ímã cresceu? mais casos passaram do corte? e —
    o mais importante — algum **caso leve** passou a receber trecho acima do
    corte, que é o ruído entrando no prompt de quem não precisava dele.
    """

    metricas_a = compute_retrieval_metrics(
        [a["avaliados"][i] for i in comuns], limiar=limiar
    )
    metricas_b = compute_retrieval_metrics(
        [b["avaliados"][i] for i in comuns], limiar=limiar
    )

    ima_a = metricas_a.get("top1_concentration") or {}
    ima_b = metricas_b.get("top1_concentration") or {}

    por_natureza = {}

    for natureza in ("caso leve", "sem cobertura"):
        linhas = []

        for caso_id in comuns:
            avaliado_b = b["avaliados"][caso_id]

            if avaliado_b["natureza"] != natureza:
                continue

            nota_a = a["avaliados"][caso_id]["max_score"]
            nota_b = avaliado_b["max_score"]

            linhas.append(
                {
                    "id": caso_id,
                    "antes": nota_a,
                    "depois": nota_b,
                    "cruzou_o_corte": (
                        nota_b is not None
                        and nota_b >= limiar
                        and not (nota_a is not None and nota_a >= limiar)
                    ),
                    "acima_do_corte": nota_b is not None and nota_b >= limiar,
                    "top1_depois": avaliado_b["top1"],
                }
            )

        por_natureza[natureza] = linhas

    return {
        "ima": {
            "antes": {"topic": ima_a.get("topic"), "share": ima_a.get("share")},
            "depois": {"topic": ima_b.get("topic"), "share": ima_b.get("share")},
            "delta": _delta(ima_a.get("share"), ima_b.get("share")),
        },
        "acima_do_corte": [
            metricas_a.get("share_cases_above_threshold"),
            metricas_b.get("share_cases_above_threshold"),
        ],
        "leves": por_natureza["caso leve"],
        "sem_cobertura": por_natureza["sem cobertura"],
        "leves_acima_do_corte": sum(
            1 for linha in por_natureza["caso leve"] if linha["acima_do_corte"]
        ),
    }


def _topicos_vistos(rodada: dict, comuns: list[str]) -> set[str]:
    """Assuntos que a busca devolveu em algum caso — o que é encontrável."""

    return {
        topico
        for caso_id in comuns
        for topico in rodada["avaliados"][caso_id]["topics"]
        if topico
    }


def comparar_cobertura(
    a: dict,
    b: dict,
    comuns: list[str],
    mapa: list[dict],
    fichas: list[dict],
) -> dict:
    """
    Quais quadros do mapa têm documento, e quais são **encontráveis**.

    A distinção é o critério "cobertura real" da porta de decisão. Um
    documento indexado que nunca aparece no top-5 do caso que o espera é
    cobertura no papel: ele entrou na base e não muda a resposta de ninguém.

    Não se mede pela coluna `cobertura` do mapa, que é estado de curadoria —
    hoje ela diz `indexada` em uma linha, enquanto a base tem oito documentos.
    """

    indexados = {}
    especies_originais = {}

    for ficha in fichas:
        topico = (ficha.get("topic") or "").strip()

        if not topico or topico == "not_informed":
            continue

        indexados[topico] = normalizar_especie(ficha.get("species", ""))
        especies_originais[topico] = ficha.get("species", "")

    vistos_a = _topicos_vistos(a, comuns)
    vistos_b = _topicos_vistos(b, comuns)

    def estado(topico: str, vistos: set[str]) -> str:
        if topico in vistos:
            return "encontravel"
        if topico in indexados:
            return "indexado, nao encontrado"
        return "sem documento"

    linhas = []

    for linha_mapa in mapa:
        topico = linha_mapa["id"]
        antes, depois = estado(topico, vistos_a), estado(topico, vistos_b)

        linhas.append(
            {
                "id": topico,
                "quadro": linha_mapa.get("quadro", ""),
                "especie_mapa": linha_mapa.get("especie", ""),
                "especie_ficha": indexados.get(topico, ""),
                "prioridade": linha_mapa.get("prioridade", ""),
                "etapa": linha_mapa.get("etapa", ""),
                "antes": antes,
                "depois": depois,
                "mudou": antes != depois,
            }
        )

    # Um documento é "novo" quando o assunto dele só aparece na base de B.
    # É sobre esses que a porta pergunta se são encontráveis.
    novos = sorted(vistos_b - vistos_a)
    novos_no_mapa = [t for t in novos if any(l["id"] == t for l in mapa)]

    # Espécie divergente entre a ficha e o mapa: não é erro, mas é o que o
    # caso b15 da régua ensinou a olhar (protocolo de gato, caso de cão).
    divergencias = [
        {
            "id": linha["id"],
            "mapa": linha["especie_mapa"],
            "ficha": linha["especie_ficha"],
        }
        for linha in linhas
        if linha["especie_ficha"]
        and linha["especie_mapa"]
        and linha["especie_ficha"] != linha["especie_mapa"]
        and linha["especie_mapa"] != "ambos"
    ]

    def cobertos(chave: str) -> int:
        return sum(1 for linha in linhas if linha[chave] == "encontravel")

    return {
        "linhas": linhas,
        "encontraveis": [cobertos("antes"), cobertos("depois")],
        "encontraveis_etapa_1": [
            sum(
                1
                for linha in linhas
                if linha["etapa"] == "1" and linha[chave] == "encontravel"
            )
            for chave in ("antes", "depois")
        ],
        "total_mapa": len(linhas),
        "total_etapa_1": sum(1 for linha in linhas if linha["etapa"] == "1"),
        "topicos_novos": novos_no_mapa,
        "fora_do_mapa": sorted(set(indexados) - {l["id"] for l in mapa}),
        "especies_divergentes": divergencias,
        "especies_normalizadas": sorted(
            {
                f"{valor} → {normalizar_especie(valor)}"
                for valor in especies_originais.values()
                if valor and normalizar_especie(valor) != valor
            }
        ),
    }


def gabarito_a_atualizar(
    a: dict,
    b: dict,
    comuns: list[str],
    mapa: list[dict],
) -> list[dict]:
    """
    Casos "sem cobertura" cujo assunto passou a existir na base.

    O critério é **assunto novo**, não "apareceu algo do mapa" — e a
    diferença não é sutil. A busca sempre devolve cinco trechos, e num caso
    sem cobertura eles são todos do assunto errado: o b12 (torção gástrica)
    recebe `trauma_and_bleeding` em primeiro lugar desde a rodada 11, que é
    o protocolo-ímã do B-02, não cobertura. Perguntar "apareceu algo do
    mapa?" marcaria os quatro casos sem cobertura em toda comparação, para
    sempre, e o bloco viraria ruído que ninguém lê.

    O que muda o gabarito é um assunto que **não existia na rodada A** passar
    a ser recuperado neste caso. Aí alguém precisa decidir se aquele
    documento novo cobre este quadro — e a decisão é de quem cuida da régua,
    com a especialista. O compare **avisa e não edita**: mudar `cases.csv`
    quebra a comparabilidade das rodadas anteriores.
    """

    ids_do_mapa = {linha["id"] for linha in mapa}
    vistos_em_a = _topicos_vistos(a, comuns)

    pendentes = []

    for caso_id in comuns:
        avaliado = b["avaliados"][caso_id]

        if avaliado["natureza"] != "sem cobertura":
            continue

        novos_neste_caso = [
            topico
            for topico in avaliado["topics"]
            if topico and topico in ids_do_mapa and topico not in vistos_em_a
        ]

        if novos_neste_caso:
            pendentes.append(
                {
                    "id": caso_id,
                    "apareceu": novos_neste_caso[0],
                    "posicao": avaliado["topics"].index(novos_neste_caso[0]) + 1,
                    "acima_do_corte": (
                        avaliado["max_score"] is not None
                        and avaliado["max_score"]
                        >= b["manifesto"].get("limiar", 0.70)
                    ),
                }
            )

    return pendentes


def porta_de_decisao(ordenacao: dict, ruido: dict, cobertura: dict) -> list[dict]:
    """
    Os quatro critérios da porta que saem deste arquivo.

    Estão em `data/curadoria/README.md`. Cinco dos seis apontam para cá; os
    outros dois (velocidade e classificação) vêm do mapa e do runner, e o
    relatório diz isso em vez de deixar a lacuna sem explicação.
    """

    criterios = []

    criterios.append(
        {
            "eixo": "Ordenação",
            "pergunta": "Adicionar documento piorou onde?",
            "valor": f"{ordenacao['pioraram']} pioraram, "
                     f"{ordenacao['melhoraram']} melhoraram",
            "limite": "pioraram ≤ melhoraram",
            "aprova": ordenacao["pioraram"] <= ordenacao["melhoraram"],
        }
    )

    share = (ruido["ima"]["depois"] or {}).get("share")

    criterios.append(
        {
            "eixo": "Ímã",
            "pergunta": "Um documento ainda atrai tudo?",
            "valor": (
                "—"
                if share is None
                else f"{ruido['ima']['depois']['topic']} em {share:.0%} dos casos"
            ),
            "limite": "nenhum documento em 1º em mais de 1/3",
            "aprova": share is not None and share <= LIMITE_IMA,
        }
    )

    criterios.append(
        {
            "eixo": "Ruído nos leves",
            "pergunta": "A base nova empurra caso leve para dentro do prompt?",
            "valor": f"{ruido['leves_acima_do_corte']} caso(s) leve(s) "
                     "acima do corte",
            "limite": "nenhum",
            "aprova": ruido["leves_acima_do_corte"] == 0,
        }
    )

    novos = cobertura["topicos_novos"]
    encontraveis_novos = [
        linha
        for linha in cobertura["linhas"]
        if linha["id"] in novos and linha["depois"] == "encontravel"
    ]
    fracao = len(encontraveis_novos) / len(novos) if novos else None

    criterios.append(
        {
            "eixo": "Cobertura real",
            "pergunta": "O documento indexado é encontrável?",
            "valor": (
                "nenhum assunto novo nesta comparação"
                if fracao is None
                else f"{len(encontraveis_novos)} de {len(novos)} "
                     f"({fracao:.0%})"
            ),
            "limite": "≥ 70% dos quadros novos",
            "aprova": fracao is None or fracao >= MINIMO_COBERTURA_REAL,
        }
    )

    return criterios


def compute_compare(
    a: dict,
    b: dict,
    mapa: list[dict],
    fichas: list[dict],
) -> dict[str, Any]:
    """Junta os quatro blocos e a porta. É o conteúdo do `compare.json`."""

    pareamento = parear(a, b)
    comuns = pareamento["comuns"]
    limiar = pareamento["limiar"]

    ordenacao = comparar_ordenacao(a, b, comuns)
    ruido = comparar_ruido(a, b, comuns, limiar)
    cobertura = comparar_cobertura(a, b, comuns, mapa, fichas)

    return {
        "a": {
            "run_id": a["run_id"],
            "quando": a["manifesto"].get("started_at"),
            "commit": (a["manifesto"].get("git") or {}).get("sha"),
        },
        "b": {
            "run_id": b["run_id"],
            "quando": b["manifesto"].get("started_at"),
            "commit": (b["manifesto"].get("git") or {}).get("sha"),
        },
        "limiar": limiar,
        "pareamento": pareamento,
        "base": comparar_base(a, b),
        "cobertura": cobertura,
        "ordenacao": ordenacao,
        "ruido": ruido,
        "gabarito_a_atualizar": gabarito_a_atualizar(a, b, comuns, mapa),
        "porta": porta_de_decisao(ordenacao, ruido, cobertura),
    }
