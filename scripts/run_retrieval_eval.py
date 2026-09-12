"""
Régua de recuperação: mede se a busca traz o protocolo certo.

Irmão de `run_evaluation.py`, para um pedaço diferente do sistema. O runner
de classificação mede o caminho inteiro, do relato até "emergência ou não";
este mede só a busca, e a nota não é acurácia — é **posição**.

Fala com `POST /search/`, que é busca pura: não passa pela etapa de consulta
(sem reescrita, sem multi-query, sem HyDE) e não aplica o corte de
relevância. As duas coisas são de propósito: a rodada precisa ser
determinística, e precisa enxergar o que ficou **abaixo** do corte para
poder dizer que o protocolo certo estava lá embaixo.

    python scripts/run_retrieval_eval.py --name linha_de_base \\
        --expect-base-hash eeba9f51...

Escrito pelo trilho B2 em nome do trilho A, a quem a régua pertence. O
gabarito em `data/retrieval/cases.csv` é **provisório** até o trilho A
validar (evidencias/joao/2026-09-12-11-regua-de-recuperacao.md).
"""

import argparse
import csv
import json
import platform
import socket
import sys
from datetime import datetime
from pathlib import Path

import requests

# O runner de classificação já resolveu escrita atômica, fingerprint,
# estado do Git e conferência da base. Reaproveitar evita duas versões da
# mesma coisa divergindo com o tempo.
from run_evaluation import (
    ApiClient,
    agora,
    conferir_base,
    escrever_atomico,
    git_estado,
    sha256_arquivo,
)
from retrieval_compare import carregar_rodada, compute_compare
from retrieval_compare_report import escrever_compare_md
from retrieval_metrics import avaliar_caso, compute_retrieval_metrics

RAIZ = Path(__file__).resolve().parents[1]
CASOS = RAIZ / "data" / "retrieval" / "cases.csv"
DIRETORIO_RODADAS = RAIZ / "data" / "retrieval" / "runs"
MAPA = RAIZ / "data" / "curadoria" / "mapa-de-assuntos.csv"
DOCUMENTOS = RAIZ / "backend" / "data" / "documents"

LIMIAR_PADRAO = 0.70


def carregar_casos() -> list[dict]:

    if not CASOS.exists():
        raise SystemExit(f"Conjunto de casos não encontrado: {CASOS}")

    with open(CASOS, encoding="utf-8", newline="") as arquivo:
        casos = list(csv.DictReader(arquivo))

    if not casos:
        raise SystemExit("O conjunto de casos está vazio.")

    return casos


def buscar(base_url: str, texto: str, timeout: int) -> list[dict]:

    resposta = requests.post(
        f"{base_url.rstrip('/')}/search/",
        json={"question": texto},
        timeout=(5, timeout),
    )
    resposta.raise_for_status()

    return resposta.json()["documents"]


def escrever_relatorio(
    diretorio: Path,
    manifesto: dict,
    metricas: dict,
    avaliados: list[dict],
) -> None:

    def n(valor, casas=3):
        return "—" if valor is None else f"{valor:.{casas}f}"

    linhas = [
        f"# Régua de recuperação — {manifesto['run_id']}",
        "",
        f"**Quando:** {manifesto['started_at']} · "
        f"**commit:** `{(manifesto.get('git') or {}).get('sha')}`",
        "",
        "Mede se a busca traz o protocolo certo, por **posição**. Não mede "
        "classificação — para isso é o runner de `data/evaluation/`.",
        "",
        "## Resultado",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| **Protocolo certo em 1º** (Precision@1) | "
        f"{n(metricas['precision_at_1'])} "
        f"({metricas['n_com_protocolo']} casos com protocolo na base) |",
        f"| Posição média invertida (MRR) | {n(metricas['mrr'])} |",
        f"| Protocolo certo entre os 5 (Recall@5) | "
        f"{n(metricas.get('recall_at_5'))} |",
        f"| Casos com algum trecho acima de {metricas['limiar']:.2f} | "
        f"{n(metricas['share_cases_above_threshold'])} |",
        f"| Nota máxima média | {n(metricas.get('mean_max_score'), 4)} |",
        "",
        "### Quando a resposta certa é não trazer nada",
        "",
        "| Natureza | Casos | Busca ficou quieta |",
        "|---|---|---|",
        f"| Caso leve | {metricas['n_caso_leve']} | "
        f"{n(metricas['silence_rate_on_mild'])} |",
        f"| Sem cobertura na base | {metricas['n_sem_cobertura']} | "
        f"{n(metricas['silence_rate_on_uncovered'])} |",
    ]

    base = metricas.get("baselines") or {}

    if base:
        linhas += [
            "",
            "### O número é bom? Comparado com o quê",
            "",
            "| Estratégia | Protocolo certo em 1º |",
            "|---|---|",
            f"| Escolher um documento ao acaso | "
            f"{n(base.get('documento_ao_acaso'))} |",
        ]

        if base.get("sempre_o_mesmo_documento") is not None:
            linhas.append(
                f"| Responder sempre o mesmo documento | "
                f"{n(base['sempre_o_mesmo_documento'])} |"
            )

        linhas.append(
            f"| **A busca** | **{n(metricas['precision_at_1'])}** |"
        )

        distintos = base.get("documentos_distintos_por_caso")
        vistos = metricas.get("n_documentos_vistos")

        if distintos and vistos:
            linhas += [
                "",
                f"> **Cuidado ao ler o Recall.** A busca mostra em média "
                f"{distintos:.1f} documentos distintos por caso, e a base "
                f"tem {vistos} documentos no total. Com um acervo pequeno, "
                "\"o certo está entre os primeiros\" é quase geométrico — a "
                "métrica só passa a informar quando a base crescer.",
            ]

    # A ressalva que impede ler silêncio como mérito.
    if metricas["share_cases_above_threshold"] == 0.0:
        linhas += [
            "",
            "> **Atenção: a busca não passou do corte em nenhum caso.** O "
            "silêncio acima não é mérito — ela está sempre quieta, e "
            "\"acerta\" os casos leves por acidente. Enquanto este número "
            "for zero, as taxas de silêncio não medem discernimento.",
        ]

    concentracao = metricas.get("top1_concentration")

    if concentracao and (concentracao.get("share") or 0) >= 0.25:
        linhas += [
            "",
            "### Concentração no primeiro lugar",
            "",
            f"O protocolo **{concentracao['topic']}** aparece em 1º lugar em "
            f"**{concentracao['cases']} de {metricas['n_casos']}** casos "
            f"({n(concentracao['share'])}). Um documento que atrai consultas "
            "de assuntos que não são dele é o mecanismo do "
            "[B-02](../../evidencias/backlog.md#b-02).",
            "",
            "| Protocolo em 1º | Casos |",
            "|---|---|",
        ]
        for topico, vezes in concentracao["distribution"].items():
            linhas.append(f"| {topico} | {vezes} |")

    linhas += ["", "## Caso a caso", "",
               "| Caso | Natureza | Esperado | 1º lugar | Posição | Nota máx. |",
               "|---|---|---|---|---|---|"]

    for c in avaliados:
        esperado = ", ".join(c["expected_topics"]) or "—"
        posicao = c.get("posicao")
        linhas.append(
            f"| {c['id']} | {c['natureza']} | {esperado} | "
            f"{c['top1'] or '—'} | {posicao or '—'} | "
            f"{n(c['max_score'], 3)} |"
        )

    linhas += [
        "",
        "---",
        "",
        "Gabarito marcado pelo trilho B2, **provisório**, aguardando "
        "validação do trilho A. Ver "
        "`data/retrieval/README.md`.",
        "",
    ]

    escrever_atomico(diretorio / "report.md", "\n".join(linhas))


def comando_compare(dir_a: Path, dir_b: Path) -> None:
    """
    Diz o que mudou entre duas rodadas, e grava o resultado ao lado de B.

    O arquivo fica na pasta da rodada **depois**, porque é ela que mudou, e
    leva o `run_id` de A no nome: uma mesma rodada pode ser comparada com
    mais de um antes, e sobrescrever silenciosamente seria perder medição.
    """

    a = carregar_rodada(dir_a)
    b = carregar_rodada(dir_b)

    with open(MAPA, encoding="utf-8", newline="") as arquivo:
        mapa = list(csv.DictReader(arquivo))

    fichas = [
        json.loads(caminho.read_text(encoding="utf-8"))
        for caminho in sorted(DOCUMENTOS.glob("*.json"))
    ]

    resultado = compute_compare(a, b, mapa, fichas)

    nome = f"compare__vs_{a['run_id']}"

    escrever_atomico(dir_b / f"{nome}.md", escrever_compare_md(resultado))
    escrever_atomico(
        dir_b / f"{nome}.json",
        json.dumps(resultado, ensure_ascii=False, indent=2, default=str),
    )

    print(f"A = {a['run_id']}")
    print(f"B = {b['run_id']}\n")

    if resultado["base"]["mesma_base"]:
        print(
            "  A base é a mesma nas duas rodadas: nada foi indexado entre "
            "elas, e tudo abaixo deve dar zero.\n"
        )

    ordenacao = resultado["ordenacao"]
    print(
        f"  ordenação : {ordenacao['melhoraram']} melhoraram, "
        f"{ordenacao['pioraram']} pioraram, {ordenacao['iguais']} iguais"
    )
    print(
        f"  cobertura : {resultado['cobertura']['encontraveis'][0]} -> "
        f"{resultado['cobertura']['encontraveis'][1]} quadros encontráveis"
    )

    if resultado["gabarito_a_atualizar"]:
        print(
            f"  gabarito  : {len(resultado['gabarito_a_atualizar'])} caso(s) "
            "precisam de revisão"
        )

    print("\n  porta de decisão:")
    for criterio in resultado["porta"]:
        marca = "passa" if criterio["aprova"] else "NÃO PASSA"
        print(f"    {criterio['eixo']:<16} {marca:<10} {criterio['valor']}")

    print(f"\n  {_curto(dir_b / f'{nome}.md')}")


def _curto(caminho: Path) -> str:

    try:
        return str(caminho.relative_to(RAIZ))
    except ValueError:
        return str(caminho)


def main(argv=None) -> None:

    argv = sys.argv[1:] if argv is None else list(argv)

    # Subcomando só quando é pedido: o comando documentado da régua é
    # `run_retrieval_eval.py --name … --expect-base-hash …`, e ele está em
    # README, em evidência e no roteiro do pesquisador. Quebrar isso para
    # acrescentar o compare trocaria um instrumento em uso por um mais
    # arrumado.
    if argv and argv[0] == "compare":
        parser = argparse.ArgumentParser(
            prog="run_retrieval_eval.py compare",
            description="Compara duas rodadas da régua: o que mudou.",
        )
        parser.add_argument("run_a", type=Path, help="a rodada de antes")
        parser.add_argument("run_b", type=Path, help="a rodada de depois")

        argumentos = parser.parse_args(argv[1:])
        comando_compare(argumentos.run_a, argumentos.run_b)
        return

    parser = argparse.ArgumentParser(
        description="Mede se a busca traz o protocolo certo. "
                    "Use `compare A B` para comparar duas rodadas."
    )
    parser.add_argument("--name", default="rodada")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--limiar",
        type=float,
        default=LIMIAR_PADRAO,
        help=(
            "Nota mínima para considerar que a busca trouxe algo relevante. "
            "Padrão 0,70, o mesmo que o classificador aplica — e igualmente "
            "provisório: é esta régua que deve dizer o valor certo."
        ),
    )
    parser.add_argument(
        "--expect-base-hash",
        help=(
            "Aborta se a base vetorial não for esta. Use em toda rodada que "
            "for citada numa evidência."
        ),
    )

    argumentos = parser.parse_args(argv)

    cliente = ApiClient(argumentos.api_url, argumentos.timeout)

    if not cliente.health():
        raise SystemExit(
            f"A API não respondeu em {argumentos.api_url}. "
            "Suba com: docker compose up -d"
        )

    impressao = cliente.fingerprint()

    # A busca é o objeto da medição: base errada ou vazia invalida tudo.
    conferir_base(impressao, hash_esperado=argumentos.expect_base_hash)
    conferir_base(impressao, config_efetivo={"retrieval_enabled": True})

    casos = carregar_casos()

    carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
    diretorio = DIRETORIO_RODADAS / f"{carimbo}_{argumentos.name}"
    diretorio.mkdir(parents=True, exist_ok=True)

    manifesto = {
        "run_id": diretorio.name,
        "name": argumentos.name,
        "started_at": agora(),
        "hostname": socket.gethostname(),
        "python": platform.python_version(),
        "git": git_estado(),
        "cases": {
            "path": str(CASOS.relative_to(RAIZ)),
            "sha256": sha256_arquivo(CASOS),
            "n": len(casos),
        },
        "limiar": argumentos.limiar,
        "api_url": argumentos.api_url,
        "expected_base_hash": argumentos.expect_base_hash,
        "backend_fingerprint": impressao,
    }

    print(f"Rodada {diretorio.name}")
    print(f"  casos: {len(casos)} | limiar: {argumentos.limiar}\n")

    resultados = []
    avaliados = []

    for numero, caso in enumerate(casos, start=1):
        documentos = buscar(argumentos.api_url, caso["text"], argumentos.timeout)

        avaliado = avaliar_caso(caso, documentos)
        avaliados.append(avaliado)

        resultados.append(
            {
                "id": caso["id"],
                "text": caso["text"],
                "expected_topics": avaliado["expected_topics"],
                "expected_none_reason": caso.get("expected_none_reason", ""),
                "natureza": avaliado["natureza"],
                "posicao": avaliado.get("posicao"),
                "documents": documentos,
            }
        )

        marca = (
            "ok "
            if avaliado.get("acertou_top1")
            else ("—  " if not avaliado["expected_topics"] else "err")
        )
        print(
            f"  [{numero:2d}/{len(casos)}] {caso['id']} {marca} "
            f"1º: {avaliado['top1'] or '—'} "
            f"({avaliado['max_score']:.3f})"
            if avaliado["max_score"] is not None
            else f"  [{numero:2d}/{len(casos)}] {caso['id']} sem resultado"
        )

    metricas = compute_retrieval_metrics(avaliados, limiar=argumentos.limiar)

    escrever_atomico(
        diretorio / "results.jsonl",
        "\n".join(
            json.dumps(registro, ensure_ascii=False) for registro in resultados
        )
        + "\n",
    )
    escrever_atomico(
        diretorio / "metrics.json",
        json.dumps(metricas, ensure_ascii=False, indent=2, default=str),
    )

    manifesto["finished_at"] = agora()
    escrever_atomico(
        diretorio / "manifest.json",
        json.dumps(manifesto, ensure_ascii=False, indent=2, default=str),
    )

    escrever_relatorio(diretorio, manifesto, metricas, avaliados)

    print("\nConcluída.")
    print(f"  protocolo certo em 1º : {metricas['precision_at_1']}")
    print(f"  MRR                   : {metricas['mrr']}")
    print(
        f"  acima do limiar       : "
        f"{metricas['share_cases_above_threshold']}"
    )

    concentracao = metricas.get("top1_concentration")
    if concentracao:
        print(
            f"  1º lugar mais comum   : {concentracao['topic']} "
            f"({concentracao['cases']}/{metricas['n_casos']})"
        )

    print(f"\n  {diretorio}")


if __name__ == "__main__":
    main()
