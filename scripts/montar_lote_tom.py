"""
Monta o lote do teste de tom (rodadas 14 e 18 do João).

Cada emergência da prova + régua (lote `dev`, calibração e régua de
recuperação: 74 casos) com uma frase tranquilizadora colada no fim, a mesma
da autópsia 2. O teste mede se o atendente rebaixa uma emergência porque o
tutor diz que o animal está bem. O rótulo continua EMERGENCIA.

    python scripts/montar_lote_tom.py            # grava data/diagnostico/tom_calmo.csv
    python scripts/montar_lote_tom.py --check    # confere que está em dia
"""

import argparse
import csv
import io
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "data" / "diagnostico" / "tom_calmo.csv"
# A frase da autópsia, com o espaço inicial: é colada depois de rstrip().
FRASE = " Mas fora isso continua comendo e brincando normalmente."
COLUNAS = ["id", "text", "expected_class", "topic", "lote", "frase"]


def _ler(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def montar() -> str:
    linhas = []
    fontes = (
        ("dev", [r for r in _ler(RAIZ / "data/prova/casos_oficiais.csv") if r["split"] == "dev"], "topic"),
        ("calib", _ler(RAIZ / "data/prova/casos_calibracao.csv"), "topic"),
        ("regua", _ler(RAIZ / "data/retrieval/cases.csv"), "expected_topics"),
    )
    for lote, registros, coluna_topico in fontes:
        for registro in registros:
            if registro["expected_class"] != "EMERGENCIA":
                continue
            linhas.append({
                "id": registro["id"],
                "text": registro["text"].rstrip() + FRASE,
                "expected_class": "EMERGENCIA",
                "topic": (registro.get(coluna_topico) or "").split(";")[0].strip(),
                "lote": lote,
                "frase": FRASE.strip(),
            })
    saida = io.StringIO()
    escritor = csv.DictWriter(saida, fieldnames=COLUNAS, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(linhas)
    return saida.getvalue()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    conteudo = montar()
    if args.check:
        atual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if atual.replace("\r\n", "\n") != conteudo:
            raise SystemExit("tom_calmo.csv desatualizado; rode python scripts/montar_lote_tom.py")
        print("tom_calmo.csv em dia")
        return
    with open(DESTINO, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(conteudo)
    print(f"gravado {DESTINO} ({conteudo.count(chr(10)) - 1} casos)")


if __name__ == "__main__":
    main()
