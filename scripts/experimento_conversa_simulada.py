"""
As perguntas extras levam à resposta certa? (rodada 21 do Ryu)

Um tutor simulado conversa com o workspace de verdade (`WorkspaceService`:
classificação, seleção de pergunta, formulário, os mesmos limites do app). O
tutor começa com uma mensagem vaga e conhece o relato completo, que fica
escondido do sistema; a cada pergunta, responde só com fatos do relato
completo, ou "não sei" quando o relato não diz. Grava num banco do MongoDB
separado (`--banco`), nunca no do app.

Fases, como o experimento do tradutor:

    # 1. no host: escolhe os casos da calibração da prova 2 (sorteio fixo)
    python scripts/experimento_conversa_simulada.py preparar --saida <casos.json>

    # 2. no container
    docker cp scripts/experimento_conversa_simulada.py backend-api:/tmp/
    docker cp <casos.json> backend-api:/tmp/casos_conversa.json
    docker exec -w /app -e PYTHONPATH=/app backend-api \\
        python /tmp/experimento_conversa_simulada.py rodar \\
        --casos /tmp/casos_conversa.json --saida /tmp/saida_conversa.jsonl
"""

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path
from uuid import uuid4

SEMENTE = "conversa-2026-10-06"
POR_CLASSE = 8
MAX_TURNOS_DO_TUTOR = 7

PROMPT_ABERTURA = """Você é o tutor de um cachorro ou gato e vai mandar a PRIMEIRA mensagem
para um aplicativo de pré-triagem veterinária. Abaixo está tudo o que você sabe.
Escreva só uma mensagem curta e vaga (1 frase), do jeito que um tutor preocupado
começaria a conversa: diga a espécie e UMA coisa genérica que chamou atenção, sem
contar os sinais mais importantes, sem dizer há quanto tempo e sem dizer se é grave.
Não invente nada que não esteja no relato. Responda só com a mensagem."""

PROMPT_RESPOSTA = """Você é o tutor de um cachorro ou gato conversando com um aplicativo de
pré-triagem. Tudo o que você sabe está no RELATO COMPLETO abaixo; você não sabe
nada além disso. O aplicativo fez uma pergunta. Responda em 1 frase curta, em
linguagem de tutor, usando SOMENTE fatos do relato completo que respondem à
pergunta. Se o relato completo não diz nada sobre o que foi perguntado, responda
exatamente: "Não sei, não reparei nisso." Não acrescente sinais que não estão no
relato e não dê diagnóstico."""

PROMPT_OPCAO = """Você é o tutor de um cachorro ou gato. Tudo o que você sabe está no RELATO
COMPLETO abaixo. O aplicativo mostrou uma pergunta com opções. Escolha a ÚNICA
opção que corresponde ao relato completo; se o relato não diz nada sobre isso,
escolha "Não observei". Responda copiando o texto da opção exatamente, e nada mais."""


def preparar(args) -> None:
    raiz = Path(__file__).resolve().parents[1]
    linhas = list(csv.DictReader(open(raiz / "data" / "prova2" / "casos.csv", encoding="utf-8")))
    calibracao = [l for l in linhas if l["split"] == "calibracao"]

    def sorteio(linha):
        return hashlib.sha256(f"{SEMENTE}:{linha['id']}".encode("utf-8")).hexdigest()

    escolhidos = []
    for classe in ("EMERGENCIA", "NAO_EMERGENCIA"):
        escolhidos += sorted((l for l in calibracao if l["expected_class"] == classe), key=sorteio)[:POR_CLASSE]
    escolhidos += [l for l in calibracao if l["expected_class"] == "INCERTO"]
    casos = [{"id": l["id"], "relato": l["text"], "esperado": l["expected_class"],
              "topic": l["topic"], "tone": l["tone"]} for l in escolhidos]
    args.saida.write_text(json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"{len(casos)} casos")


def rodar(args) -> None:
    from app.core.config import settings
    settings.MONGODB_DB_NAME = args.banco  # antes do primeiro acesso: nunca o banco do app

    from app.clients.gemini_query_client import GeminiQueryClient
    from app.schemas.auth import Principal
    from app.schemas.workspace import TurnInput
    from app.services.workspace_service import WorkspaceService

    def falar(prompt, texto):
        resposta = GeminiQueryClient._chat(prompt, texto)
        time.sleep(4)  # a cota gratuita tem limite por minuto
        return resposta

    tutor = Principal(user_id="avaliacao-ryu-rodada-21", role="tutor",
                      display_name="Tutor simulado", demo=True)
    casos = json.loads(Path(args.casos).read_text(encoding="utf-8"))
    feitos = set()
    if Path(args.saida).exists():
        feitos = {json.loads(l)["id"] for l in open(args.saida, encoding="utf-8")}

    with open(args.saida, "a", encoding="utf-8", newline="\n") as saida:
        for caso in casos:
            if caso["id"] in feitos:
                continue
            contexto = f"RELATO COMPLETO:\n{caso['relato']}"
            abertura = falar(PROMPT_ABERTURA, contexto)
            conversa = WorkspaceService.create(tutor)
            turnos = []
            mensagem, origem, opcao = abertura, "text", None
            for _ in range(MAX_TURNOS_DO_TUTOR):
                pedido = TurnInput(content=mensagem, request_id=uuid4().hex, origin=origem,
                                   question_id=(conversa.get("followup") or {}).get("question_id") if origem == "form" else None,
                                   selected_option=opcao)
                conversa, _ = WorkspaceService.submit(tutor, conversa["id"], pedido)
                WorkspaceService.process(tutor, conversa["id"], pedido.request_id)
                conversa = WorkspaceService.get(tutor, conversa["id"])
                if conversa["status"] == "failed":
                    turnos.append({"tutor": mensagem, "erro": conversa.get("error")})
                    break
                resposta = conversa["messages"][-1]
                acompanhamento = resposta.get("followup") or {}
                turnos.append({
                    "tutor": mensagem, "origem": origem,
                    "classe": resposta["triage"]["classificacao"],
                    "estado": acompanhamento.get("state"),
                    "pergunta": acompanhamento.get("question"),
                    "opcoes": acompanhamento.get("options") or [],
                    "fichas": [s["topic"] for s in resposta.get("sources", [])],
                })
                if acompanhamento.get("state") == "asking":
                    pergunta = acompanhamento["question"]
                    mensagem = falar(PROMPT_RESPOSTA, f"{contexto}\n\nPERGUNTA DO APLICATIVO: {pergunta}")
                    origem, opcao = "text", None
                elif acompanhamento.get("state") == "form":
                    opcoes = acompanhamento["options"]
                    escolha = falar(
                        PROMPT_OPCAO, f"{contexto}\n\nPERGUNTA: {acompanhamento['question']}\nOPÇÕES:\n" + "\n".join(opcoes)
                    ).strip().strip('"')
                    opcao = escolha if escolha in opcoes else "Não observei"
                    mensagem, origem = opcao, "form"
                else:
                    break
            final = next((t for t in reversed(turnos) if "classe" in t), None)
            saida.write(json.dumps({
                "id": caso["id"], "esperado": caso["esperado"], "topic": caso["topic"],
                "tone": caso["tone"], "abertura": abertura, "turnos": turnos,
                "classe_inicial": turnos[0].get("classe") if turnos else None,
                "classe_final": final["classe"] if final else None,
                "estado_final": final["estado"] if final else None,
                "perguntas": sum(1 for t in turnos if t.get("estado") in {"asking", "form"}),
            }, ensure_ascii=False) + "\n")
            saida.flush()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    sub = parser.add_subparsers(dest="fase", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("--saida", type=Path, required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--casos", required=True)
    r.add_argument("--saida", required=True)
    r.add_argument("--banco", default="tcc_conversa_simulada_ryu_20261006")
    args = parser.parse_args(argv)
    preparar(args) if args.fase == "preparar" else rodar(args)


if __name__ == "__main__":
    main()
