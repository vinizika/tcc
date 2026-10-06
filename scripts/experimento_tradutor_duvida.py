"""
O tradutor só nos casos de dúvida, medido só na busca (rodada 19 do Ryu,
B-69). Experimento: nada no sistema muda.

Duas fases, porque o Gemini e a chave só existem dentro do container:

    # 1. no host: separa os relatos em que o gatilho dispara
    python scripts/experimento_tradutor_duvida.py preparar \\
        --diagnostico evidencias/ryu/dados/2026-10-06-diagnostico-busca.jsonl \\
        --saida <entrada.json>

    # 2. no container (o Gemini escreve as paráfrases e a busca roda de novo)
    docker cp scripts/experimento_tradutor_duvida.py backend-api:/tmp/
    docker cp <entrada.json> backend-api:/tmp/entrada.json
    docker exec -w /app -e PYTHONPATH=/app backend-api \\
        python /tmp/experimento_tradutor_duvida.py rodar \\
        --entrada /tmp/entrada.json --saida /tmp/saida.jsonl
"""

import argparse
import json
import sys
import time
from pathlib import Path

LIMIAR_DISTANCIA = 0.0155  # o gatilho escolhido só no calibrar (passo 1)

PROMPT_PARAFRASE = """Você recebe o relato de um tutor sobre o cachorro ou o gato dele.
Escreva 3 versões diferentes do MESMO relato, uma por linha, como outro tutor
contaria a mesma situação com outras palavras do dia a dia.

Regras obrigatórias:
- Mantenha exatamente os sinais que o tutor observou, a espécie, a idade e há quanto tempo acontece.
- Não acrescente nenhum sinal que o tutor não contou, e não tire nenhum.
- PROIBIDO: nome de doença, diagnóstico, causa provável, tratamento, remédio,
  e palavras de urgência ("urgente", "emergência", "grave", "imediato").
- Se o tutor disse que algo NÃO aconteceu, mantenha a negação.
- Responda só com as 3 linhas, sem numeração e sem explicação."""


def preparar(args) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from diagnostico_busca import CONJUNTOS, casos_do_conjunto

    textos = {}
    for nome, _papel, arquivo, split, coluna in CONJUNTOS:
        for caso in casos_do_conjunto(arquivo, split, coluna):
            textos[(nome, caso["id"])] = caso["text"]

    marcados = []
    for linha in map(json.loads, args.diagnostico.open(encoding="utf-8")):
        notas = [f["score"] for f in linha["fichas"]]
        if notas[0] - notas[1] < LIMIAR_DISTANCIA:
            linha["text"] = textos[(linha["conjunto"], linha["id"])]
            marcados.append(linha)
    args.saida.write_text(json.dumps(marcados, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"{len(marcados)} relatos marcados")


def rodar(args) -> None:
    import requests
    from app.clients.gemini_query_client import GeminiQueryClient

    marcados = json.loads(Path(args.entrada).read_text(encoding="utf-8"))
    feitos = set()
    if Path(args.saida).exists():
        feitos = {(l["conjunto"], l["id"]) for l in map(json.loads, open(args.saida, encoding="utf-8"))}

    with open(args.saida, "a", encoding="utf-8", newline="\n") as saida:
        for caso in marcados:
            if (caso["conjunto"], caso["id"]) in feitos:
                continue
            texto = GeminiQueryClient._chat(PROMPT_PARAFRASE, caso["text"])
            parafrases = [l.strip(" -•\t") for l in texto.splitlines() if l.strip()][:3]
            melhor: dict[str, float] = {}
            for consulta in [caso["text"], *parafrases]:
                resposta = requests.post(f"{args.api_url}/search/", json={"question": consulta}, timeout=600)
                resposta.raise_for_status()
                for doc in resposta.json()["documents"]:
                    melhor[doc["topic"]] = max(melhor.get(doc["topic"], -1.0), doc["score"])
            ordem = sorted(melhor, key=melhor.get, reverse=True)
            posicoes = [i + 1 for i, t in enumerate(ordem) if t in caso["topics"]]
            saida.write(json.dumps({
                "conjunto": caso["conjunto"], "papel": caso["papel"], "id": caso["id"],
                "topics": caso["topics"], "parafrases": parafrases,
                "posicao_cru": caso["posicao_certa"],
                "posicao_tradutor": posicoes[0] if posicoes else None,
                "top3_tradutor": ordem[:3],
            }, ensure_ascii=False) + "\n")
            saida.flush()
            time.sleep(args.intervalo_s)  # a cota gratuita tem limite por minuto


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    sub = parser.add_subparsers(dest="fase", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("--diagnostico", type=Path, required=True)
    p.add_argument("--saida", type=Path, required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--entrada", required=True)
    r.add_argument("--saida", required=True)
    r.add_argument("--api-url", default="http://localhost:8000")
    r.add_argument("--intervalo-s", type=float, default=4.0)
    args = parser.parse_args(argv)
    preparar(args) if args.fase == "preparar" else rodar(args)


if __name__ == "__main__":
    main()
