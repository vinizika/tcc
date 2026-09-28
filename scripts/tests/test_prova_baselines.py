"""
Os baselines triviais precisam continuar batendo com um resultado
calculável à mão — é isso que garante que a validação cruzada está
particionando e agregando direito, não só "rodando sem erro".
"""

from prova_baselines import (
    baseline_comprimento_cv,
    baseline_palavra_de_alarme,
    baseline_saco_de_palavras_cv,
    compute_baselines,
)


def caso(id_, texto, classe):
    return {"id": id_, "text": texto, "expected_class": classe}


def test_palavra_de_alarme_acerta_quando_o_vocabulario_e_limpo():

    casos = [
        caso("e1", "meu cachorro esta sangrando muito", "EMERGENCIA"),
        caso("e2", "meu gato desmaiou agora", "EMERGENCIA"),
        caso("n1", "meu cachorro esta comendo bem", "NAO_EMERGENCIA"),
        caso("n2", "meu gato esta brincando normal", "NAO_EMERGENCIA"),
    ]

    resultado = baseline_palavra_de_alarme(casos)

    assert resultado["n"] == 4
    assert resultado["acuracia"] == 1.0


def test_palavra_de_alarme_ignora_casos_incerto():

    casos = [
        caso("e1", "meu cachorro esta sangrando muito", "EMERGENCIA"),
        {"id": "i1", "text": "nao sei o que ele tem", "expected_class": "INCERTO"},
    ]

    resultado = baseline_palavra_de_alarme(casos)

    assert resultado["n"] == 1


def test_comprimento_cv_separa_quando_o_tamanho_e_o_unico_sinal():

    # Emergencia sempre com relatos longos; leve sempre curtos. Um limiar
    # de comprimento resolve isso perfeitamente, em qualquer dobra.
    casos = [
        caso(f"e{i}", "palavra " * 20, "EMERGENCIA") for i in range(10)
    ] + [
        caso(f"n{i}", "palavra " * 3, "NAO_EMERGENCIA") for i in range(10)
    ]

    resultado = baseline_comprimento_cv(casos, k=5)

    assert resultado["acuracia"] == 1.0
    assert resultado["n"] == 20


def test_saco_de_palavras_separa_vocabulario_disjunto():

    # Vocabulario que nao se repete entre as classes: o Naive Bayes deveria
    # separar perfeitamente, em qualquer dobra.
    casos = [
        caso(f"e{i}", "convulsao sangue veneno grave", "EMERGENCIA")
        for i in range(10)
    ] + [
        caso(f"n{i}", "brincando comendo normal tranquilo", "NAO_EMERGENCIA")
        for i in range(10)
    ]

    resultado = baseline_saco_de_palavras_cv(casos, k=5)

    assert resultado["acuracia"] == 1.0


def test_compute_baselines_devolve_os_tres():

    casos = [
        caso("e1", "convulsao e sangue muito grave", "EMERGENCIA"),
        caso("e2", "meu cachorro desmaiou de repente", "EMERGENCIA"),
        caso("n1", "comendo e brincando normal", "NAO_EMERGENCIA"),
        caso("n2", "tudo tranquilo por aqui hoje", "NAO_EMERGENCIA"),
    ]

    resultado = compute_baselines(casos, k=2)

    assert set(resultado) == {
        "palavra_de_alarme",
        "comprimento_do_relato",
        "saco_de_palavras",
    }
    for baseline in resultado.values():
        assert baseline["n"] == 4
