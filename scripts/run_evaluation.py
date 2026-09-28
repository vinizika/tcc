"""
Roda o conjunto de avaliação contra a API e grava os resultados.

Cada rodada produz um diretório com quatro arquivos:

    predictions.jsonl  cada relato enviado e a resposta completa
    manifest.json      o que foi executado: versão, dados, configuração
    metrics.json       os números
    report.md          leitura humana

O manifesto é o que torna duas rodadas comparáveis. Sem ele, dois números
diferentes não dizem se a mudança testada funcionou ou se o modelo, a base
de conhecimento ou os prompts mudaram no caminho.

Uso:
    python scripts/run_evaluation.py --preset naive_rag --subset full --name marco1
    python scripts/run_evaluation.py --resume data/evaluation/runs/<dir>
"""

import argparse
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from evaluation_metrics import compute_metrics
from report_evaluation import escrever_relatorio


RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "data" / "processed" / "dataset1_augmented_llm_validated.csv"
DIRETORIO_RODADAS = RAIZ / "data" / "evaluation" / "runs"
PRESETS = Path(__file__).resolve().parent / "presets.json"

ANIMAIS = ["Dog", "Cat"]

COLUNAS_SINTOMAS = [
    "symptoms1",
    "symptoms2",
    "symptoms3",
    "symptoms4",
    "symptoms5",
]

# Seed da amostragem dos subconjuntos: fixa para que "smoke" signifique
# sempre as mesmas linhas entre rodadas e entre máquinas.
SEED_AMOSTRAGEM = 20260904

# Espera entre tentativas quando a API falha por motivo transitório.
ESPERAS = [5, 15, 45]

MAX_ERROS_SEGUIDOS = 3


# ----------------------------------------------------------------------
# Construção dos relatos (idêntica à medição de 04/05)
# ----------------------------------------------------------------------


def get_symptoms(row) -> list[str]:

    sintomas = []

    for coluna in COLUNAS_SINTOMAS:
        valor = row[coluna]

        if pd.notna(valor) and str(valor).strip() != "":
            sintomas.append(str(valor).strip())

    return sintomas


def build_relato(row) -> str:
    """
    Mesmo texto do runner de 04/05. Não mudar sem registrar: a comparação
    com aquele resultado depende de o relato ser o mesmo.
    """

    return (
        f"Animal: {row['AnimalName']}. "
        f"Sintomas observados: {', '.join(get_symptoms(row))}."
    )


def get_expected_label(dangerous) -> str:

    if dangerous == "Yes":
        return "EMERGENCIA"

    if dangerous == "No":
        return "NAO_EMERGENCIA"

    return "INVALID_LABEL"


# ----------------------------------------------------------------------
# Cliente da API
# ----------------------------------------------------------------------


class ApiClient:
    """
    Conversa com o backend. Isolado para os testes poderem substituí-lo.
    """

    def __init__(self, base_url: str, timeout: int = 1500):
        self.base_url = base_url.rstrip("/")
        # Conectar é rápido; responder pode demorar muito. O tempo de
        # leitura precisa ser maior que o pior caso do servidor, senão o
        # runner desiste enquanto o Ollama continua ocupado e contamina o
        # tempo da linha seguinte.
        self.timeout = (5, timeout)

    def classify(self, relato: str, options: dict) -> dict:

        resposta = requests.post(
            f"{self.base_url}/chat/",
            json={"question": relato, "options": options},
            timeout=self.timeout,
        )
        resposta.raise_for_status()

        return resposta.json()

    def health(self) -> bool:

        try:
            return (
                requests.get(f"{self.base_url}/health/", timeout=10).json()[
                    "status"
                ]
                == "ok"
            )
        except Exception:
            return False

    def fingerprint(self) -> dict:

        try:
            resposta = requests.get(
                f"{self.base_url}/health/fingerprint", timeout=30
            )
            resposta.raise_for_status()
            return resposta.json()
        except Exception as erro:
            return {"error": str(erro)}


# ----------------------------------------------------------------------
# Configuração
# ----------------------------------------------------------------------


def carregar_presets() -> dict:

    with open(PRESETS, encoding="utf-8") as arquivo:
        presets = json.load(arquivo)

    return {
        nome: {
            chave: valor
            for chave, valor in conteudo.items()
            if not chave.startswith("_")
        }
        for nome, conteudo in presets.items()
        if not nome.startswith("_")
    }


def coagir(valor: str):
    """
    Converte o texto da linha de comando para o tipo que a API espera.
    """

    minusculo = valor.strip().lower()

    if minusculo in ("true", "false"):
        return minusculo == "true"

    if minusculo in ("none", "null"):
        return None

    try:
        return int(valor)
    except ValueError:
        pass

    try:
        return float(valor)
    except ValueError:
        pass

    return valor


OPCOES_VALIDAS = {
    "query_rewriting_enabled",
    "multi_query_enabled",
    "hyde_enabled",
    "retrieval_enabled",
    "retrieval_mode",
    "context_top_k",
    "context_min_score",
    "rewritten_hint_enabled",
    "cot_enabled",
    "cot_position",
    "self_refine_enabled",
    "prompt_version",
    "structured_output_mode",
    "think",
    "attendant_provider",
    "llm_model",
    "temperature",
    "seed",
    "num_predict",
    "include_debug",
}


def montar_opcoes(preset: str, ajustes: list[str]) -> dict:
    """
    Junta o preset com os ajustes da linha de comando.

    Uma chave desconhecida falha aqui, antes de qualquer requisição: um erro
    de digitação aceito em silêncio produziria uma rodada inteira medindo a
    configuração padrão, sem ninguém perceber.
    """

    presets = carregar_presets()

    if preset not in presets:
        raise SystemExit(
            f"Preset '{preset}' não existe. "
            f"Disponíveis: {', '.join(sorted(presets))}"
        )

    opcoes = dict(presets[preset])

    for ajuste in ajustes or []:
        if "=" not in ajuste:
            raise SystemExit(
                f"--set espera chave=valor, recebeu '{ajuste}'"
            )

        chave, valor = ajuste.split("=", 1)
        chave = chave.strip()

        if chave not in OPCOES_VALIDAS:
            raise SystemExit(
                f"Opção '{chave}' não existe. "
                f"Disponíveis: {', '.join(sorted(OPCOES_VALIDAS))}"
            )

        opcoes[chave] = coagir(valor)

    return opcoes


# ----------------------------------------------------------------------
# Seleção das linhas
# ----------------------------------------------------------------------


def carregar_dataset() -> pd.DataFrame:

    df = pd.read_csv(DATASET)

    return df[df["AnimalName"].isin(ANIMAIS)].copy()


# ----------------------------------------------------------------------
# Lotes no formato da prova (--cases)
# ----------------------------------------------------------------------

COLUNAS_DOS_CASOS = ("id", "text", "expected_class")


def carregar_casos(caminho: Path, split: str | None = None) -> pd.DataFrame:
    """
    Um lote no formato da prova: uma linha por relato, com `id`, `text` e
    `expected_class` (rodada 25 do João). As outras colunas (tópico, tom,
    espécie) seguem para a linha de resultado.

    Com `--split`, fica só aquele lote. Se o lote tiver congelamento
    (`<arquivo>.<split>.freeze.json`, de `prova_freeze.py`), o hash é
    conferido antes de qualquer requisição: um lote teste alterado não roda.
    """

    df = pd.read_csv(caminho, dtype=str, keep_default_na=False)

    faltando = [coluna for coluna in COLUNAS_DOS_CASOS if coluna not in df.columns]
    if faltando:
        raise SystemExit(
            f"{caminho} não tem as colunas {', '.join(faltando)} "
            f"(o formato é {', '.join(COLUNAS_DOS_CASOS)})."
        )

    if split is not None:
        if "split" not in df.columns:
            raise SystemExit(f"{caminho} não tem a coluna split.")
        df = df[df["split"] == split]
        if df.empty:
            raise SystemExit(f"Nenhuma linha com split={split!r} em {caminho}.")

        import prova_freeze

        manifesto_congelado = prova_freeze.caminho_manifesto(caminho, split)
        if manifesto_congelado.exists():
            esperado = json.loads(
                manifesto_congelado.read_text(encoding="utf-8")
            )["sha256"]
            atual = prova_freeze.hash_split(
                prova_freeze.carregar_split(caminho, split)
            )
            if atual != esperado:
                raise SystemExit(
                    f"O lote {split!r} de {caminho} não bate com o "
                    f"congelamento ({manifesto_congelado.name}). "
                    "Recongele de propósito ou não rode."
                )

    if df["id"].duplicated().any():
        raise SystemExit(f"{caminho} tem ids repetidos.")

    return df.set_index("id", drop=False)


def contexto_do_caso(linha, repeticao: int, seed) -> tuple[str, str, dict]:
    """O relato e o contexto de uma linha do modo --cases."""

    relato = str(linha["text"])
    extras = {
        coluna: linha[coluna]
        for coluna in ("topic", "tone", "species", "difficulty_tag", "split")
        if coluna in linha.index
    }
    return str(linha["id"]), relato, {
        "row_id": str(linha["id"]),
        "repeat": repeticao,
        "seed_used": seed,
        **extras,
        "relato": relato,
        "relato_sha1": hashlib.sha1(relato.encode("utf-8")).hexdigest()[:12],
        "expected": str(linha["expected_class"]),
    }


def selecionar(df: pd.DataFrame, subset: str, limite: int | None):
    """
    Os subconjuntos existem para iterar rápido sem perder o equilíbrio
    entre as classes: medir só emergências esconderia metade dos erros.
    """

    if subset == "full":
        escolhido = df
    else:
        quantidade = {"smoke": 12, "balanced": 27}[subset]

        emergencias = df[df["Dangerous"] == "Yes"]
        nao_emergencias = df[df["Dangerous"] == "No"]

        # As emergências são amostradas mantendo a proporção entre cão e
        # gato: um subconjunto só de cães mediria outra coisa.
        por_especie = []

        for _, grupo in emergencias.groupby("AnimalName"):
            fatia = max(1, round(quantidade * len(grupo) / len(emergencias)))

            por_especie.append(
                grupo.sample(
                    n=min(fatia, len(grupo)),
                    random_state=SEED_AMOSTRAGEM,
                )
            )

        # A classe menor tem 27 linhas: em "balanced" ela entra inteira.
        if quantidade < len(nao_emergencias):
            nao_emergencias = nao_emergencias.sample(
                n=quantidade, random_state=SEED_AMOSTRAGEM
            )

        escolhido = pd.concat(por_especie + [nao_emergencias]).sort_index()

    if limite and limite < len(escolhido):
        # Cortar as primeiras linhas traria só emergências, porque elas
        # ocupam os menores índices do arquivo — e uma acurácia medida sobre
        # uma classe só não diz nada. O corte alterna entre as classes.
        emergencias = list(escolhido[escolhido["Dangerous"] == "Yes"].index)
        nao_emergencias = list(escolhido[escolhido["Dangerous"] == "No"].index)

        intercalado = []

        for posicao in range(max(len(emergencias), len(nao_emergencias))):
            if posicao < len(emergencias):
                intercalado.append(emergencias[posicao])
            if posicao < len(nao_emergencias):
                intercalado.append(nao_emergencias[posicao])

        escolhido = escolhido.loc[sorted(intercalado[:limite])]

    return escolhido


# ----------------------------------------------------------------------
# Escrita
# ----------------------------------------------------------------------


def escrever_atomico(caminho: Path, conteudo: str) -> None:
    """
    Escreve em arquivo temporário e substitui de uma vez.

    Assim um Ctrl+C no meio da escrita não deixa um manifesto pela metade,
    que seria pior do que nenhum.
    """

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=caminho.parent,
        delete=False,
    ) as temporario:
        temporario.write(conteudo)
        temporario.flush()
        os.fsync(temporario.fileno())
        nome = temporario.name

    for tentativa in range(3):
        try:
            os.replace(nome, caminho)
            return
        except PermissionError:
            # No Windows, o arquivo pode estar aberto num editor.
            if tentativa == 2:
                raise SystemExit(
                    f"Não consegui escrever {caminho.name}. "
                    "Feche o arquivo se ele estiver aberto e tente de novo."
                )
            time.sleep(1)


def anexar_linha(caminho: Path, registro: dict) -> None:
    """
    Grava linha a linha, com sincronização: uma rodada de 40 minutos não
    pode perder tudo por uma interrupção no fim.
    """

    with open(caminho, "a", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
        arquivo.flush()
        os.fsync(arquivo.fileno())


def ler_previsoes(caminho: Path) -> list[dict]:
    """
    Lê o que já foi gravado, tolerando uma última linha incompleta —
    resultado normal de uma interrupção no meio da escrita.
    """

    if not caminho.exists():
        return []

    registros = []

    for numero, linha in enumerate(
        caminho.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not linha.strip():
            continue

        try:
            registros.append(json.loads(linha))
        except json.JSONDecodeError:
            print(
                f"  aviso: linha {numero} incompleta, será refeita",
                file=sys.stderr,
            )

    return registros


# ----------------------------------------------------------------------
# Achatamento da resposta
# ----------------------------------------------------------------------


def achatar(resposta: dict, contexto: dict) -> dict:
    """
    Transforma a resposta da API numa linha de resultado.

    A regra central: quando o modelo não devolveu uma saída utilizável, a
    API responde INCERTO com `schema_valid` falso. Isso vira INVALID_JSON,
    que é como a medição de 04/05 contabilizava esses casos.
    """

    triagem = resposta.get("triage") or {}
    recuperacao = resposta.get("retrieval") or {}
    tempos = resposta.get("timings") or {}
    depuracao = resposta.get("debug") or {}
    fontes = resposta.get("sources") or []
    procedencia = resposta.get("provenance") or {}
    atendente = procedencia.get("attendant") or {}
    consulta = procedencia.get("query_stage") or {}

    classificacao = triagem.get("classificacao")

    if triagem.get("schema_valid") is False:
        previsto = "INVALID_JSON"
    else:
        previsto = classificacao

    return {
        **contexto,
        "status": "ok",
        "error": None,
        "predicted": previsto,
        "classificacao_raw": classificacao,
        "json_parsed": triagem.get("json_parsed"),
        "schema_valid": triagem.get("schema_valid"),
        "attempts": triagem.get("attempts"),
        "done_reason": triagem.get("done_reason"),
        "n_sources_used": len(fontes),
        # O corte que de fato valeu e a trava de auditoria. `abaixo_do_corte`
        # nunca deve ser verdadeiro: se for, um trecho irrelevante chegou ao
        # classificador e a linha inteira é suspeita.
        "context_min_score": recuperacao.get("context_min_score"),
        "used_below_min_score": recuperacao.get("used_below_min_score"),
        "n_sources_cited": len(triagem.get("fontes") or []),
        "n_invalid_citations": len(
            triagem.get("invalid_source_indices") or []
        ),
        "used_chunk_ids": [f.get("chunk_id") for f in fontes],
        "cited_chunk_ids": [
            f.get("chunk_id") for f in (triagem.get("fontes") or [])
        ],
        "retrieval_returned": recuperacao.get("returned_count"),
        "retrieval_above_threshold": recuperacao.get(
            "above_threshold_count"
        ),
        "retrieval_max_score": recuperacao.get("max_score"),
        "retrieval_max_ranking_score": recuperacao.get("max_ranking_score"),
        "query_s": tempos.get("query_s"),
        "retrieval_s": tempos.get("retrieval_s"),
        "generation_s": tempos.get("generation_s"),
        "total_s": tempos.get("total_s"),
        "prompt_tokens": tempos.get("prompt_tokens"),
        "completion_tokens": tempos.get("completion_tokens"),
        "tokens_per_s": tempos.get("tokens_per_s"),
        "load_duration_s": tempos.get("load_duration_s"),
        "justificativa": triagem.get("justificativa"),
        "sinais_de_alerta": triagem.get("sinais_de_alerta"),
        # O raciocínio do Chain-of-Thought. Nulo nos braços sem a chave —
        # e nulo é diferente de vazio: distingue "não raciocinou" de
        # "raciocinou e não escreveu nada". O comprimento vira métrica; o
        # texto é o que permite ler, depois, se o modelo marcou o sinal
        # grave e mesmo assim concluiu errado.
        "raciocinio": triagem.get("raciocinio"),
        "len_raciocinio": len(triagem.get("raciocinio") or "") or None,
        "recomendacao": triagem.get("recomendacao"),
        "queries": depuracao.get("queries"),
        "rewritten_question": depuracao.get("rewritten_question"),
        "raw_llm_output": depuracao.get("raw_llm_output"),
        # Procedência (rodada 25 do João): quem respondeu, linha a linha. Uma
        # troca de provedor no meio da rodada aparece aqui.
        "used_topics": [f.get("topic") for f in fontes],
        "attendant_provider": atendente.get("provider"),
        "attendant_model": atendente.get("model"),
        "attendant_model_version": atendente.get("model_version"),
        "attendant_thinking": atendente.get("thinking"),
        "attendant_fallback_from": atendente.get("fallback_from"),
        "query_stage_calls": consulta.get("calls"),
    }


# ----------------------------------------------------------------------
# Ambiente
# ----------------------------------------------------------------------


def sha256_arquivo(caminho: Path) -> str:

    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def git_estado() -> dict:

    def executar(*argumentos):
        try:
            return subprocess.run(
                argumentos,
                cwd=RAIZ,
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout.strip()
        except Exception:
            return None

    return {
        "sha": executar("git", "rev-parse", "--short", "HEAD"),
        "dirty": bool(executar("git", "status", "--porcelain")),
    }


def _caminho_relativo(caminho: Path) -> str:
    """Relativo à raiz do repositório, com barra normal, quando der."""

    try:
        return caminho.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return caminho.resolve().as_posix()


def agora() -> str:

    return datetime.now(timezone.utc).astimezone().isoformat()


def conferir_base(
    impressao: dict,
    config_efetivo: dict | None = None,
    hash_esperado: str | None = None,
) -> None:
    """
    Recusa a rodada quando a base não é a que a medição precisa.

    Dois casos, os dois silenciosos até aqui (evidencias/backlog.md#b-38):

    1. Busca ligada e base vazia. A rodada iria até o fim e sairia como
       sucesso, mas o modelo não teria visto documento nenhum — seria um
       `llm_only` com rótulo de `naive_rag`. Base vazia é o estado padrão de
       um clone limpo (B-12).
    2. Base diferente da esperada. Desde a troca do chunking em 07/09, a
       mesma pasta de documentos gera uma base diferente (B-37), e quem
       compara com uma rodada citada precisa saber disso **antes** de gastar
       meia hora de GPU, não depois, no `compare`.

    Só `SystemExit`: erro de configuração não é dado.
    """

    base = impressao.get("vector_store") or {}

    if hash_esperado:
        hash_real = base.get("chunk_ids_sha256")

        if hash_real != hash_esperado:
            raise SystemExit(
                "A base vetorial não é a esperada.\n"
                f"  esperado: {hash_esperado}\n"
                f"  na API  : {hash_real}\n"
                "Compare com o `backend_fingerprint` da rodada que você "
                "quer reproduzir, ou rode sem --expect-base-hash se a "
                "intenção é medir a base atual."
            )

    if config_efetivo is None:
        return

    if not config_efetivo.get("retrieval_enabled"):
        return

    if base.get("chunk_count"):
        return

    raise SystemExit(
        "A busca está ligada, mas a base vetorial está vazia "
        f"(chunk_count={base.get('chunk_count')}).\n"
        "A rodada mediria o modelo sem contexto nenhum, com rótulo de RAG. "
        "Indexe antes:\n"
        "  docker compose exec backend python -m "
        "app.database.ingest_documents"
    )


# ----------------------------------------------------------------------
# Execução
# ----------------------------------------------------------------------


def executar_rodada(
    diretorio: Path,
    manifesto: dict,
    linhas: pd.DataFrame,
    cliente: ApiClient,
    repeticoes: int,
    base_seed: int | None,
    casos_livres: bool = False,
) -> None:

    caminho_previsoes = diretorio / "predictions.jsonl"

    opcoes_base = dict(manifesto["requested_options"])
    opcoes_base["include_debug"] = True

    registros_anteriores = ler_previsoes(caminho_previsoes)

    aprovadas = [
        registro
        for registro in registros_anteriores
        if registro.get("status") == "ok"
    ]

    ja_feitas = {
        (registro["row_id"], registro["repeat"]) for registro in aprovadas
    }

    # Uma rodada interrompida pode ter deixado linhas com erro, e uma
    # interrupção no meio da escrita pode ter deixado a última linha pela
    # metade. As duas serão refeitas, então o arquivo é reescrito apenas
    # com o que se aproveita — inclusive quando isso é nada.
    if registros_anteriores:
        escrever_atomico(
            caminho_previsoes,
            "".join(
                json.dumps(r, ensure_ascii=False) + "\n" for r in aprovadas
            ),
        )

        descartadas = len(registros_anteriores) - len(aprovadas)

        print(
            f"  retomando: {len(aprovadas)} linha(s) aproveitada(s)"
            + (f", {descartadas} a refazer" if descartadas else "")
        )

    total = len(linhas) * repeticoes
    feitas = len(ja_feitas)
    erros_seguidos = 0
    config_referencia = None

    for repeticao in range(repeticoes):

        # Com temperatura acima de zero, cada repetição precisa de uma seed
        # diferente para medir variação. Sem isso, a API usa a seed padrão e
        # as repetições seriam cópias da mesma execução.
        seed = None

        if base_seed is not None:
            seed = base_seed + repeticao

        for _, linha in linhas.iterrows():

            if casos_livres:
                row_id, relato, contexto = contexto_do_caso(
                    linha, repeticao, seed
                )
                if (row_id, repeticao) in ja_feitas:
                    continue
            else:
                row_id = int(linha.name)

                if (row_id, repeticao) in ja_feitas:
                    continue

                relato = build_relato(linha)

                contexto = {
                    "row_id": row_id,
                    "repeat": repeticao,
                    "seed_used": seed,
                    "animal": linha["AnimalName"],
                    "source": linha["Source"],
                    "n_symptoms": len(get_symptoms(linha)),
                    "symptoms": get_symptoms(linha),
                    "relato": relato,
                    "relato_sha1": hashlib.sha1(
                        relato.encode("utf-8")
                    ).hexdigest()[:12],
                    "expected": get_expected_label(linha["Dangerous"]),
                }

            opcoes = dict(opcoes_base)

            if seed is not None:
                opcoes["seed"] = seed

            registro = None

            for tentativa, espera in enumerate([0] + ESPERAS):

                if espera:
                    print(
                        f"    nova tentativa em {espera}s...",
                        file=sys.stderr,
                    )
                    time.sleep(espera)

                inicio = time.perf_counter()

                try:
                    resposta = cliente.classify(relato, opcoes)

                    registro = achatar(resposta, contexto)
                    registro["client_s"] = round(
                        time.perf_counter() - inicio, 3
                    )

                    config = resposta.get("config") or {}
                    comparavel = {
                        chave: valor
                        for chave, valor in config.items()
                        if chave != "seed"
                    }

                    # Um backend reiniciado com outra configuração no meio
                    # da rodada produziria linhas incomparáveis sem que
                    # ninguém notasse.
                    if config_referencia is None:
                        config_referencia = comparavel
                        manifesto["effective_config"] = config
                    elif comparavel != config_referencia:
                        raise SystemExit(
                            "A configuração efetiva mudou no meio da "
                            "rodada. O backend foi reiniciado? "
                            f"Antes: {config_referencia}\n"
                            f"Agora: {comparavel}"
                        )

                    erros_seguidos = 0
                    break

                except requests.HTTPError as erro:
                    codigo = erro.response.status_code

                    try:
                        corpo_do_erro = erro.response.json()
                    except Exception:
                        corpo_do_erro = {}

                    # A cota do dia acabou: a rodada para aqui, e não com
                    # metade das linhas em erro (rodada 26 do João).
                    if (corpo_do_erro or {}).get("code") == "quota_exhausted":
                        raise SystemExit(
                            "A cota diária do atendente acabou "
                            f"({(corpo_do_erro.get('details') or {}).get('provider')}). "
                            "O que foi feito está gravado; continue com "
                            f"--resume {diretorio} depois da virada da cota "
                            "ou com outra chave na API."
                        )

                    if codigo in (400, 422):
                        raise SystemExit(
                            f"A API recusou a configuração (HTTP {codigo}): "
                            f"{erro.response.text}\n"
                            "Erro de configuração não é dado: corrija as "
                            "opções e rode de novo."
                        )

                    mensagem = f"HTTP {codigo}"

                except Exception as erro:
                    mensagem = f"{type(erro).__name__}: {erro}"

                if tentativa == len(ESPERAS):
                    registro = {
                        **contexto,
                        "status": "error",
                        "error": mensagem,
                        "predicted": None,
                        "client_s": round(time.perf_counter() - inicio, 3),
                    }
                    erros_seguidos += 1

            anexar_linha(caminho_previsoes, registro)

            feitas += 1
            marca = registro.get("predicted") or registro.get("status")

            print(
                f"  [{feitas:>3}/{total}] linha {row_id!s:>3} "
                f"esperado {contexto['expected']:<14} -> {marca}"
            )

            if erros_seguidos >= MAX_ERROS_SEGUIDOS:
                raise SystemExit(
                    f"{MAX_ERROS_SEGUIDOS} linhas seguidas falharam. "
                    "A API está de pé? Use --resume para continuar."
                )


def finalizar(diretorio: Path, manifesto: dict) -> dict:

    registros = ler_previsoes(diretorio / "predictions.jsonl")
    df = pd.DataFrame(registros)

    metricas = compute_metrics(df)

    escrever_atomico(
        diretorio / "metrics.json",
        json.dumps(metricas, ensure_ascii=False, indent=2, default=str),
    )

    # A versão em CSV é para abrir em planilha; sai sem os textos longos,
    # que têm quebras de linha e quebrariam o formato.
    colunas_longas = [
        "raw_llm_output",
        "justificativa",
        "recomendacao",
        "raciocinio",
    ]
    df.drop(
        columns=[c for c in colunas_longas if c in df.columns]
    ).to_csv(diretorio / "predictions.csv", index=False, encoding="utf-8")

    # Linhas respondidas por troca de atendente (permitida pela
    # configuração). Numa rodada de réplica, tem de ser zero.
    manifesto["attendant_fallback_lines"] = sum(
        1 for registro in registros if registro.get("attendant_fallback_from")
    )
    manifesto["finished_at"] = agora()
    manifesto["status"] = "done"

    escrever_atomico(
        diretorio / "manifest.json",
        json.dumps(manifesto, ensure_ascii=False, indent=2, default=str),
    )

    escrever_relatorio(diretorio, manifesto, metricas)

    return metricas


def main(argv=None) -> None:

    parser = argparse.ArgumentParser(
        description="Roda o conjunto de avaliação contra a API de triagem."
    )
    parser.add_argument("--preset", default="llm_only")
    parser.add_argument("--set", dest="ajustes", action="append", default=[])
    parser.add_argument(
        "--subset", choices=["smoke", "balanced", "full"], default="full"
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument(
        "--base-seed",
        type=int,
        help=(
            "Seed inicial. Use com temperatura acima de zero para que cada "
            "repetição meça variação em vez de repetir a mesma execução."
        ),
    )
    parser.add_argument("--name", default="rodada")
    parser.add_argument(
        "--expect-base-hash",
        help=(
            "Aborta se a base vetorial não for esta (o "
            "`chunk_ids_sha256` do fingerprint). Opcional, para não "
            "atrapalhar um smoke; use em toda rodada que for citada numa "
            "evidência."
        ),
    )
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=1500)
    parser.add_argument(
        "--cases",
        type=Path,
        help=(
            "Roda um lote no formato da prova (colunas id, text, "
            "expected_class) em vez do conjunto antigo. Sem esta opção, o "
            "runner faz exatamente o que fazia."
        ),
    )
    parser.add_argument(
        "--split",
        help="Com --cases: só as linhas deste split. Confere o congelamento, se houver.",
    )

    argumentos = parser.parse_args(argv)

    cliente = ApiClient(argumentos.api_url, argumentos.timeout)
    casos_livres = bool(argumentos.cases)

    if argumentos.split and not argumentos.cases:
        parser.error("--split só vale com --cases.")

    if argumentos.resume:
        diretorio = argumentos.resume
        manifesto = json.loads(
            (diretorio / "manifest.json").read_text(encoding="utf-8")
        )

        casos_livres = "cases" in manifesto
        if casos_livres:
            caminho_casos = RAIZ / manifesto["cases"]["path"]
            if sha256_arquivo(caminho_casos) != manifesto["cases"]["sha256"]:
                raise SystemExit(
                    "O arquivo de casos mudou desde que esta rodada começou. "
                    "Retomar misturaria dados diferentes na mesma medição."
                )
            linhas = carregar_casos(
                caminho_casos, manifesto["cases"].get("split")
            ).loc[manifesto["row_ids"]]
        else:
            if sha256_arquivo(DATASET) != manifesto["dataset"]["sha256"]:
                raise SystemExit(
                    "O dataset mudou desde que esta rodada começou. "
                    "Retomar misturaria dados diferentes na mesma medição."
                )

            df = carregar_dataset()
            linhas = df.loc[manifesto["row_ids"]]

        manifesto.setdefault("resumed_at", []).append(agora())
        repeticoes = manifesto["repeats"]
        base_seed = manifesto.get("base_seed")

        print(f"Retomando {diretorio.name}")

    else:
        opcoes = montar_opcoes(argumentos.preset, argumentos.ajustes)

        if casos_livres:
            caminho_casos = argumentos.cases.resolve()
            linhas = carregar_casos(caminho_casos, argumentos.split)
            if argumentos.limit:
                linhas = linhas.head(argumentos.limit)
        else:
            df = carregar_dataset()
            linhas = selecionar(df, argumentos.subset, argumentos.limit)

        if not cliente.health():
            raise SystemExit(
                f"A API não respondeu em {argumentos.api_url}. "
                "Suba com: docker compose up -d"
            )

        impressao = cliente.fingerprint()

        # O hash é conferido antes do aquecimento: é barato e evita pagar o
        # carregamento do modelo para depois descobrir que a base é outra.
        conferir_base(impressao, hash_esperado=argumentos.expect_base_hash)

        # Aquecimento: a primeira chamada paga o carregamento do modelo, e
        # também é aqui que uma configuração inválida é recusada, antes de
        # gastar meia hora de rodada.
        print("Aquecendo o modelo e conferindo a configuração...")

        inicio = time.perf_counter()

        try:
            resposta_aquecimento = cliente.classify(
                (
                    str(linhas.iloc[0]["text"])
                    if casos_livres
                    else build_relato(linhas.iloc[0])
                ),
                {**opcoes, "include_debug": True},
            )
        except requests.HTTPError as erro:
            if erro.response.status_code in (400, 422):
                raise SystemExit(
                    f"A API recusou a configuração "
                    f"(HTTP {erro.response.status_code}): "
                    f"{erro.response.text}"
                )
            raise

        aquecimento = round(time.perf_counter() - inicio, 2)
        print(f"  pronto em {aquecimento}s")

        # A busca é conferida contra o config **efetivo**, e não contra o
        # pedido: o modo legado desliga a recuperação no servidor, e ali
        # base vazia não é problema nenhum.
        conferir_base(
            impressao,
            config_efetivo=resposta_aquecimento.get("config") or {},
        )

        carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
        diretorio = DIRETORIO_RODADAS / f"{carimbo}_{argumentos.name}"
        diretorio.mkdir(parents=True, exist_ok=True)

        manifesto = {
            "run_id": diretorio.name,
            "name": argumentos.name,
            "status": "running",
            "started_at": agora(),
            "hostname": socket.gethostname(),
            "python": platform.python_version(),
            "git": git_estado(),
            **(
                {
                    "cases": {
                        "path": _caminho_relativo(caminho_casos),
                        "sha256": sha256_arquivo(caminho_casos),
                        "split": argumentos.split,
                        "n": len(linhas),
                    },
                    "subset": None,
                    "limit": argumentos.limit,
                    "row_ids": [str(i) for i in linhas.index],
                    "label_distribution": linhas["expected_class"]
                    .value_counts()
                    .to_dict(),
                }
                if casos_livres
                else {
                    "dataset": {
                        "path": str(DATASET.relative_to(RAIZ)),
                        "sha256": sha256_arquivo(DATASET),
                    },
                    "subset": argumentos.subset,
                    "limit": argumentos.limit,
                    "row_ids": [int(i) for i in linhas.index],
                    "label_distribution": linhas["Dangerous"]
                    .value_counts()
                    .to_dict(),
                }
            ),
            "preset": argumentos.preset,
            "set": argumentos.ajustes,
            "requested_options": opcoes,
            "effective_config": None,
            "repeats": argumentos.repeat,
            "base_seed": argumentos.base_seed,
            "relato_lang": "pt" if casos_livres else "en",
            "api_url": argumentos.api_url,
            "presets_sha256": sha256_arquivo(PRESETS),
            "warmup_seconds": aquecimento,
            "backend_fingerprint": impressao,
            "expected_base_hash": argumentos.expect_base_hash,
        }

        escrever_atomico(
            diretorio / "manifest.json",
            json.dumps(manifesto, ensure_ascii=False, indent=2, default=str),
        )

        repeticoes = argumentos.repeat
        base_seed = argumentos.base_seed

        print(f"\nRodada {diretorio.name}")
        print(f"  preset  : {argumentos.preset}")
        print(f"  opções  : {opcoes}")
        print(f"  linhas  : {len(linhas)} x {repeticoes} repetição(ões)\n")

    executar_rodada(
        diretorio, manifesto, linhas, cliente, repeticoes, base_seed,
        casos_livres=casos_livres,
    )

    metricas = finalizar(diretorio, manifesto)

    classificacao = metricas["classification"]

    print("\nConcluída.")
    print(f"  acurácia balanceada : {classificacao['balanced_accuracy']}")
    print(f"  acurácia estrita    : {classificacao['accuracy_strict']}")
    print(f"  falsos não urgentes : {classificacao['false_non_urgent']}")
    print(f"  falsos urgentes     : {classificacao['false_urgent']}")
    print(f"\n  {diretorio}")


if __name__ == "__main__":
    main()
