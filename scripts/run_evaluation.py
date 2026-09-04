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
    "context_top_k",
    "context_min_score",
    "rewritten_hint_enabled",
    "cot_enabled",
    "self_refine_enabled",
    "prompt_version",
    "structured_output_mode",
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
        "recomendacao": triagem.get("recomendacao"),
        "queries": depuracao.get("queries"),
        "rewritten_question": depuracao.get("rewritten_question"),
        "raw_llm_output": depuracao.get("raw_llm_output"),
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


def agora() -> str:

    return datetime.now(timezone.utc).astimezone().isoformat()


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
                f"  [{feitas:>3}/{total}] linha {row_id:>3} "
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
    colunas_longas = ["raw_llm_output", "justificativa", "recomendacao"]
    df.drop(
        columns=[c for c in colunas_longas if c in df.columns]
    ).to_csv(diretorio / "predictions.csv", index=False, encoding="utf-8")

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
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=1500)

    argumentos = parser.parse_args(argv)

    cliente = ApiClient(argumentos.api_url, argumentos.timeout)

    if argumentos.resume:
        diretorio = argumentos.resume
        manifesto = json.loads(
            (diretorio / "manifest.json").read_text(encoding="utf-8")
        )

        if sha256_arquivo(DATASET) != manifesto["dataset"]["sha256"]:
            raise SystemExit(
                "O dataset mudou desde que esta rodada começou. "
                "Retomar misturaria dados diferentes na mesma medição."
            )

        manifesto.setdefault("resumed_at", []).append(agora())

        df = carregar_dataset()
        linhas = df.loc[manifesto["row_ids"]]
        repeticoes = manifesto["repeats"]
        base_seed = manifesto.get("base_seed")

        print(f"Retomando {diretorio.name}")

    else:
        opcoes = montar_opcoes(argumentos.preset, argumentos.ajustes)

        df = carregar_dataset()
        linhas = selecionar(df, argumentos.subset, argumentos.limit)

        if not cliente.health():
            raise SystemExit(
                f"A API não respondeu em {argumentos.api_url}. "
                "Suba com: docker compose up -d"
            )

        # Aquecimento: a primeira chamada paga o carregamento do modelo, e
        # também é aqui que uma configuração inválida é recusada, antes de
        # gastar meia hora de rodada.
        print("Aquecendo o modelo e conferindo a configuração...")

        inicio = time.perf_counter()

        try:
            cliente.classify(
                build_relato(linhas.iloc[0]),
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
            "preset": argumentos.preset,
            "set": argumentos.ajustes,
            "requested_options": opcoes,
            "effective_config": None,
            "repeats": argumentos.repeat,
            "base_seed": argumentos.base_seed,
            "relato_lang": "en",
            "api_url": argumentos.api_url,
            "presets_sha256": sha256_arquivo(PRESETS),
            "warmup_seconds": aquecimento,
            "backend_fingerprint": cliente.fingerprint(),
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
        diretorio, manifesto, linhas, cliente, repeticoes, base_seed
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
