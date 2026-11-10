"""
O histórico do animal muda a decisão do jeito que a regra promete? (rodada 34 do João)

Roda cada relato sem e com o histórico do animal (documento anexado ou
conversa anterior), pelo mesmo caminho do app: o `poc_pipeline()` do
workspace, com as opções do `WorkspaceService.process`, o cadastro no mesmo
formato e o bloco montado pela mesma função (`records_block`). A busca recebe
só o relato, como no app. Não grava nada no MongoDB. Precisa do backend e da
chave do Gemini, então roda no container:

    docker cp scripts/experimento_historico_do_animal.py backend-api:/tmp/
    docker cp evidencias/joao/dados/2026-11-09-pares-historico-do-animal.csv backend-api:/tmp/pares.csv
    docker exec -w /app -e PYTHONPATH=/app backend-api \\
        python /tmp/experimento_historico_do_animal.py --pares /tmp/pares.csv \\
        --saida /tmp/saida.jsonl --repeticoes 2
    docker cp backend-api:/tmp/saida.jsonl evidencias/joao/dados/2026-11-09-historico-do-animal-resultados.jsonl

    python scripts/experimento_historico_do_animal.py --resumo <resultados.jsonl>

Os pares são de desenvolvimento, escritos por quem escreveu a regra e sem
validação de veterinário: servem para ver o comportamento, não para o número
final do TCC.
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ORDEM = {"NAO_EMERGENCIA": 0, "INCERTO": 1, "EMERGENCIA": 2}


def registros_do_par(par: dict, records, agora: datetime):
    """O bloco de histórico do par, montado pela função que o app usa."""
    documentos, conversas = [], []
    if par.get("doc_resumo"):
        documentos.append({"id": "doc-" + par["id"], "kind": par["doc_tipo"], "document_date": par["doc_data"], "summary": par["doc_resumo"]})
    if par.get("conversa_relato"):
        quando = (agora - timedelta(days=int(par["conversa_dias"]))).isoformat()
        data, ha = records._quando(quando, agora)
        conversas.append({"conversation_id": "conv-" + par["id"], "date": data, "ago": ha,
                          "report": par["conversa_relato"], "classification": par["conversa_classe"]})
    bloco, _ = records.records_block(documentos, conversas)
    return bloco


def rodar(args) -> None:
    from app.core.config import settings
    from app.schemas.triage import PipelineOptions
    from app.services import animal_records_service as records
    from app.services.workspace_service import poc_pipeline

    pares = list(csv.DictReader(open(args.pares, encoding="utf-8")))
    feitos = set()
    if Path(args.saida).exists():
        feitos = {(l["id"], l["braco"], l["repeticao"]) for l in map(json.loads, open(args.saida, encoding="utf-8"))}

    agora = datetime.now(timezone.utc)
    pipeline = poc_pipeline()
    with open(args.saida, "a", encoding="utf-8", newline="\n") as saida:
        for repeticao in range(args.repeticoes):
            for par in pares:
                for braco in ("sem_historico", "com_historico"):
                    if (par["id"], braco, repeticao) in feitos:
                        continue
                    bloco = registros_do_par(par, records, agora) if braco == "com_historico" else None
                    extra = {"animal_records": bloco} if bloco else {}
                    opcoes = PipelineOptions(
                        num_ctx=settings.WORKSPACE_NUM_CTX, retrieval_enabled=True,
                        prompt_version=settings.WORKSPACE_PROMPT_VERSION, cot_enabled=False,
                        query_rewriting_enabled=False, multi_query_enabled=False, hyde_enabled=False,
                        attendant_provider="gemini")
                    resultado = pipeline.execute(par["relato"], opcoes, animal_context=f"name: {par['nome']}; species: {par['especie']}",
                                                 retrieval_question=par["relato"], **extra)
                    saida.write(json.dumps({
                        "id": par["id"], "grupo": par["grupo"], "braco": braco, "repeticao": repeticao,
                        "classificacao": resultado.triage.classificacao,
                        "justificativa": resultado.triage.justificativa,
                        "recomendacao": resultado.triage.recomendacao,
                        "historico": bloco,
                        "modelo": resultado.provenance.attendant.model if resultado.provenance and resultado.provenance.attendant else None,
                        "prompt_version": settings.WORKSPACE_PROMPT_VERSION,
                        "quando": datetime.now(timezone.utc).isoformat(),
                    }, ensure_ascii=False) + "\n")
                    saida.flush()
                    print(par["id"], braco, repeticao, resultado.triage.classificacao, flush=True)


def resumo(caminho: str) -> None:
    linhas = [json.loads(l) for l in open(caminho, encoding="utf-8")]
    por = defaultdict(dict)
    for l in linhas:
        por[(l["repeticao"], l["id"])][l["braco"]] = l["classificacao"]
    grupos = {l["id"]: l["grupo"] for l in linhas}
    for repeticao in sorted({r for r, _ in por}):
        print(f"\nRepetição {repeticao + 1}")
        conta = defaultdict(lambda: defaultdict(int))
        for (r, pid), d in sorted(por.items()):
            if r != repeticao or len(d) < 2:
                continue
            g, sem, com = grupos[pid], d["sem_historico"], d["com_historico"]
            c = conta[g]
            c["n"] += 1
            c["subiu"] += ORDEM[com] > ORDEM[sem]
            c["desceu"] += ORDEM[com] < ORDEM[sem]
            c["com_nao"] += com == "NAO_EMERGENCIA"
            c["com_emergencia"] += com == "EMERGENCIA"
            print(f"  {pid:<4} {g:<28} sem: {sem:<15} com: {com}")
        for g, c in sorted(conta.items()):
            print(f"  [{g}] n={c['n']} · subiu {c['subiu']} · desceu {c['desceu']} · NAO_EMERGENCIA com histórico {c['com_nao']} · EMERGENCIA com histórico {c['com_emergencia']}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--pares")
    parser.add_argument("--saida")
    parser.add_argument("--repeticoes", type=int, default=2)
    parser.add_argument("--resumo", help="Só resume um arquivo de resultados já gravado")
    args = parser.parse_args(argv)
    if args.resumo:
        resumo(args.resumo)
    else:
        if not (args.pares and args.saida):
            parser.error("--pares e --saida são obrigatórios para rodar")
        rodar(args)


if __name__ == "__main__":
    main()
