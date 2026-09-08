"""
Mede o WER do Whisper sobre o benchmark de voz.

Envia cada áudio de `scripts/voice_benchmark/audio/` para `POST /voice/` (a
API precisa estar de pé) e compara a transcrição com o texto de
`references.csv`. Grava `data/voice_benchmark/predictions.csv`,
`report.md` e `summary.json`.

O número que sai daqui é o WER do Whisper sobre **fala sintética limpa** —
um limite otimista. Ver evidencias/backlog.md#b-13.

Uso:
    docker compose up -d
    python scripts/run_voice_benchmark.py
    python scripts/run_voice_benchmark.py --base-url http://localhost:8000
"""

import argparse
import csv
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from wer_metrics import agregar


RAIZ = Path(__file__).resolve().parents[1]
BENCH = RAIZ / "scripts" / "voice_benchmark"
AUDIO = BENCH / "audio"
SAIDA = RAIZ / "data" / "voice_benchmark"


def _git_sha() -> str:

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=RAIZ,
            text=True,
        ).strip()
    except Exception:
        return "desconhecido"


def _fingerprint(base_url: str) -> dict:

    try:
        return requests.get(f"{base_url}/health/fingerprint", timeout=15).json()
    except Exception as erro:
        return {"erro": str(erro)}


def _transcrever(base_url: str, caminho: Path, timeout: float) -> dict:

    with open(caminho, "rb") as arquivo:
        resposta = requests.post(
            f"{base_url}/voice/",
            files={"audio": (caminho.name, arquivo, "audio/mpeg")},
            timeout=timeout,
        )

    resposta.raise_for_status()

    return resposta.json()


def _tabela_por_item(resumo: dict, linhas: list) -> str:

    por_id = {item["id"]: item for item in resumo["per_item"]}
    saida = [
        "| id | classe | voz | WER | S/D/I | ref → hipótese |",
        "|---|---|---|---:|---|---|",
    ]

    for linha in linhas:
        item = por_id[linha["id"]]
        m = item["wer"]
        voz = linha["voice"].replace("pt-BR-", "").replace("Neural", "")
        saida.append(
            f"| {linha['id']} | {linha['expected_class']} | {voz} "
            f"| {m['error_rate']:.2f} "
            f"| {m['substitutions']}/{m['deletions']}/{m['insertions']} "
            f"| {linha['reference']}<br>→ _{linha['hypothesis']}_ |"
        )

    return "\n".join(saida)


def _relatorio(resumo: dict, linhas: list, manifesto: dict) -> str:

    wer = resumo["wer"]
    cer = resumo["cer"]

    return f"""# Benchmark de transcrição de voz (Whisper)

**Gerado em:** {manifesto['gerado_em']} · **commit:** `{manifesto['git_sha']}`
· **modelo:** {manifesto['whisper_model']}

Fala **sintética** (edge-tts, vozes neurais PT-BR) a partir de
`scripts/voice_benchmark/references.csv`. É um limite otimista: áudio limpo e
bem articulado, não um tutor real ao telefone (evidencias/backlog.md#b-13).

## Resultado

| Métrica | Valor |
|---|---:|
| **WER agregado** | **{wer:.3f}** ({wer * 100:.1f}%) |
| CER agregado | {cer:.3f} ({cer * 100:.1f}%) |
| Áudios | {resumo['n_items']} |
| Palavras de referência | {resumo['ref_words']} |
| Substituições / remoções / inserções | {resumo['substitutions']} / {resumo['deletions']} / {resumo['insertions']} |
| Tempo mediano por requisição | {manifesto['request_s_median']:.1f}s |
| Idioma detectado ≠ pt | {manifesto['language_not_pt']} |

WER agregado = (S + D + I) ÷ palavras de referência, sobre todos os áudios.

## Por item

{_tabela_por_item(resumo, linhas)}
"""


def main(argv=None) -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=float, default=600)
    args = parser.parse_args(argv)

    with open(BENCH / "references.csv", encoding="utf-8") as arquivo:
        referencias = list(csv.DictReader(arquivo))

    if not AUDIO.exists() or not any(AUDIO.glob("*.mp3")):
        raise SystemExit(
            f"Sem áudios em {AUDIO}. Rode primeiro:\n"
            f"    python scripts/generate_voice_benchmark.py"
        )

    SAIDA.mkdir(parents=True, exist_ok=True)

    linhas = []
    pares = []
    tempos = []

    for referencia in referencias:

        caminho = AUDIO / f"{referencia['id']}.mp3"

        if not caminho.exists():
            print(f"faltando: {caminho.name} — pulando")
            continue

        inicio = time.perf_counter()
        dados = _transcrever(args.base_url, caminho, args.timeout)
        segundos = time.perf_counter() - inicio
        tempos.append(segundos)

        hipotese = dados.get("transcription", "")

        linhas.append(
            {
                "id": referencia["id"],
                "expected_class": referencia["expected_class"],
                "voice": referencia["voice"],
                "rate": referencia["rate"],
                "reference": referencia["text"],
                "hypothesis": hipotese,
                "language": dados.get("language"),
                "duration_s": dados.get("duration"),
                "request_s": round(segundos, 1),
            }
        )
        pares.append((referencia["id"], referencia["text"], hipotese))

        print(f"{referencia['id']}  {segundos:6.1f}s  {hipotese}")

    resumo = agregar(pares)

    tempos_ordenados = sorted(tempos)
    mediana = (
        tempos_ordenados[len(tempos_ordenados) // 2]
        if tempos_ordenados
        else 0.0
    )

    fingerprint = _fingerprint(args.base_url)

    manifesto = {
        "gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "git_sha": _git_sha(),
        "base_url": args.base_url,
        "fingerprint": fingerprint,
        "whisper_model": fingerprint.get("defaults", {}).get(
            "whisper_model_size", "small"
        ),
        "request_s_median": round(mediana, 1),
        "language_not_pt": sum(
            1 for linha in linhas if (linha["language"] or "pt") != "pt"
        ),
    }

    (SAIDA / "summary.json").write_text(
        json.dumps(
            {"resumo": {k: v for k, v in resumo.items() if k != "per_item"},
             "manifesto": manifesto},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    with open(SAIDA / "predictions.csv", "w", newline="", encoding="utf-8") as arquivo:
        campos = list(linhas[0].keys()) + ["wer"]
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        por_id = {item["id"]: item for item in resumo["per_item"]}
        for linha in linhas:
            linha = dict(linha)
            linha["wer"] = round(por_id[linha["id"]]["wer"]["error_rate"], 3)
            escritor.writerow(linha)

    (SAIDA / "report.md").write_text(
        _relatorio(resumo, linhas, manifesto), encoding="utf-8"
    )

    print(
        f"\nWER agregado: {resumo['wer']:.3f}  "
        f"CER: {resumo['cer']:.3f}  "
        f"({resumo['n_items']} áudios)\n"
        f"Relatório: {SAIDA / 'report.md'}"
    )


if __name__ == "__main__":
    main()
