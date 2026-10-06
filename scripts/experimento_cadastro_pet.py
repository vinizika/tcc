"""
O cadastro do pet ajuda a decidir? (rodada 20 do Ryu)

Roda cada relato sem e com o cadastro do animal, pelo mesmo caminho do
primeiro turno do app (o `poc_pipeline()` do workspace, com as opções do
`WorkspaceService.process` e o contexto montado no mesmo formato). Não grava
nada no MongoDB. Precisa do backend (e da chave do Gemini), então roda no
container:

    docker cp scripts/experimento_cadastro_pet.py backend-api:/tmp/
    docker cp <casos.csv> backend-api:/tmp/casos.csv
    docker exec -w /app -e PYTHONPATH=/app backend-api \\
        python /tmp/experimento_cadastro_pet.py --casos /tmp/casos.csv \\
        --saida /tmp/saida.jsonl --repeticoes 2
"""

import argparse
import csv
import json
from pathlib import Path

CAMPOS_DO_CONTEXTO = ("name", "species", "age", "weight_kg", "breed", "relevant_history")


def contexto_do_animal(caso: dict) -> str:
    """O mesmo texto que o WorkspaceService.process monta a partir do pet salvo."""
    partes = []
    for campo in CAMPOS_DO_CONTEXTO:
        valor = caso.get(campo) or None
        if campo == "weight_kg" and valor is not None:
            valor = float(valor)
        if valor is not None:
            partes.append(f"{campo}: {valor}")
    return "; ".join(partes)


def consulta_com_cadastro(caso: dict) -> str:
    """V1 da rodada 22: espécie, idade e histórico na frente do relato."""
    primeira = {"cao": "Cão", "gato": "Gato"}[caso["species"]]
    if caso.get("age"):
        primeira += f", {caso['age']}"
    partes = [primeira + "."]
    if caso.get("relevant_history"):
        partes.append(caso["relevant_history"].strip())
    return " ".join(partes) + "\n" + caso["relato"]


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--casos", required=True)
    parser.add_argument("--saida", required=True)
    parser.add_argument("--repeticoes", type=int, default=2)
    parser.add_argument("--bracos", default="sem_cadastro,com_cadastro",
                        help="Rodada 22: com_cadastro_e_busca põe o cadastro também na busca")
    args = parser.parse_args(argv)

    from app.core.config import settings
    from app.schemas.triage import PipelineOptions
    from app.services.workspace_service import poc_pipeline

    casos = list(csv.DictReader(open(args.casos, encoding="utf-8")))
    feitos = set()
    if Path(args.saida).exists():
        feitos = {(l["id"], l["braco"], l["repeticao"]) for l in map(json.loads, open(args.saida, encoding="utf-8"))}

    pipeline = poc_pipeline()
    with open(args.saida, "a", encoding="utf-8", newline="\n") as saida:
        for repeticao in range(args.repeticoes):
            for caso in casos:
                for braco in args.bracos.split(","):
                    if (caso["id"], braco, repeticao) in feitos:
                        continue
                    contexto = contexto_do_animal(caso) if braco != "sem_cadastro" else None
                    busca = consulta_com_cadastro(caso) if braco == "com_cadastro_e_busca" else caso["relato"]
                    opcoes = PipelineOptions(
                        num_ctx=settings.WORKSPACE_NUM_CTX, retrieval_enabled=True,
                        prompt_version="v1_grounded", cot_enabled=False,
                        query_rewriting_enabled=False, multi_query_enabled=False,
                        hyde_enabled=False, attendant_provider=settings.ATTENDANT_PROVIDER,
                    )
                    resultado = pipeline.execute(caso["relato"], opcoes, animal_context=contexto,
                                                 retrieval_question=busca)
                    saida.write(json.dumps({
                        "id": caso["id"], "par": caso["par"], "braco": braco, "repeticao": repeticao,
                        "esperado": caso["expected_class"], "previsto": resultado.triage.classificacao,
                        "contexto": contexto,
                        "fichas": [s.document.topic for s in resultado.sources],
                        "justificativa": resultado.triage.justificativa,
                    }, ensure_ascii=False) + "\n")
                    saida.flush()


if __name__ == "__main__":
    main()
