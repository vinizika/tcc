"""
Gera os áudios do benchmark de voz a partir de `references.csv`, com edge-tts.

Roda **uma vez** e precisa de rede: usa as vozes neurais PT-BR da Microsoft
(Francisca, Antônio, Thalita). Os MP3 gerados são versionados em
`scripts/voice_benchmark/audio/`, então medir o WER depois (`run_voice_benchmark.py`)
não depende de rede nem de o TTS ser reproduzível bit a bit.

Os áudios são fala sintética limpa e bem articulada — o WER medido sobre eles
é um limite otimista, não a condição de um tutor real ao telefone. A
motivação e a limitação estão em evidencias/backlog.md#b-13.

Uso:
    pip install edge-tts
    python scripts/generate_voice_benchmark.py
"""

import asyncio
import csv
from pathlib import Path

import edge_tts


BENCH = Path(__file__).resolve().parent / "voice_benchmark"
REFERENCIAS = BENCH / "references.csv"
AUDIO = BENCH / "audio"


async def _sintetizar(texto: str, voz: str, rate: str, destino: Path) -> None:

    comunicacao = edge_tts.Communicate(texto, voz, rate=rate)

    await comunicacao.save(str(destino))


async def main() -> None:

    AUDIO.mkdir(parents=True, exist_ok=True)

    with open(REFERENCIAS, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    for linha in linhas:

        destino = AUDIO / f"{linha['id']}.mp3"

        print(
            f"{linha['id']}  {linha['voice']:<32}  {linha['rate']:>5}  "
            f"{linha['text'][:50]}…"
        )

        await _sintetizar(
            linha["text"],
            linha["voice"],
            linha["rate"],
            destino,
        )

    print(f"\n{len(linhas)} áudios gravados em {AUDIO}")


if __name__ == "__main__":
    asyncio.run(main())
