"""
Relatórios e comparação entre rodadas de avaliação.

    report RUN   regera métricas e relatório a partir das previsões
    compare A B  compara duas rodadas nas linhas em comum
    cite RUN     promove uma rodada citada por uma evidência

Sobre a comparação: com 98 linhas, uma diferença só é detectável a partir de
uns 6 pontos percentuais. Este módulo imprime o teste, o intervalo de
confiança e essa ressalva juntos, para que uma variação de 2 pontos não
seja lida como melhoria.
"""

import argparse
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation_metrics import compute_metrics, wilson_ci


RAIZ = Path(__file__).resolve().parents[1]
DIRETORIO_CITADAS = RAIZ / "data" / "evaluation" / "cited"

# Número de reamostragens do bootstrap. 10 mil é suficiente para um
# intervalo estável e roda em menos de um segundo com 98 linhas.
REAMOSTRAGENS = 10_000


# ----------------------------------------------------------------------
# Estatística
# ----------------------------------------------------------------------


def mcnemar(b: int, c: int) -> dict:
    """
    Teste de McNemar exato para duas medições nas mesmas linhas.

    Só os desacordos informam: `b` são as linhas que a rodada A acertou e a
    B errou, `c` o contrário. Linhas em que as duas concordam não dizem
    nada sobre qual é melhor.

    Usa a binomial exata (sem scipy) porque com poucos desacordos a
    aproximação por chi-quadrado é ruim. Também devolve a variante mid-p,
    menos conservadora, recomendada para amostras pequenas.
    """

    n = b + c

    if n == 0:
        return {
            "b": 0,
            "c": 0,
            "p_exact": 1.0,
            "p_mid": 1.0,
            "note": "as duas rodadas fizeram previsões idênticas",
        }

    menor = min(b, c)

    # P(X <= menor) numa binomial(n, 0.5)
    acumulado = sum(math.comb(n, k) for k in range(menor + 1)) / 2**n
    ponto = math.comb(n, menor) / 2**n

    return {
        "b": b,
        "c": c,
        "p_exact": min(1.0, 2 * acumulado),
        "p_mid": min(1.0, 2 * (acumulado - 0.5 * ponto)),
    }


def bootstrap_diferenca(
    acertos_a: np.ndarray,
    acertos_b: np.ndarray,
    reamostragens: int = REAMOSTRAGENS,
    seed: int = 0,
) -> dict:
    """
    Intervalo de confiança da diferença de acurácia entre duas rodadas.

    Reamostra as linhas em pares: a mesma linha entra ou sai das duas
    medições ao mesmo tempo. Isso preserva o pareamento e dá um intervalo
    mais estreito que tratar as rodadas como independentes.
    """

    gerador = np.random.default_rng(seed)
    n = len(acertos_a)

    diferencas = []

    for _ in range(reamostragens):
        indices = gerador.integers(0, n, n)
        diferencas.append(
            acertos_a[indices].mean() - acertos_b[indices].mean()
        )

    return {
        "diff": float(acertos_a.mean() - acertos_b.mean()),
        "ci95": [
            round(float(np.percentile(diferencas, 2.5)), 4),
            round(float(np.percentile(diferencas, 97.5)), 4),
        ],
    }


# ----------------------------------------------------------------------
# Relatório
# ----------------------------------------------------------------------


def _formatar(valor, casas: int = 4) -> str:

    if valor is None:
        return "n/a"

    if isinstance(valor, float):
        return f"{valor:.{casas}f}"

    return str(valor)


def escrever_relatorio(
    diretorio: Path, manifesto: dict, metricas: dict
) -> None:

    c = metricas["classification"]
    b = metricas["baselines"]

    linhas = [
        f"# Rodada {manifesto['run_id']}",
        "",
        f"**Preset:** {manifesto.get('preset')} · "
        f"**Subconjunto:** {manifesto.get('subset')} · "
        f"**Linhas:** {metricas['rows_evaluated']} · "
        f"**Repetições:** {manifesto.get('repeats', 1)}",
        "",
        f"Início {manifesto.get('started_at')} · "
        f"máquina {manifesto.get('hostname')} · "
        f"commit {(manifesto.get('git') or {}).get('sha')}"
        f"{' (com alterações locais)' if (manifesto.get('git') or {}).get('dirty') else ''}",
        "",
        "## Configuração efetiva",
        "",
        "```json",
        json.dumps(
            manifesto.get("effective_config") or {},
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
        "## Resultado",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| **Acurácia balanceada** | **{_formatar(c['balanced_accuracy'])}** |",
        f"| Acurácia estrita | {_formatar(c['accuracy_strict'])} "
        f"IC95 {c['accuracy_strict_ci95']} |",
        f"| Cobertura | {_formatar(c['coverage'])} |",
        f"| Acurácia entre as decididas | {_formatar(c['accuracy_decided'])} |",
        f"| Macro-F1 | {_formatar(c['macro_f1'])} |",
        "",
        "### Erros clínicos",
        "",
        "| Erro | Contagem | Taxa |",
        "|---|---|---|",
        f"| Falsos não urgentes (emergência tratada como leve) | "
        f"{c['false_non_urgent']} | {_formatar(c['false_non_urgent_rate'], 3)} |",
        f"| Falsos urgentes (leve tratado como emergência) | "
        f"{c['false_urgent']} | {_formatar(c['false_urgent_rate'], 3)} |",
        f"| Abstenções (INCERTO) | — | {_formatar(c['incerto_rate'], 3)} |",
        f"| Saída inválida | — | {_formatar(c['invalid_rate'], 3)} |",
        "",
        "### Referências sem modelo",
        "",
        "Regras triviais sobre este conjunto. Se o sistema não as supera, o "
        "ganho medido não vem da compreensão do relato.",
        "",
        "| Referência | Acurácia |",
        "|---|---|",
        f"| Sempre responder emergência | {_formatar(b.get('always_emergencia'))} |",
        f"| Menos de 5 sintomas → não emergência | {_formatar(b.get('rule_few_symptoms'))} |",
        f"| Só sintomas leves → não emergência | {_formatar(b.get('rule_only_mild_symptoms'))} |",
        "",
        "### Por classe",
        "",
        "| Classe | Apoio | Precisão | Revocação | F1 |",
        "|---|---|---|---|---|",
    ]

    for classe, dados in c["per_class"].items():
        linhas.append(
            f"| {classe} | {dados['support']} | "
            f"{_formatar(dados['precision'])} | "
            f"{_formatar(dados['recall'])} | "
            f"{_formatar(dados['f1'])} |"
        )

    linhas += ["", "### Matriz de confusão", "", "| real ↓ / previsto → | " + " | ".join(
        c["confusion_matrix"]["EMERGENCIA"].keys()
    ) + " |", "|---" * 6 + "|"]

    for real, previstos in c["confusion_matrix"].items():
        linhas.append(
            f"| {real} | " + " | ".join(str(v) for v in previstos.values()) + " |"
        )

    if metricas.get("grounding"):
        g = metricas["grounding"]
        linhas += [
            "",
            "### Ancoragem nos documentos",
            "",
            "| Métrica | Valor |",
            "|---|---|",
            f"| Fontes citadas por resposta | {_formatar(g.get('mean_cited_sources'), 2)} |",
            f"| Respostas com ao menos uma citação | {_formatar(g.get('share_rows_with_citation'), 3)} |",
            f"| Linhas em que nada passou de 0,70 | {_formatar(g.get('share_rows_max_score_below_0_70'), 3)} |",
            f"| Score máximo médio | {_formatar(g.get('mean_max_score'))} |",
            f"| Respostas com citação inválida | {_formatar(g.get('share_rows_invalid_citation'), 3)} |",
        ]

    if metricas.get("repeats"):
        r = metricas["repeats"]
        linhas += [
            "",
            "### Estabilidade entre repetições",
            "",
            f"- Repetições: {r['n_repeats']}",
            f"- Linhas com resposta idêntica em todas: "
            f"{_formatar(r['exact_agreement_rate'], 3)}",
            f"- Linhas instáveis: {r['n_unstable_rows']}",
        ]

        if r.get("aggregate"):
            a = r["aggregate"]
            linhas.append(
                f"- Acurácia balanceada: média "
                f"{_formatar(a['balanced_accuracy_mean'])}, "
                f"desvio {_formatar(a['balanced_accuracy_sd'])}, "
                f"faixa {_formatar(a['balanced_accuracy_min'])}–"
                f"{_formatar(a['balanced_accuracy_max'])}"
            )

    latencia = metricas["latency"]

    linhas += ["", "### Tempo de resposta", "", "| Etapa | Média | Mediana | p95 |", "|---|---|---|---|"]

    for etapa in ("query_s", "retrieval_s", "generation_s", "total_s", "client_s"):
        if etapa in latencia:
            d = latencia[etapa]
            linhas.append(
                f"| {etapa} | {d['mean']} | {d['median']} | {d['p95']} |"
            )

    if latencia.get("rows_with_model_load"):
        linhas.append("")
        linhas.append(
            f"Excluídas {latencia['rows_with_model_load']} linha(s) que "
            "pagaram o carregamento do modelo."
        )

    if metricas["rows_with_error"]:
        linhas += [
            "",
            f"**Atenção:** {metricas['rows_with_error']} linha(s) "
            "falharam e ficaram fora das contas.",
        ]

    caminho = diretorio / "report.md"
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")


# ----------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------


def carregar(diretorio: Path):

    manifesto = json.loads(
        (diretorio / "manifest.json").read_text(encoding="utf-8")
    )

    registros = [
        json.loads(linha)
        for linha in (diretorio / "predictions.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if linha.strip()
    ]

    return manifesto, pd.DataFrame(registros)


def comando_report(diretorio: Path) -> None:

    manifesto, df = carregar(diretorio)
    metricas = compute_metrics(df)

    (diretorio / "metrics.json").write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
        newline="\n",
    )

    escrever_relatorio(diretorio, manifesto, metricas)

    print(f"Regerado: {diretorio / 'report.md'}")


def comando_compare(dir_a: Path, dir_b: Path, usar: str) -> None:

    manifesto_a, df_a = carregar(dir_a)
    manifesto_b, df_b = carregar(dir_b)

    print(f"A = {manifesto_a['run_id']}")
    print(f"B = {manifesto_b['run_id']}\n")

    # O diff de configuração vem primeiro de propósito: se mais de uma coisa
    # mudou entre as rodadas, o resultado não diz qual delas causou o quê.
    print("--- diferenças de configuração ---")

    config_a = manifesto_a.get("effective_config") or {}
    config_b = manifesto_b.get("effective_config") or {}

    diferencas = [
        (chave, config_a.get(chave), config_b.get(chave))
        for chave in sorted(set(config_a) | set(config_b))
        if config_a.get(chave) != config_b.get(chave)
    ]

    if diferencas:
        for chave, valor_a, valor_b in diferencas:
            print(f"  {chave}: {valor_a}  ->  {valor_b}")
        if len(diferencas) > 1:
            print(
                "\n  Atenção: mais de uma diferença. O resultado não "
                "identifica qual delas causou a mudança."
            )
    else:
        print("  nenhuma")

    if manifesto_a.get("relato_lang") != manifesto_b.get("relato_lang"):
        raise SystemExit(
            "\nAs rodadas usaram idiomas diferentes nos relatos. "
            "Comparar mediria a tradução, não a mudança testada."
        )

    if (
        manifesto_a["dataset"]["sha256"]
        != manifesto_b["dataset"]["sha256"]
    ):
        raise SystemExit(
            "\nAs rodadas usaram versões diferentes do dataset."
        )

    impressao_a = (manifesto_a.get("backend_fingerprint") or {})
    impressao_b = (manifesto_b.get("backend_fingerprint") or {})

    for parte in ("model", "vector_store", "prompts"):
        if impressao_a.get(parte) != impressao_b.get(parte):
            print(
                f"\n  Aviso: '{parte}' difere entre as rodadas — "
                "o sistema não era o mesmo."
            )

    # Só a primeira execução de cada rodada entra na comparação: usar todas
    # as repetições trataria a mesma linha como observações independentes e
    # estreitaria o intervalo artificialmente.
    def preparar(df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["status"] == "ok"].copy()

        if usar == "majority" and df["repeat"].nunique() > 1:
            agrupado = df.groupby("row_id")
            return pd.DataFrame(
                {
                    "row_id": agrupado["predicted"].first().index,
                    "predicted": agrupado["predicted"].agg(
                        lambda s: s.value_counts().idxmax()
                    ),
                    "expected": agrupado["expected"].first(),
                }
            ).reset_index(drop=True)

        return df[df["repeat"] == df["repeat"].min()][
            ["row_id", "predicted", "expected"]
        ]

    a = preparar(df_a)
    b = preparar(df_b)

    comuns = sorted(set(a["row_id"]) & set(b["row_id"]))

    if not comuns:
        raise SystemExit("As rodadas não têm linhas em comum.")

    a = a[a["row_id"].isin(comuns)].sort_values("row_id")
    b = b[b["row_id"].isin(comuns)].sort_values("row_id")

    print(f"\n--- {len(comuns)} linhas em comum ---")

    metricas_a = compute_metrics(a.assign(status="ok"))["classification"]
    metricas_b = compute_metrics(b.assign(status="ok"))["classification"]

    print(
        f"\n{'métrica':<28} {'A':>10} {'B':>10} {'B - A':>10}"
    )

    for rotulo, chave in (
        ("acurácia balanceada", "balanced_accuracy"),
        ("acurácia estrita", "accuracy_strict"),
        ("falsos não urgentes", "false_non_urgent"),
        ("falsos urgentes", "false_urgent"),
    ):
        valor_a = metricas_a[chave]
        valor_b = metricas_b[chave]

        if valor_a is None or valor_b is None:
            continue

        if isinstance(valor_a, float):
            print(
                f"{rotulo:<28} {valor_a:>10.4f} {valor_b:>10.4f} "
                f"{valor_b - valor_a:>+10.4f}"
            )
        else:
            print(
                f"{rotulo:<28} {valor_a:>10} {valor_b:>10} "
                f"{valor_b - valor_a:>+10}"
            )

    acertos_a = (a["expected"].values == a["predicted"].values).astype(int)
    acertos_b = (b["expected"].values == b["predicted"].values).astype(int)

    resultado = mcnemar(
        b=int(((acertos_a == 1) & (acertos_b == 0)).sum()),
        c=int(((acertos_a == 0) & (acertos_b == 1)).sum()),
    )

    print("\n--- teste de McNemar (pareado) ---")
    print(f"  A acertou e B errou : {resultado['b']}")
    print(f"  A errou e B acertou : {resultado['c']}")
    print(f"  p exato             : {resultado['p_exact']:.4f}")
    print(f"  p mid               : {resultado['p_mid']:.4f}")

    if resultado.get("note"):
        print(f"  {resultado['note']}")

    intervalo = bootstrap_diferenca(acertos_b, acertos_a)

    print("\n--- diferença de acurácia estrita ---")
    print(f"  B - A  : {intervalo['diff']:+.4f}")
    print(f"  IC 95% : {intervalo['ci95']}")

    print(
        f"\n  Com {len(comuns)} linhas, uma diferença só é detectável a "
        "partir de cerca de 6 pontos percentuais (6 linhas líquidas)."
    )

    viradas = a.merge(b, on="row_id", suffixes=("_a", "_b"))
    viradas = viradas[viradas["predicted_a"] != viradas["predicted_b"]]

    if not viradas.empty:
        print(f"\n--- {len(viradas)} linha(s) mudaram de classificação ---")

        for _, linha in viradas.head(15).iterrows():
            print(
                f"  linha {int(linha['row_id']):>3} "
                f"(esperado {linha['expected_a']:<14}) "
                f"{linha['predicted_a']:<14} -> {linha['predicted_b']}"
            )


def comando_cite(diretorio: Path) -> None:

    DIRETORIO_CITADAS.mkdir(parents=True, exist_ok=True)

    destino = DIRETORIO_CITADAS / diretorio.name

    if destino.exists():
        shutil.rmtree(destino)

    shutil.copytree(diretorio, destino)

    manifesto, _ = carregar(destino)
    metricas = json.loads(
        (destino / "metrics.json").read_text(encoding="utf-8")
    )
    c = metricas["classification"]

    relativo = destino.relative_to(RAIZ).as_posix()

    print(f"Copiada para {relativo}\n")
    print("Trecho para a evidência:\n")
    print(
        f"Rodada [`{manifesto['run_id']}`]"
        f"(../../{relativo}/report.md) · "
        f"preset `{manifesto.get('preset')}` · "
        f"{metricas['rows_evaluated']} linhas · "
        f"acurácia balanceada {_formatar(c['balanced_accuracy'])}, "
        f"estrita {_formatar(c['accuracy_strict'])}, "
        f"{c['false_non_urgent']} falso(s) não urgente(s)."
    )


def main(argv=None) -> None:

    parser = argparse.ArgumentParser(
        description="Relatórios e comparação de rodadas de avaliação."
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_report = sub.add_parser("report", help="regera métricas e relatório")
    p_report.add_argument("run", type=Path)

    p_compare = sub.add_parser("compare", help="compara duas rodadas")
    p_compare.add_argument("run_a", type=Path)
    p_compare.add_argument("run_b", type=Path)
    p_compare.add_argument(
        "--use", choices=["first", "majority"], default="first"
    )

    p_cite = sub.add_parser("cite", help="promove uma rodada citada")
    p_cite.add_argument("run", type=Path)

    argumentos = parser.parse_args(argv)

    if argumentos.comando == "report":
        comando_report(argumentos.run)
    elif argumentos.comando == "compare":
        comando_compare(argumentos.run_a, argumentos.run_b, argumentos.use)
    else:
        comando_cite(argumentos.run)


if __name__ == "__main__":
    main()
