"""
WER e CER para o benchmark de transcrição de voz.

Módulo puro: recebe pares (referência, hipótese) e devolve números. Sem rede
nem configuração, então roda offline e é fácil de testar.

WER (*word error rate*) = (substituições + remoções + inserções) / número de
palavras da referência, contado pela distância de edição entre as duas
sequências de palavras. CER é o mesmo no nível de caractere. Quanto menor,
melhor; pode passar de 1 quando a hipótese é maior que a referência.

A normalização — minúsculas, sem pontuação, espaços colapsados — é aplicada
antes de contar: "Chocolate," e "chocolate" não são um erro de transcrição.
Acentos são preservados de propósito: em português eles distinguem palavras
e o Whisper os produz.
"""

import re
import unicodedata


_PONTUACAO = re.compile(r"[^\w\s]", flags=re.UNICODE)
_ESPACOS = re.compile(r"\s+")


def normalizar(texto: str) -> str:

    texto = unicodedata.normalize("NFC", texto or "")
    texto = texto.casefold()
    texto = _PONTUACAO.sub(" ", texto)
    texto = _ESPACOS.sub(" ", texto)

    return texto.strip()


def _contar_operacoes(referencia: list, hipotese: list) -> tuple[int, int, int]:
    """
    Distância de edição de Levenshtein, devolvendo (substituições, remoções,
    inserções). Programação dinâmica O(n·m); as frases do benchmark são
    curtas, então o custo não importa.

    Cada célula guarda a tripla acumulada de operações. Em empate de custo
    total, a ordem substituição → remoção → inserção decide — arbitrário,
    mas determinístico.
    """

    n, m = len(referencia), len(hipotese)

    anterior = [(0, 0, j) for j in range(m + 1)]

    for i in range(1, n + 1):

        atual = [(0, i, 0)] + [(0, 0, 0)] * m

        for j in range(1, m + 1):

            if referencia[i - 1] == hipotese[j - 1]:
                atual[j] = anterior[j - 1]
                continue

            s_sub, d_sub, i_sub = anterior[j - 1]
            s_del, d_del, i_del = anterior[j]
            s_ins, d_ins, i_ins = atual[j - 1]

            candidatos = (
                (s_sub + 1, d_sub, i_sub),
                (s_del, d_del + 1, i_del),
                (s_ins, d_ins, i_ins + 1),
            )

            atual[j] = min(candidatos, key=lambda t: t[0] + t[1] + t[2])

        anterior = atual

    return anterior[m]


def _taxa(referencia: list, hipotese: list) -> dict:

    substituicoes, remocoes, insercoes = _contar_operacoes(
        referencia, hipotese
    )

    n = len(referencia)
    erros = substituicoes + remocoes + insercoes

    return {
        "n_ref": n,
        "substitutions": substituicoes,
        "deletions": remocoes,
        "insertions": insercoes,
        "hits": n - substituicoes - remocoes,
        "error_rate": (
            erros / n
            if n
            else (0.0 if not hipotese else float(len(hipotese)))
        ),
    }


def wer(referencia: str, hipotese: str) -> dict:

    return _taxa(
        normalizar(referencia).split(),
        normalizar(hipotese).split(),
    )


def cer(referencia: str, hipotese: str) -> dict:

    return _taxa(
        list(normalizar(referencia).replace(" ", "")),
        list(normalizar(hipotese).replace(" ", "")),
    )


def agregar(pares) -> dict:
    """
    Números do conjunto todo.

    O WER agregado é a soma de erros dividida pela soma de palavras de
    referência — não a média das taxas por frase, em que uma frase curta com
    um erro pesaria o mesmo que uma longa sem nenhum.
    """

    por_item = []

    total_s = total_d = total_i = total_n = 0
    total_sc = total_dc = total_ic = total_nc = 0

    for identificador, referencia, hipotese in pares:

        m = wer(referencia, hipotese)
        c = cer(referencia, hipotese)

        por_item.append(
            {"id": identificador, "wer": m, "cer": c}
        )

        total_s += m["substitutions"]
        total_d += m["deletions"]
        total_i += m["insertions"]
        total_n += m["n_ref"]

        total_sc += c["substitutions"]
        total_dc += c["deletions"]
        total_ic += c["insertions"]
        total_nc += c["n_ref"]

    return {
        "n_items": len(por_item),
        "wer": (total_s + total_d + total_i) / total_n if total_n else None,
        "cer": (
            (total_sc + total_dc + total_ic) / total_nc if total_nc else None
        ),
        "substitutions": total_s,
        "deletions": total_d,
        "insertions": total_i,
        "ref_words": total_n,
        "per_item": por_item,
    }
