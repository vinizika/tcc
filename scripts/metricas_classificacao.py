"""
Métricas de classificação para o relatório (rodada 26 do Ryu), calculadas a
partir das previsões caso a caso já registradas: nenhuma chamada nova a
modelo.

Classe positiva: EMERGENCIA. Uma emergência prevista como NAO_EMERGENCIA ou
INCERTO é falso negativo (emergência perdida, a semântica das autópsias); um
caso leve previsto como EMERGENCIA é falso positivo (falso alarme). A
acurácia é a concordância exata nas três classes, sobre todos os casos.

    python scripts/metricas_classificacao.py
"""

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AUTOPSIA = RAIZ / "data" / "evaluation" / "autopsia2" / "resultados_por_caso.csv"
CITADAS = RAIZ / "data" / "evaluation" / "cited"

CONJUNTOS = {
    "Prova 1 e régua (134)": {"calib", "dev", "regua"},
    "Relatos independentes (122)": {"indep", "indep2"},
    "Piloto da prova 2 (40)": {"piloto"},
}

CONFIGURACOES = [
    ("Fichas + Gemini", "ctxarq_bgecl_leitura_mapa_top3", "gemini-3.5-flash-lite"),
    ("Fichas + Qwen", "ctxarq_bgecl_leitura_mapa_top3", "qwen3-8b"),
    ("Gemini sem contexto", "sem_rag", "gemini-3.5-flash-lite"),
    ("Qwen sem contexto", "sem_rag", "qwen3-8b"),
    ("Llama sem contexto", "sem_rag", "llama3.2-3b"),
    ("Base acadêmica + Llama", "rag_full", "llama3.2-3b"),
    ("Base acadêmica + Llama + reformulação", "ragtrad_full", "llama3.2-3b"),
]

CALIBRACAO_PROVA2 = [
    ("Fichas + Gemini (05/10)", "20261005-224021_r18_gemini_calib"),
    ("Fichas + Gemini (07/10)", "20261007-223852_r23_calib_v1"),
    ("Fichas + Gemini, regra de suficiência (07/10)", "20261007-222308_r23_calib_v2"),
    ("Gemini sem contexto (05/10)", "20261005-224914_r18_gemini_sem_busca_calib"),
    ("Fichas + Llama (05/10)", "20261005-225812_r18_llama_calib"),
]


def metricas(pares: list[tuple[str, str]]) -> dict:
    """pares = [(esperado, previsto)]"""
    vp = sum(1 for e, p in pares if e == "EMERGENCIA" and p == "EMERGENCIA")
    fn = sum(1 for e, p in pares if e == "EMERGENCIA" and p != "EMERGENCIA")
    fp = sum(1 for e, p in pares if e == "NAO_EMERGENCIA" and p == "EMERGENCIA")
    vn = sum(1 for e, p in pares if e == "NAO_EMERGENCIA" and p != "EMERGENCIA")
    sens = vp / (vp + fn) if vp + fn else None
    espec = vn / (vn + fp) if vn + fp else None
    prec = vp / (vp + fp) if vp + fp else None
    f1 = 2 * prec * sens / (prec + sens) if prec and sens else None
    return {
        "n": len(pares),
        "acuracia": sum(e == p for e, p in pares) / len(pares),
        "sensibilidade": sens,
        "especificidade": espec,
        "precisao": prec,
        "f1": f1,
        "acuracia_balanceada": (sens + espec) / 2 if sens is not None and espec is not None else None,
        "perdidas": fn,
        "falsos_alarmes": fp,
        "incerto": sum(1 for _, p in pares if p == "INCERTO"),
    }


def linhas() -> list[dict]:
    saida = []
    casos = list(csv.DictReader(AUTOPSIA.open(encoding="utf-8")))
    for conjunto, lotes in CONJUNTOS.items():
        for nome, condicao, atendente in CONFIGURACOES:
            pares = [(c["esperado"], c["previsto"]) for c in casos
                     if c["condicao"] == condicao and c["atendente"] == atendente and c["lote"] in lotes]
            if pares:
                saida.append({"conjunto": conjunto, "configuracao": nome, **metricas(pares)})
    for nome, rodada in CALIBRACAO_PROVA2:
        arquivo = CITADAS / rodada / "predictions.csv"
        pares = [(c["expected"], c["predicted"]) for c in csv.DictReader(arquivo.open(encoding="utf-8"))]
        saida.append({"conjunto": "Calibração da prova 2 (66)", "configuracao": nome, **metricas(pares)})
    return saida


def main() -> None:
    def fmt(x):
        return "—" if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))

    colunas = ["conjunto", "configuracao", "n", "acuracia", "acuracia_balanceada", "sensibilidade",
               "especificidade", "precisao", "f1", "perdidas", "falsos_alarmes", "incerto"]
    print(" | ".join(colunas))
    for linha in linhas():
        print(" | ".join(fmt(linha[c]) for c in colunas))


if __name__ == "__main__":
    main()
