"""
A busca com os dados do cadastro do pet (rodada 22 do Ryu). Só a busca:
nenhum modelo de linguagem, nenhuma cota do Gemini.

Para cada relato, chama `POST /search/` com três consultas: V0 (só o relato),
V1 (espécie, idade e histórico na frente) e V2 (V1 com raça e peso), e anota a
posição da ficha certa.

    python scripts/experimento_busca_com_cadastro.py --output <arquivo.jsonl>
"""

import argparse
import csv
import json
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[1]
ESPECIE = {"cao": "Cão", "gato": "Gato"}


def prefixo(caso: dict, com_raca_e_peso: bool) -> str:
    """O cadastro em frase curta, só com fatos clínicos (nunca o nome)."""
    primeira = ESPECIE[caso["species"]]
    if caso.get("age"):
        primeira += f", {caso['age']}"
    if com_raca_e_peso and caso.get("breed"):
        primeira += f", {caso['breed']}"
    if com_raca_e_peso and caso.get("weight_kg"):
        primeira += f", {caso['weight_kg'].replace('.', ',')} kg"
    partes = [primeira + "."]
    if caso.get("relevant_history"):
        partes.append(caso["relevant_history"].strip())
    return " ".join(partes)


def casos() -> list[dict]:
    lista = []
    for linha in csv.DictReader(open(RAIZ / "evidencias/ryu/dados/2026-10-06-casos-cadastro-pet.csv", encoding="utf-8")):
        if linha["par"] != "controle":
            grupo = "pares_A" if linha["id"].endswith("a") else "pares_B"
            lista.append(linha | {"grupo": grupo, "text": linha["relato"]})
    for linha in csv.DictReader(open(RAIZ / "data/prova2/casos.csv", encoding="utf-8")):
        if linha["split"] == "calibracao" and linha["topic"]:
            lista.append(linha | {"grupo": "prova2_calibracao"})
    for linha in csv.DictReader(open(RAIZ / "data/diagnostico/relatos_independentes.csv", encoding="utf-8")):
        if linha["topic"]:
            lista.append(linha | {"grupo": "independentes"})
    return lista


def posicao(api_url: str, consulta: str, topico: str):
    resposta = requests.post(f"{api_url}/search/", json={"question": consulta}, timeout=600)
    resposta.raise_for_status()
    topicos = [d["topic"] for d in resposta.json()["documents"]]
    return topicos.index(topico) + 1 if topico in topicos else None


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    with args.output.open("w", encoding="utf-8", newline="\n") as saida:
        for caso in casos():
            consultas = {
                "V0": caso["text"],
                "V1": prefixo(caso, False) + "\n" + caso["text"],
                "V2": prefixo(caso, True) + "\n" + caso["text"],
            }
            saida.write(json.dumps({
                "grupo": caso["grupo"], "id": caso["id"], "topic": caso["topic"],
                "prefixo_v1": prefixo(caso, False),
                **{v: posicao(args.api_url, q, caso["topic"]) for v, q in consultas.items()},
            }, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
