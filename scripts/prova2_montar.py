"""
Monta a prova 2 a partir dos pedidos e do que os autores devolveram
(rodada 28 do João).

Entrada:
- `data/prova2/geracao/pedidos/lote_<n>.json` — os pedidos completos, com o
  tópico do mapa e o rótulo (gerados por `prova2_pedidos.py`);
- `data/prova2/geracao/autores/lote_<n>/relatos.json` — o que o autor do lote
  escreveu: `id`, `texto`, `inspiracao`.

Saída: `data/prova2/casos.csv`, uma linha por relato, e a conferência mínima
impressa (composição, ids, duplicatas, "mas" por classe). Os rótulos são
**provisórios**: valem depois da validação dos veterinários.

    python scripts/prova2_montar.py            # grava o casos.csv
    python scripts/prova2_montar.py --check    # confere que está em dia
"""

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GERACAO = RAIZ / "data" / "prova2" / "geracao"
DESTINO = RAIZ / "data" / "prova2" / "casos.csv"
LOTES = range(1, 10)

COLUNAS = [
    "id", "text", "species", "expected_class", "expected_urgency", "topic",
    "tone", "difficulty_tag", "confusion_pair_topic", "persona", "author",
    "note", "source_reference", "marked_by", "split",
]
ESPECIE = {"cão": "cao", "cadela": "cao", "gato": "gato", "gata": "gato"}
MAS = re.compile(r"\bmas\b", re.IGNORECASE)


def _ler_json(caminho: Path):
    return json.loads(caminho.read_text(encoding="utf-8"))


def montar() -> tuple[str, dict]:
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
                "marked_by": f"IA (agente isolado, lote {lote}) - provisorio, aguardando validacao de especialista",
                "split": "",
            })

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
