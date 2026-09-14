"""
O relatório que o `compare` da régua produz.

Separado do cálculo de propósito: `retrieval_compare.py` decide os números e
este arquivo decide como eles são lidos. É o mesmo corte que existe entre
`retrieval_metrics.py` e o `escrever_relatorio` do runner.

O `compare.md` é artefato **em disco**, e isso é uma decisão, não um detalhe:
o roteiro do agente de ingestão diz que "número citado aponta para o arquivo,
não para a conversa". O compare da régua de classificação só imprime no
terminal, e por isso nada do que ele calcula pode ser citado numa evidência
sem alguém recontar à mão.
"""

from typing import Optional

from retrieval_compare import _delta


def formatar(valor, casas: int = 3) -> str:
    """O mesmo travessão que o `report.md` da régua usa para ausência."""

    if valor is None:
        return "—"

    if isinstance(valor, float):
        return f"{valor:.{casas}f}"

    return str(valor)


def _sinal(valor: Optional[float], casas: int = 4) -> str:
    """Delta com sinal explícito: `+0.0444` diz mais do que `0.0444`."""

    if valor is None:
        return "—"

    return f"{valor:+.{casas}f}"


def _cabecalho(resultado: dict) -> list[str]:

    base = resultado["base"]
    pareamento = resultado["pareamento"]

    linhas = [
        f"# Comparação da régua — {resultado['b']['run_id']}",
        "",
        f"**Antes (A):** `{resultado['a']['run_id']}` · "
        f"{resultado['a']['quando']} · commit `{resultado['a']['commit']}`",
        "",
        f"**Depois (B):** `{resultado['b']['run_id']}` · "
        f"{resultado['b']['quando']} · commit `{resultado['b']['commit']}`",
        "",
        f"Corte de relevância: {resultado['limiar']} · "
        f"{len(pareamento['comuns'])} casos em comum",
        "",
        "## O que mudou na base",
        "",
        "| | Antes | Depois |",
        "|---|---|---|",
        f"| Trechos indexados | {formatar(base['chunk_count'][0])} | "
        f"{formatar(base['chunk_count'][1])} |",
        f"| Recorte (`chunk_ids_sha256`) | "
        f"`{(base['chunk_ids_sha256'][0] or '—')[:12]}` | "
        f"`{(base['chunk_ids_sha256'][1] or '—')[:12]}` |",
        f"| Conteúdo (`content_sha256`) | "
        f"`{(base['content_sha256'][0] or '—')[:12]}` | "
        f"`{(base['content_sha256'][1] or '—')[:12]}` |",
    ]

    if base["mesma_base"]:
        linhas += [
            "",
            "> **Nenhum documento entrou entre as duas rodadas.** O recorte da "
            "base é o mesmo, então esta comparação mede o **instrumento**, "
            "não uma mudança de curadoria: tudo abaixo deve dar zero. A régua "
            "é determinística, e qualquer diferença aqui seria defeito do "
            "compare ou da rodada.",
        ]

    for aviso in base["avisos"]:
        linhas += ["", f"> **Atenção:** {aviso}"]

    if pareamento["so_em_b"] or pareamento["so_em_a"]:
        linhas += ["", "### Casos que não entram na comparação", ""]

        if pareamento["so_em_b"]:
            linhas.append(
                "- **Novos em B** (sem antes): "
                f"{', '.join(pareamento['so_em_b'])}. Entram na próxima "
                "comparação, quando já tiverem um antes."
            )

        if pareamento["so_em_a"]:
            linhas.append(
                "- **Só em A** (saíram do conjunto): "
                f"{', '.join(pareamento['so_em_a'])}."
            )

    return linhas


def _bloco_cobertura(cobertura: dict) -> list[str]:

    linhas = [
        "",
        "## 1. Cobertura — quais quadros têm documento encontrável",
        "",
        "**Encontrável** quer dizer que o assunto apareceu entre os cinco "
        "trechos de um caso que realmente o espera e que a fonte cobre a "
        "espécie exigida. Aparecer por acaso em outro caso é ruído, não "
        "cobertura.",
        "",
        "| | Antes | Depois |",
        "|---|---|---|",
        f"| Quadros encontráveis (de {cobertura['total_mapa']}) | "
        f"{cobertura['encontraveis'][0]} | {cobertura['encontraveis'][1]} |",
        f"| Na etapa 1 (de {cobertura['total_etapa_1']}) | "
        f"{cobertura['encontraveis_etapa_1'][0]} | "
        f"{cobertura['encontraveis_etapa_1'][1]} |",
    ]

    mudaram = [linha for linha in cobertura["linhas"] if linha["mudou"]]

    if mudaram:
        linhas += [
            "",
            "| Quadro | Espécie | Prio. | Antes | Depois |",
            "|---|---|---|---|---|",
        ]
        for linha in mudaram:
            linhas.append(
                f"| {linha['quadro'] or linha['id']} | "
                f"{linha['especie_mapa']} | {linha['prioridade']} | "
                f"{linha['antes']} | **{linha['depois']}** |"
            )
    else:
        linhas += ["", "Nenhum quadro mudou de estado."]

    if cobertura["especies_divergentes"]:
        linhas += [
            "",
            "> **Espécie divergente entre a ficha e o mapa** — é o que o caso "
            "b15 da régua ensinou a olhar (protocolo de gato, caso de cão):",
            "",
        ]
        for divergencia in cobertura["especies_divergentes"]:
            linhas.append(
                f"> - `{divergencia['id']}`: o mapa diz *{divergencia['mapa']}*, "
                f"a ficha diz *{divergencia['ficha']}*"
            )

    if cobertura["fora_do_mapa"]:
        linhas += [
            "",
            "> **Documentos sem linha no mapa:** "
            f"{', '.join(cobertura['fora_do_mapa'])}. Assunto indexado que "
            "ninguém decidiu cobrir.",
        ]

    return linhas


def _bloco_ordenacao(ordenacao: dict) -> list[str]:

    linhas = [
        "",
        "## 2. Ordenação — onde cada caso foi parar",
        "",
        "| Métrica | Antes | Depois | Δ |",
        "|---|---|---|---|",
    ]

    for chave, rotulo in (
        ("precision_at_1", "Protocolo certo em 1º"),
        ("mrr", "Posição média invertida (MRR)"),
        ("recall_at_5", "Certo entre os cinco"),
    ):
        antes, depois = ordenacao["metricas"][chave]
        linhas.append(
            f"| {rotulo} | {formatar(antes)} | {formatar(depois)} | "
            f"{_sinal(ordenacao['deltas'][chave])} |"
        )

    linhas += [
        "",
        f"**{ordenacao['melhoraram']} melhoraram · "
        f"{ordenacao['pioraram']} pioraram · {ordenacao['iguais']} iguais**",
    ]

    mudou = [caso for caso in ordenacao["casos"] if caso["situacao"] != "igual"]

    if mudou:
        linhas += [
            "",
            "| Caso | Esperado | Antes | Depois | |",
            "|---|---|---|---|---|",
        ]
        for caso in mudou:
            linhas.append(
                f"| {caso['id']} | {', '.join(caso['esperado'])} | "
                f"{formatar(caso['antes'])} | {formatar(caso['depois'])} | "
                f"**{caso['situacao']}** |"
            )
    else:
        linhas += ["", "Nenhum caso mudou de posição."]

    return linhas


def _bloco_ruido(ruido: dict) -> list[str]:

    ima = ruido["ima"]

    linhas = [
        "",
        "## 3. Ruído — o que a base nova empurrou para dentro",
        "",
        "| | Antes | Depois | Δ |",
        "|---|---|---|---|",
        f"| Protocolo-ímã | {ima['antes']['topic'] or '—'} "
        f"({formatar(ima['antes']['share'])}) | "
        f"{ima['depois']['topic'] or '—'} "
        f"({formatar(ima['depois']['share'])}) | {_sinal(ima['delta'])} |",
        f"| Casos acima do corte | {formatar(ruido['acima_do_corte'][0])} | "
        f"{formatar(ruido['acima_do_corte'][1])} | "
        f"{_sinal(_delta(*ruido['acima_do_corte']))} |",
    ]

    for chave, rotulo in (
        ("leves", "Casos leves"),
        ("sem_cobertura", "Casos sem cobertura na base"),
    ):
        if not ruido[chave]:
            continue

        linhas += [
            "",
            f"### {rotulo} — a nota máxima subiu?",
            "",
            "| Caso | Antes | Depois | 1º lugar agora | |",
            "|---|---|---|---|---|",
        ]

        for linha in ruido[chave]:
            marca = "**cruzou o corte**" if linha["cruzou_o_corte"] else ""
            linhas.append(
                f"| {linha['id']} | {formatar(linha['antes'])} | "
                f"{formatar(linha['depois'])} | "
                f"{linha['top1_depois'] or '—'} | {marca} |"
            )

    if ruido["leves_acima_do_corte"] == 0 and ruido["acima_do_corte"][1] == 0.0:
        linhas += [
            "",
            "> **Nenhum caso leve recebeu trecho acima do corte — mas nenhum "
            "caso recebeu.** Enquanto a busca não passar do corte em caso "
            "nenhum, este silêncio é acidente, não discernimento. É a mesma "
            "ressalva que o `report.md` da régua emite sozinho.",
        ]

    return linhas


def _bloco_gabarito(pendentes: list[dict]) -> list[str]:

    linhas = ["", "## 4. Gabarito a atualizar", ""]

    if not pendentes:
        linhas.append("Nenhum caso precisa de revisão de gabarito.")
        return linhas

    linhas += [
        "Estes casos estão marcados **sem cobertura**, e agora a busca "
        "devolve neles um assunto que **não existia na base antes**. Alguém "
        "precisa decidir se o documento novo cobre o quadro — o compare "
        "**avisa e não edita**, porque mudar `cases.csv` quebra a "
        "comparabilidade das rodadas anteriores.",
        "",
        "| Caso | Assunto novo | Posição | Acima do corte |",
        "|---|---|---|---|",
    ]

    for pendente in pendentes:
        linhas.append(
            f"| {pendente['id']} | `{pendente['apareceu']}` | "
            f"{pendente['posicao']} | "
            f"{'sim' if pendente['acima_do_corte'] else 'não'} |"
        )

    return linhas


def _bloco_porta(resultado: dict) -> list[str]:

    linhas = [
        "",
        "## 5. A porta de decisão",
        "",
        "Os critérios de `data/curadoria/README.md` que saem deste arquivo:",
        "",
        "| Eixo | Valor | Limite | |",
        "|---|---|---|---|",
    ]

    for criterio in resultado["porta"]:
        linhas.append(
            f"| {criterio['eixo']} | {criterio['valor']} | "
            f"{criterio['limite']} | "
            f"{'passa' if criterio['aprova'] else '**não passa**'} |"
        )

    linhas += [
        "",
        "Os outros dois critérios não vêm daqui: **velocidade** sai da coluna "
        "`cobertura` do mapa de assuntos, e **classificação** sai de uma "
        "rodada do runner de `data/evaluation/`.",
    ]

    return linhas


def _rodape(resultado: dict) -> list[str]:

    ordenacao = resultado["ordenacao"]
    cobertura = resultado["cobertura"]
    n_casos = max(1, len(ordenacao["casos"]))

    linhas = [
        "",
        "---",
        "",
        "### Como ler este arquivo",
        "",
        "- **A régua é determinística.** Duas rodadas sobre a mesma base "
        "devolvem posições e notas idênticas, então aqui diferença é sinal — "
        "não ruído de sessão, ao contrário do runner de classificação.",
        f"- **Um caso vale {1 / n_casos:.3f} da Precision@1.** Com poucos "
        "casos com protocolo, uma linha move muito: leia a tabela pareada "
        "antes da média.",
        "- **A comparação é sobre os casos em comum**, não sobre o arquivo "
        "inteiro. Cada lote de fontes traz relatos novos, e travar por hash "
        "do `cases.csv` abortaria sempre; o que aborta é um caso em comum ter "
        "mudado de texto ou de gabarito.",
        "- **Inventário e espécie vêm do fingerprint de cada rodada.** "
        "Artefatos históricos sem esses campos usam apenas tópicos observados "
        "e não recebem cobertura de espécie inventada.",
    ]

    if cobertura["especies_normalizadas"]:
        linhas.append(
            "- **Espécies normalizadas** (as fichas usam mais de uma grafia, "
            "B-53): " + "; ".join(cobertura["especies_normalizadas"]) + "."
        )

    return linhas


def escrever_compare_md(resultado: dict) -> str:
    """Monta o relatório inteiro, na ordem que o B-51 pediu."""

    linhas = [
        *_cabecalho(resultado),
        *_bloco_cobertura(resultado["cobertura"]),
        *_bloco_ordenacao(resultado["ordenacao"]),
        *_bloco_ruido(resultado["ruido"]),
        *_bloco_gabarito(resultado["gabarito_a_atualizar"]),
        *_bloco_porta(resultado),
        *_rodape(resultado),
    ]

    return "\n".join(linhas) + "\n"
