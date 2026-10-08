"""
Monta a prova 2 a partir dos pedidos e do que os autores devolveram
(rodada 28 do João).

Entrada:
- `data/prova2/geracao/pedidos/lote_<n>.json` — os pedidos completos, com o
  tópico do mapa e o rótulo (gerados por `prova2_pedidos.py`);
- `data/prova2/geracao/autores/lote_<n>/relatos.json` — o que o autor do lote
  escreveu: `id`, `texto`, `inspiracao`.

Saída: `data/prova2/casos.csv`, uma linha por relato, e a conferência mínima
impressa (composição, ids, duplicatas, "mas" por classe). Os rótulos valem
depois da validação dos veterinários, registrada em `data/prova2/validacao.json`
(rodada 30): com o registro, o `marked_by` diz quem validou e quando; sem ele,
que o rótulo é provisório.

A coluna `split` sai da divisão por assunto da rodada 20 do João (decisão 4),
feita na rodada 17 do Ryu: um relato de cada quadro na `calibracao`, os outros
quatro no `teste`; dos especiais, 2 + 2 + 1 na `calibracao`. Qual relato vai é
sorteio determinístico pela `SEMENTE_DIVISAO`, fixada antes de qualquer
medição — mudar a semente muda a prova e exige recongelar.

    python scripts/prova2_montar.py            # grava o casos.csv
    python scripts/prova2_montar.py --check    # confere que está em dia
"""

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GERACAO = RAIZ / "data" / "prova2" / "geracao"
DESTINO = RAIZ / "data" / "prova2" / "casos.csv"
VALIDACAO = RAIZ / "data" / "prova2" / "validacao.json"
LOTES = range(1, 10)

COLUNAS = [
    "id", "text", "species", "expected_class", "expected_urgency", "topic",
    "tone", "difficulty_tag", "confusion_pair_topic", "persona", "author",
    "note", "source_reference", "marked_by", "split",
]
ESPECIE = {"cão": "cao", "cadela": "cao", "gato": "gato", "gata": "gato"}
MAS = re.compile(r"\bmas\b", re.IGNORECASE)

SEMENTE_DIVISAO = "prova2-divisao-2026-10-05"
# Quantos relatos de cada grupo vão para a calibração: 1 por quadro do mapa e,
# dos 25 especiais, 5 na proporção de cada tipo (10 : 8 : 7).
CALIBRACAO_POR_QUADRO = 1
CALIBRACAO_ESPECIAIS = {
    "informacao_insuficiente": 2,
    "fora_do_mapa_clinico": 2,
    "nao_clinico": 1,
}


def _ler_json(caminho: Path):
    return json.loads(caminho.read_text(encoding="utf-8"))


def marcado_por(lote: int, validacao: dict | None) -> str:
    autor = f"IA (agente isolado, lote {lote})"
    if validacao and validacao.get("rotulos") == "validados":
        ano, mes, dia = validacao["data"].split("-")
        return f"{autor} - rotulo validado por especialista ({validacao['por']}, {dia}/{mes}/{ano})"
    return f"{autor} - provisorio, aguardando validacao de especialista"


def dividir(linhas: list[dict], semente: str = SEMENTE_DIVISAO) -> None:
    """Preenche `split` em cada linha: `calibracao` ou `teste`."""
    grupos = defaultdict(list)
    for linha in linhas:
        grupos[linha["topic"] or linha["difficulty_tag"]].append(linha)
    for chave, membros in grupos.items():
        quantos = (CALIBRACAO_POR_QUADRO if membros[0]["topic"]
                   else CALIBRACAO_ESPECIAIS[chave])
        sorteio = sorted(
            membros,
            key=lambda l: hashlib.sha256(f"{semente}:{l['id']}".encode("utf-8")).hexdigest(),
        )
        escolhidos = {l["id"] for l in sorteio[:quantos]}
        for linha in membros:
            linha["split"] = "calibracao" if linha["id"] in escolhidos else "teste"


def montar() -> tuple[str, dict]:
    validacao = _ler_json(VALIDACAO) if VALIDACAO.exists() else None
    linhas = []
    problemas = []
    for lote in LOTES:
        pedidos = _ler_json(GERACAO / "pedidos" / f"lote_{lote}.json")["pedidos"]
        relatos = {r["id"]: r for r in _ler_json(GERACAO / "autores" / f"lote_{lote}" / "relatos.json")}
        if set(relatos) != {p["id"] for p in pedidos}:
            problemas.append(f"lote {lote}: ids dos relatos não batem com os pedidos")
        for pedido in pedidos:
            relato = relatos.get(pedido["id"])
            if relato is None:
                continue
            nota = f"Quadro pedido: {pedido['quadro_leigo']}"
            if pedido["familia_calma"]:
                nota += f"; calma: {pedido['familia_calma']}"
            if pedido["parecido_com"]:
                nota += f"; parecido com: {pedido['parecido_com']}"
            nota += f"; 'mas' pedido: {'sim' if pedido['usar_mas'] else 'não'}"
            linhas.append({
                "id": pedido["id"],
                "text": " ".join(str(relato["texto"]).split()),
                "species": ESPECIE[pedido["especie"]],
                "expected_class": pedido["classe"],
                "expected_urgency": pedido["expected_urgency"],
                "topic": pedido["topic"],
                "tone": pedido["tom"],
                "difficulty_tag": pedido["difficulty_tag"],
                "confusion_pair_topic": pedido["confusion_pair_topic"],
                "persona": pedido["persona"],
                "author": f"Claude, autor isolado do lote {lote}",
                "note": nota,
                "source_reference": (
                    f"data/curadoria/mapa-de-assuntos.csv#{pedido['topic']}" if pedido["topic"] else ""
                ),
                "marked_by": marcado_por(lote, validacao),
                "split": "",
            })

    dividir(linhas)
    textos = Counter(linha["text"] for linha in linhas)
    conferencia = {
        "n": len(linhas),
        "por_classe": dict(Counter(l["expected_class"] for l in linhas)),
        "do_mapa_por_classe": dict(Counter(l["expected_class"] for l in linhas if l["topic"])),
        "especiais": dict(Counter(l["difficulty_tag"] for l in linhas if not l["topic"])),
        "quadros": len({l["topic"] for l in linhas if l["topic"]}),
        "ids_unicos": len({l["id"] for l in linhas}) == len(linhas),
        "textos_repetidos": sum(n - 1 for n in textos.values() if n > 1),
        "mas_por_classe": {
            classe: f"{sum(1 for l in linhas if l['expected_class'] == classe and MAS.search(l['text']))}/"
                    f"{sum(1 for l in linhas if l['expected_class'] == classe)}"
            for classe in ("EMERGENCIA", "NAO_EMERGENCIA", "INCERTO")
        },
        "por_split": {
            split: dict(Counter(l["expected_class"] for l in linhas if l["split"] == split))
            for split in ("calibracao", "teste")
        },
        "problemas": problemas,
    }

    saida = io.StringIO()
    escritor = csv.DictWriter(saida, fieldnames=COLUNAS, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(linhas)
    return saida.getvalue(), conferencia


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    conteudo, conferencia = montar()
    if conferencia["problemas"]:
        raise SystemExit("\n".join(conferencia["problemas"]))
    if args.check:
        atual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if atual.replace("\r\n", "\n") != conteudo:
            raise SystemExit("data/prova2/casos.csv desatualizado; rode python scripts/prova2_montar.py")
        print("casos.csv da prova 2 em dia")
        return
    with open(DESTINO, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(conteudo)
    print(json.dumps(conferencia, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
