"""
Testes da régua de recuperação.

Os valores de referência são calculáveis à mão, e é isso que os torna
úteis: se uma fórmula for trocada por outra parecida, o número muda e o
teste avisa.
"""

from retrieval_metrics import (
    avaliar_caso,
    compute_retrieval_metrics,
    posicao_do_acerto,
)


def caso(id_, topicos="", motivo=""):
    return {
        "id": id_,
        "expected_topics": topicos,
        "expected_none_reason": motivo,
    }


def recuperados(*pares):
    """`pares` são (topic, score), na ordem em que a busca devolveu."""
    return [{"topic": t, "score": s} for t, s in pares]


# ----------------------------------------------------------------------
# Posição
# ----------------------------------------------------------------------


def test_posicao_e_um_quando_o_certo_vem_no_topo():

    assert posicao_do_acerto(["chocolate", "trauma"], ["chocolate"]) == 1


def test_posicao_conta_a_partir_de_um():
    """
    Um por cento de diferença aqui vira metade no recíproco: posição 1 vale
    1,0 e posição 2 vale 0,5.
    """

    assert posicao_do_acerto(["trauma", "chocolate"], ["chocolate"]) == 2


def test_sem_o_protocolo_certo_na_lista_nao_ha_posicao():

    assert posicao_do_acerto(["trauma", "vomito"], ["chocolate"]) is None


def test_qualquer_protocolo_aceitavel_conta():
    """
    Um cão atropelado e ofegante casa com trauma e com respiratório. Exigir
    um único documento puniria acerto legítimo.
    """

    assert posicao_do_acerto(
        ["respiratorio", "trauma"], ["trauma", "respiratorio"]
    ) == 1


# ----------------------------------------------------------------------
# Agregação
# ----------------------------------------------------------------------


def test_precision_e_mrr_com_valores_conferiveis_a_mao():
    """
    Três casos: acerto no topo (recíproco 1), acerto em segundo (0,5) e
    erro (0). Precision@1 = 1/3; MRR = (1 + 0,5 + 0) / 3 = 0,5.
    """

    avaliados = [
        avaliar_caso(caso("a", "chocolate"), recuperados(("chocolate", 0.8))),
        avaliar_caso(
            caso("b", "trauma"),
            recuperados(("vomito", 0.6), ("trauma", 0.5)),
        ),
        avaliar_caso(caso("c", "convulsao"), recuperados(("trauma", 0.4))),
    ]

    m = compute_retrieval_metrics(avaliados)

    assert m["precision_at_1"] == round(1 / 3, 4)
    assert m["mrr"] == 0.5
    assert m["n_com_protocolo"] == 3


def test_recall_conta_o_acerto_fora_do_topo_mas_dentro_do_k():

    avaliados = [
        avaliar_caso(
            caso("a", "chocolate"),
            recuperados(
                ("trauma", 0.6), ("vomito", 0.5), ("chocolate", 0.4)
            ),
        )
    ]

    m = compute_retrieval_metrics(avaliados, recall_k=5)

    assert m["precision_at_1"] == 0.0
    assert m["recall_at_5"] == 1.0
    assert m["mrr"] == round(1 / 3, 4)


def test_caso_leve_nao_entra_na_precisao():
    """
    A natureza do caso decide em que conta ele entra. Um caso leve sem
    protocolo esperado não pode contar como erro de Precision@1 — não havia
    o que acertar.
    """

    avaliados = [
        avaliar_caso(caso("a", "chocolate"), recuperados(("chocolate", 0.8))),
        avaliar_caso(
            caso("b", motivo="caso leve"), recuperados(("trauma", 0.5))
        ),
    ]

    m = compute_retrieval_metrics(avaliados)

    assert m["n_com_protocolo"] == 1
    assert m["precision_at_1"] == 1.0
    assert m["n_caso_leve"] == 1


def test_leve_e_sem_cobertura_sao_contados_separados():
    """
    "A busca acertou ao ficar quieta" e "a base não tem o que buscar" são
    diagnósticos diferentes: o segundo é dado de curadoria, não nota da
    busca.
    """

    avaliados = [
        avaliar_caso(caso("a", motivo="caso leve"), recuperados(("x", 0.5))),
        avaliar_caso(
            caso("b", motivo="sem cobertura"), recuperados(("x", 0.9))
        ),
    ]

    m = compute_retrieval_metrics(avaliados, limiar=0.70)

    assert m["silence_rate_on_mild"] == 1.0
    assert m["silence_rate_on_uncovered"] == 0.0


def test_silencio_usa_o_limiar_e_nao_a_ausencia_de_resultado():
    """
    A busca sempre devolve algo. "Ficar quieta" é não devolver nada **acima
    do corte** — a mesma definição que o classificador usa desde 12/09.
    """

    avaliados = [
        avaliar_caso(caso("a", motivo="caso leve"), recuperados(("x", 0.69))),
        avaliar_caso(caso("b", motivo="caso leve"), recuperados(("x", 0.71))),
    ]

    m = compute_retrieval_metrics(avaliados, limiar=0.70)

    assert m["silence_rate_on_mild"] == 0.5


def test_corte_usa_nota_hibrida_com_fallback_para_snapshot_antigo():
    novo = avaliar_caso(
        caso("novo", motivo="caso leve"),
        [{"topic": "x", "score": 0.50, "ranking_score": 0.75}],
    )
    antigo = avaliar_caso(
        caso("antigo", motivo="caso leve"),
        [{"topic": "x", "score": 0.69}],
    )

    assert novo["max_score"] == 0.75
    assert antigo["max_score"] == 0.69


def test_silencio_em_tudo_fica_visivel_como_acidente():
    """
    Com a base atual a busca não passa do corte em nenhum caso, e por isso
    "acerta" todos os leves. `share_cases_above_threshold` em zero é o que
    impede ler 100% de silêncio como mérito.
    """

    avaliados = [
        avaliar_caso(caso("a", "chocolate"), recuperados(("trauma", 0.5))),
        avaliar_caso(caso("b", motivo="caso leve"), recuperados(("x", 0.4))),
    ]

    m = compute_retrieval_metrics(avaliados, limiar=0.70)

    assert m["silence_rate_on_mild"] == 1.0
    assert m["share_cases_above_threshold"] == 0.0


def test_protocolo_ima_aparece_na_concentracao():
    """
    O achado do ensaio: um documento em primeiro lugar para assuntos que
    não são dele. Nenhuma das três métricas clássicas mostra isso, porque
    todas olham o caso e não o conjunto.
    """

    avaliados = [
        avaliar_caso(caso("a", "chocolate"), recuperados(("trauma", 0.5))),
        avaliar_caso(caso("b", "convulsao"), recuperados(("trauma", 0.5))),
        avaliar_caso(caso("c", "vomito"), recuperados(("vomito", 0.5))),
    ]

    concentracao = compute_retrieval_metrics(avaliados)["top1_concentration"]

    assert concentracao["topic"] == "trauma"
    assert concentracao["cases"] == 2
    assert concentracao["share"] == round(2 / 3, 4)


def test_sem_casos_com_protocolo_as_metricas_de_posicao_somem():
    """
    Sem denominador não existe taxa. Zero diria "nenhum acerto" onde o
    certo é "não havia o que medir".
    """

    avaliados = [
        avaliar_caso(caso("a", motivo="caso leve"), recuperados(("x", 0.3)))
    ]

    m = compute_retrieval_metrics(avaliados)

    assert m["precision_at_1"] is None
    assert m["mrr"] is None


def test_busca_vazia_nao_quebra():

    avaliado = avaliar_caso(caso("a", "chocolate"), [])

    m = compute_retrieval_metrics([avaliado])

    assert avaliado["max_score"] is None
    assert avaliado["posicao"] is None
    assert m["precision_at_1"] == 0.0


# ----------------------------------------------------------------------
# Baselines triviais
# ----------------------------------------------------------------------


def test_baseline_do_acaso_usa_o_tamanho_da_base():
    """
    Sem referência, "Precision@1 = 0,5" é um número solto. Com dois
    documentos na base e um aceitável por caso, o acaso acerta metade — e
    aí 0,5 deixa de ser um bom resultado.
    """

    avaliados = [
        avaliar_caso(caso("a", "chocolate"), recuperados(("chocolate", 0.8), ("trauma", 0.4))),
        avaliar_caso(caso("b", "trauma"), recuperados(("chocolate", 0.6), ("trauma", 0.5))),
    ]

    base = compute_retrieval_metrics(avaliados)["baselines"]

    assert base["documento_ao_acaso"] == 0.5


def test_baseline_de_responder_sempre_o_mesmo():
    """
    Se um documento domina o primeiro lugar, vale saber quanto ele
    acertaria sozinho — é o piso que a busca precisa superar.
    """

    avaliados = [
        avaliar_caso(caso("a", "trauma"), recuperados(("trauma", 0.5))),
        avaliar_caso(caso("b", "chocolate"), recuperados(("trauma", 0.5))),
        avaliar_caso(caso("c", "convulsao"), recuperados(("trauma", 0.5))),
    ]

    m = compute_retrieval_metrics(avaliados)

    assert m["top1_concentration"]["topic"] == "trauma"
    assert m["baselines"]["sempre_o_mesmo_documento"] == round(1 / 3, 4)


def test_quantos_documentos_a_busca_mostra_por_caso():
    """
    É o número que diz se o Recall@k informa alguma coisa. Mostrando quase
    a base inteira por consulta, "o certo está entre os primeiros" é quase
    geométrico.
    """

    avaliados = [
        avaliar_caso(
            caso("a", "chocolate"),
            recuperados(("chocolate", 0.8), ("trauma", 0.4), ("trauma", 0.3)),
        )
    ]

    base = compute_retrieval_metrics(avaliados)["baselines"]

    # Três trechos, dois documentos distintos.
    assert base["documentos_distintos_por_caso"] == 2.0
