"""
Testes do módulo de WER/CER do benchmark de voz.

Casos pequenos, conferíveis à mão: é o cálculo que sustenta o número de
qualidade da transcrição citado na evidência.
"""

from wer_metrics import agregar, cer, normalizar, wer


def test_normalizacao_ignora_caixa_e_pontuacao():

    assert normalizar("  Chocolate, AGORA! ") == "chocolate agora"


def test_normalizacao_preserva_acentos():

    assert normalizar("cão órfão") == "cão órfão"


def test_transcricao_identica_tem_wer_zero():

    resultado = wer("meu cão comeu chocolate", "meu cão comeu chocolate")

    assert resultado["error_rate"] == 0.0
    assert resultado["hits"] == 4


def test_uma_substituicao_em_cinco_palavras():

    resultado = wer(
        "meu cão está com dor",
        "meu gato está com dor",
    )

    assert resultado["substitutions"] == 1
    assert resultado["deletions"] == 0
    assert resultado["insertions"] == 0
    assert resultado["error_rate"] == 0.2


def test_remocao_e_insercao_sao_contadas():

    faltou = wer("meu cão comeu chocolate amargo", "meu cão comeu chocolate")
    assert faltou["deletions"] == 1
    assert faltou["error_rate"] == 0.2

    sobrou = wer("meu cão comeu chocolate", "meu cão comeu muito chocolate")
    assert sobrou["insertions"] == 1
    assert sobrou["error_rate"] == 0.25


def test_pontuacao_nao_conta_como_erro():

    resultado = wer("a gata não urina", "A gata não urina!")

    assert resultado["error_rate"] == 0.0


def test_hipotese_vazia_erra_a_referencia_inteira():

    resultado = wer("meu cão comeu chocolate", "")

    assert resultado["deletions"] == 4
    assert resultado["error_rate"] == 1.0


def test_cer_conta_caracteres():

    resultado = cer("gato", "jato")

    assert resultado["substitutions"] == 1
    assert resultado["n_ref"] == 4
    assert resultado["error_rate"] == 0.25


def test_agregado_soma_erros_nao_media_das_taxas():
    """
    Frase curta com um erro não pode pesar o mesmo que uma longa sem erro:
    o agregado é (soma de erros) / (soma de palavras), não a média.
    """

    pares = [
        ("curta", "um dois", "um três"),          # 1 erro em 2 palavras
        ("longa", "a b c d e f g h", "a b c d e f g h"),  # 0 em 8
    ]

    resultado = agregar(pares)

    # média das taxas seria (0,5 + 0,0) / 2 = 0,25
    assert resultado["wer"] == 1 / 10
    assert resultado["ref_words"] == 10
    assert resultado["substitutions"] == 1
