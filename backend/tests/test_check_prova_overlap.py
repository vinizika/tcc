"""
A regra 4 da muralha (docs/plano-base-e-prova.md) pede um passo automático
que confira sobreposição de texto entre os casos da prova e os documentos
da base, antes de congelar o lote de teste.
"""

from app.database.check_prova_overlap import n_gramas, normaliza_palavras


def test_normaliza_palavras_ignora_pontuacao_e_maiusculas():

    palavras = normaliza_palavras("Meu cachorro comeu chocolate, e agora?")

    assert palavras == [
        "meu", "cachorro", "comeu", "chocolate", "e", "agora",
    ]


def test_n_gramas_detecta_sequencia_repetida():

    base = normaliza_palavras(
        "o animal apresenta quadro clinico compativel com intoxicacao aguda"
    )
    caso = normaliza_palavras(
        "meu cachorro apresenta quadro clinico compativel com dor"
    )

    colisao = n_gramas(base, 5) & n_gramas(caso, 5)

    assert colisao == {("apresenta", "quadro", "clinico", "compativel", "com")}


def test_n_gramas_nao_acusa_frases_diferentes():

    base = normaliza_palavras("protocolo de tratamento para intoxicacao por chocolate em caes")
    caso = normaliza_palavras("meu cachorro comeu chocolate e esta tremendo muito")

    colisao = n_gramas(base, 6) & n_gramas(caso, 6)

    assert colisao == set()
