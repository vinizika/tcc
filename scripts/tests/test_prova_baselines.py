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


def test_cv_por_assunto_tira_o_acerto_que_vem_de_assunto_repetido():
    """
    Cada assunto tem uma palavra própria e uma classe só: com o assunto
    repetido entre treino e teste, a palavra entrega a classe; separando
    por assunto, o modelo nunca viu a palavra e só resta o chute.
    """
    from prova_baselines import naive_bayes_cv_repetido

    casos = []
    for indice in range(10):
        classe = "EMERGENCIA" if indice % 2 == 0 else "NAO_EMERGENCIA"
        for repeticao in range(4):
            casos.append({"id": f"t{indice}r{repeticao}", "text": f"palavra{indice} relato",
                          "expected_class": classe, "topic": f"t{indice}"})

    aleatoria = naive_bayes_cv_repetido(casos, k=4, repeticoes=3)
    por_assunto = naive_bayes_cv_repetido(casos, chave_grupo="topic", k=5, repeticoes=3)

    assert aleatoria["acuracia"] == 1.0
    assert por_assunto["acuracia"] <= 0.6
    assert por_assunto["n"] == 40


def test_treino_teste_mede_so_no_conjunto_de_teste():
    from prova_baselines import naive_bayes_treino_teste

    treino = [caso("e1", "sangue convulsao", "EMERGENCIA"), caso("n1", "brincando comendo", "NAO_EMERGENCIA")]
    teste = [caso("e2", "convulsao forte", "EMERGENCIA"), caso("n2", "comendo bem", "NAO_EMERGENCIA"),
             {"id": "i1", "text": "nao sei", "expected_class": "INCERTO"}]

    resultado = naive_bayes_treino_teste(treino, teste)

    assert resultado == {"nome": "naive_bayes_treino_teste", "acuracia": 1.0, "n": 2}


def test_regra_mas_conta_a_palavra_inteira_e_o_chute():
    from prova_baselines import regra_mas

    casos = [
        caso("e1", "ele caiu mas levantou", "EMERGENCIA"),
        caso("e2", "ele desmaiou", "EMERGENCIA"),
        caso("e3", "ele esta mastigando pedra", "EMERGENCIA"),
        caso("n1", "espirrou mas esta bem", "NAO_EMERGENCIA"),
    ]

    resultado = regra_mas(casos)

    # e2 e e3 (sem "mas": "mastigando" não conta) e n1 acertam; e1 erra.
    assert resultado["acuracia"] == 0.75
    assert resultado["chute_classe_mais_comum"] == 0.75
