"""
Testes do compare da régua.

O compare existe para pegar uma piora que ninguém viu. Se ele mesmo tiver um
defeito silencioso, a base cresce e o time acha que está medindo — que é pior
do que não ter instrumento nenhum. Daí o cuidado com os casos de borda:
posição que vira `None`, assunto que aparece sem ser novo, espécie escrita de
três jeitos.

Sem rede e sem disco de verdade: as rodadas são escritas em `tmp_path`.
"""

import json

import pytest

from retrieval_compare import (
    carregar_rodada,
    compute_compare,
    normalizar_especie,
    ordenar_posicao,
)
from retrieval_compare_report import escrever_compare_md

MAPA = [
    {
        "id": "chocolate_toxicosis", "quadro": "Intoxicacao por chocolate",
        "especie": "cao", "prioridade": "A", "etapa": "1",
    },
    {
        "id": "gastric_dilatation_volvulus", "quadro": "Torcao gastrica",
        "especie": "cao", "prioridade": "A", "etapa": "1",
    },
    {
        "id": "trauma_and_bleeding", "quadro": "Trauma e hemorragias",
        "especie": "ambos", "prioridade": "A", "etapa": "1",
    },
    {
        "id": "urethral_obstruction", "quadro": "Obstrucao uretral",
        "especie": "gato", "prioridade": "A", "etapa": "1",
    },
]

FICHAS = [
    {"topic": "chocolate_toxicosis", "species": "dogs_and_cats"},
    {"topic": "trauma_and_bleeding", "species": "dogs_and_cats"},
    {"topic": "urethral_obstruction", "species": "cats"},
]


def escrever_rodada(
    destino,
    casos,
    *,
    run_id="rodada",
    chunk_ids="hash-da-base",
    chunk_count=18,
    limiar=0.70,
    indexed_topics=None,
    include_inventory=True,
):
    """
    Escreve uma rodada de mentira com a mesma forma da real.

    `casos` é uma lista de `(id, expected_topics, natureza, [(topic, score)])`
    — os pares são o que a busca devolveu, na ordem.
    """

    destino.mkdir(parents=True, exist_ok=True)

    if indexed_topics is None:
        indexed_topics = {
            ficha["topic"]: ficha["species"] for ficha in FICHAS
        }
    vector_store = {
        "chunk_count": chunk_count,
        "chunk_ids_sha256": chunk_ids,
        "content_sha256": chunk_ids + "-conteudo",
    }
    if include_inventory:
        vector_store.update(
            {
                "topic_counts": {topic: 1 for topic in indexed_topics},
                "species_counts_by_topic": {
                    topic: {species: 1}
                    for topic, species in indexed_topics.items()
                },
            }
        )

    (destino / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "started_at": "2026-09-12T10:00:00-03:00",
                "git": {"sha": "abc1234"},
                "limiar": limiar,
                "backend_fingerprint": {
                    "vector_store": vector_store
                },
            }
        ),
        encoding="utf-8",
    )

    linhas = []

    for caso_id, esperados, natureza, recuperados in casos:
        linhas.append(
            json.dumps(
                {
                    "id": caso_id,
                    "text": f"relato do caso {caso_id}",
                    "expected_topics": esperados,
                    "expected_none_reason": (
                        "" if natureza == "com protocolo" else natureza
                    ),
                    "natureza": natureza,
                    "posicao": None,
                    "documents": [
                        {
                            "id": f"chunk-{i}",
                            "title": topico,
                            "content": "…",
                            "source": "teste",
                            "score": score,
                            "topic": topico,
                            "source_file": f"{topico}.pdf",
                        }
                        for i, (topico, score) in enumerate(recuperados)
                    ],
                },
                ensure_ascii=False,
            )
        )

    (destino / "results.jsonl").write_text(
        "\n".join(linhas) + "\n", encoding="utf-8"
    )

    return destino


def comparar(tmp_path, casos_a, casos_b, **kwargs):
    """Compara duas rodadas descritas pelos casos, devolvendo o resultado."""

    chunk_ids_b = kwargs.pop("chunk_ids_b", "hash-da-base-nova")
    indexed_topics_a = kwargs.pop("indexed_topics_a", None)
    indexed_topics_b = kwargs.pop("indexed_topics_b", None)

    a = carregar_rodada(
        escrever_rodada(
            tmp_path / "a",
            casos_a,
            run_id="antes",
            indexed_topics=indexed_topics_a,
            **kwargs,
        )
    )
    b = carregar_rodada(
        escrever_rodada(
            tmp_path / "b",
            casos_b,
            run_id="depois",
            chunk_ids=chunk_ids_b,
            indexed_topics=indexed_topics_b,
            **kwargs,
        )
    )

    return compute_compare(a, b, MAPA, FICHAS)


UM_CASO = [
    (
        "b01",
        ["chocolate_toxicosis"],
        "com protocolo",
        [("trauma_and_bleeding", 0.5), ("chocolate_toxicosis", 0.4)],
    )
]


# ----------------------------------------------------------------------
# Posição: o `None` é o perigo
# ----------------------------------------------------------------------


def test_posicao_ausente_e_pior_que_qualquer_posicao():
    """
    `None` quer dizer "não apareceu entre os cinco". Tratar como zero faria
    "sumiu da lista" ser contado como "melhorou" — a leitura mais perigosa
    que este instrumento poderia produzir.
    """

    assert ordenar_posicao(None) > ordenar_posicao(5)
    assert ordenar_posicao(1) < ordenar_posicao(2)


def test_caso_que_sobe_de_posicao_melhorou(tmp_path):

    antes = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("trauma_and_bleeding", 0.5), ("chocolate_toxicosis", 0.4)])]
    depois = [("b01", ["chocolate_toxicosis"], "com protocolo",
               [("chocolate_toxicosis", 0.6), ("trauma_and_bleeding", 0.5)])]

    resultado = comparar(tmp_path, antes, depois)

    assert resultado["ordenacao"]["casos"][0]["situacao"] == "melhorou"
    assert resultado["ordenacao"]["melhoraram"] == 1
    assert resultado["ordenacao"]["pioraram"] == 0


def test_caso_que_desce_de_posicao_piorou(tmp_path):

    antes = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("chocolate_toxicosis", 0.6)])]
    depois = [("b01", ["chocolate_toxicosis"], "com protocolo",
               [("trauma_and_bleeding", 0.7), ("chocolate_toxicosis", 0.4)])]

    resultado = comparar(tmp_path, antes, depois)

    assert resultado["ordenacao"]["casos"][0]["situacao"] == "piorou"
    assert resultado["ordenacao"]["pioraram"] == 1


def test_protocolo_que_sumiu_do_top5_conta_como_piora(tmp_path):
    """
    O protocolo certo deixou de ser recuperado. É o pior resultado possível
    para um caso, e precisa aparecer como piora — não como "igual" nem, pior,
    como melhora.
    """

    antes = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("chocolate_toxicosis", 0.6)])]
    depois = [("b01", ["chocolate_toxicosis"], "com protocolo",
               [("trauma_and_bleeding", 0.7)])]

    resultado = comparar(tmp_path, antes, depois)

    assert resultado["ordenacao"]["casos"][0]["situacao"] == "saiu"
    assert resultado["ordenacao"]["pioraram"] == 1


def test_protocolo_que_apareceu_conta_como_melhora(tmp_path):

    antes = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("trauma_and_bleeding", 0.7)])]
    depois = [("b01", ["chocolate_toxicosis"], "com protocolo",
               [("trauma_and_bleeding", 0.7), ("chocolate_toxicosis", 0.4)])]

    resultado = comparar(tmp_path, antes, depois)

    assert resultado["ordenacao"]["casos"][0]["situacao"] == "entrou"
    assert resultado["ordenacao"]["melhoraram"] == 1


# ----------------------------------------------------------------------
# O que aborta, e o que não aborta
# ----------------------------------------------------------------------


def test_limiar_diferente_aborta(tmp_path):
    """
    Os blocos de ruído dependem do corte. Comparar com limiares diferentes
    mediria a mudança de limiar e chamaria isso de efeito da base.
    """

    a = carregar_rodada(escrever_rodada(tmp_path / "a", UM_CASO, limiar=0.70))
    b = carregar_rodada(escrever_rodada(tmp_path / "b", UM_CASO, limiar=0.60))

    with pytest.raises(SystemExit, match="limiares diferentes"):
        compute_compare(a, b, MAPA, FICHAS)


def test_caso_em_comum_com_texto_diferente_aborta(tmp_path):
    """
    Mesmo id, outro relato: o gabarito mudou, e "antes e depois" deixaria de
    ser sobre a mesma pergunta.
    """

    a = carregar_rodada(escrever_rodada(tmp_path / "a", UM_CASO))
    b = carregar_rodada(escrever_rodada(tmp_path / "b", UM_CASO))
    b["casos"]["b01"]["text"] = "outro relato"

    with pytest.raises(SystemExit, match="textos diferentes"):
        compute_compare(a, b, MAPA, FICHAS)


def test_caso_com_gabarito_diferente_aborta(tmp_path):

    a = carregar_rodada(escrever_rodada(tmp_path / "a", UM_CASO))
    b = carregar_rodada(escrever_rodada(tmp_path / "b", UM_CASO))
    b["casos"]["b01"]["expected_topics"] = ["trauma_and_bleeding"]

    with pytest.raises(SystemExit, match="protocolos diferentes"):
        compute_compare(a, b, MAPA, FICHAS)


def test_caso_novo_em_b_nao_aborta_e_fica_registrado(tmp_path):
    """
    Cada lote de fontes traz relatos de régua novos. Travar por igualdade do
    `cases.csv` abortaria em todo lote, e o instrumento nasceria inútil: a
    comparação é sobre a interseção, e o caso novo entra na próxima.
    """

    depois = UM_CASO + [
        ("b19", ["trauma_and_bleeding"], "com protocolo",
         [("trauma_and_bleeding", 0.6)])
    ]

    resultado = comparar(tmp_path, UM_CASO, depois)

    assert resultado["pareamento"]["so_em_b"] == ["b19"]
    assert resultado["pareamento"]["comuns"] == ["b01"]


# ----------------------------------------------------------------------
# Cobertura
# ----------------------------------------------------------------------


def test_assunto_que_passou_a_aparecer_vira_encontravel(tmp_path):

    antes = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("trauma_and_bleeding", 0.5)])]
    depois = [("b01", ["chocolate_toxicosis"], "com protocolo",
               [("trauma_and_bleeding", 0.5), ("chocolate_toxicosis", 0.4)])]

    cobertura = comparar(tmp_path, antes, depois)["cobertura"]
    linha = next(l for l in cobertura["linhas"] if l["id"] == "chocolate_toxicosis")

    assert linha["antes"] == "indexado, nao encontrado"
    assert linha["depois"] == "encontravel"
    # Trauma apareceu no caso de chocolate, onde é erro: não é cobertura.
    assert cobertura["encontraveis"] == [0, 1]


def test_documento_indexado_que_nunca_aparece_nao_conta_como_cobertura(tmp_path):
    """
    É o critério "cobertura real" da porta: um documento que entrou na base e
    nunca é recuperado não muda a resposta de ninguém.
    """

    casos = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("trauma_and_bleeding", 0.5)])]

    cobertura = comparar(tmp_path, casos, casos)["cobertura"]
    linha = next(l for l in cobertura["linhas"] if l["id"] == "urethral_obstruction")

    assert linha["depois"] == "indexado, nao encontrado"


def test_quadro_sem_documento_nenhum_fica_marcado(tmp_path):

    casos = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("trauma_and_bleeding", 0.5)])]

    cobertura = comparar(tmp_path, casos, casos)["cobertura"]
    linha = next(
        l for l in cobertura["linhas"] if l["id"] == "gastric_dilatation_volvulus"
    )

    assert linha["depois"] == "sem documento"


# ----------------------------------------------------------------------
# Espécie
# ----------------------------------------------------------------------


def test_especie_normaliza_as_tres_grafias_das_fichas():
    """
    As fichas usam `dogs_and_cats`, `cats` e `dog` (B-53). Sem normalizar,
    `cats` nunca casaria com `gato` do mapa e a cobertura por espécie sairia
    errada em silêncio.
    """

    assert normalizar_especie("cats") == "gato"
    assert normalizar_especie("dog") == "cao"
    assert normalizar_especie("dogs_and_cats") == "ambos"
    assert normalizar_especie("") == ""


def test_especie_divergente_entre_ficha_e_mapa_e_apontada(tmp_path):
    """
    O caso b15 da régua ensinou a olhar isto: o protocolo era de gatos e o
    caso era de cão. O mapa diz `gato` para `urethral_obstruction` e a ficha
    diz `cats` — que normaliza para `gato` e **não** é divergência.
    """

    casos = [("b01", ["chocolate_toxicosis"], "com protocolo",
              [("chocolate_toxicosis", 0.5)])]

    cobertura = comparar(tmp_path, casos, casos)["cobertura"]
    divergentes = {d["id"] for d in cobertura["especies_divergentes"]}

    # Uma fonte para ambos cobre corretamente uma linha que exige somente cão.
    assert "chocolate_toxicosis" not in divergentes
    assert "urethral_obstruction" not in divergentes


def test_linha_ambos_nao_e_coberta_por_fonte_so_de_gato(tmp_path):
    mapa = [
        {
            "id": "urethral_obstruction",
            "quadro": "Obstrucao uretral",
            "especie": "ambos",
            "prioridade": "A",
            "etapa": "1",
        }
    ]
    casos = [
        (
            "b15",
            ["urethral_obstruction"],
            "com protocolo",
            [("urethral_obstruction", 0.8)],
        )
    ]
    a = carregar_rodada(
        escrever_rodada(
            tmp_path / "a",
            casos,
            indexed_topics={"urethral_obstruction": "cat"},
        )
    )

    cobertura = compute_compare(a, a, mapa, [])["cobertura"]

    assert cobertura["linhas"][0]["depois"] == (
        "indexado, cobertura de especie incompleta"
    )


def test_documento_em_caso_inesperado_nao_e_encontravel(tmp_path):
    casos = [
        (
            "b01",
            ["chocolate_toxicosis"],
            "com protocolo",
            [("trauma_and_bleeding", 0.9)],
        )
    ]

    cobertura = comparar(tmp_path, casos, casos)["cobertura"]
    trauma = next(
        line for line in cobertura["linhas"]
        if line["id"] == "trauma_and_bleeding"
    )

    assert trauma["depois"] == "indexado, nao encontrado"


def test_topico_existente_nas_duas_bases_nao_e_novo(tmp_path):
    casos = [
        (
            "b12",
            [],
            "sem cobertura",
            [("gastric_dilatation_volvulus", 0.8)],
        )
    ]
    indexed = {"gastric_dilatation_volvulus": "dog"}

    resultado = comparar(
        tmp_path,
        casos,
        casos,
        indexed_topics_a=indexed,
        indexed_topics_b=indexed,
    )

    assert resultado["cobertura"]["topicos_novos"] == []
    assert resultado["gabarito_a_atualizar"] == []


# ----------------------------------------------------------------------
# Gabarito
# ----------------------------------------------------------------------


def test_assunto_novo_num_caso_sem_cobertura_pede_revisao(tmp_path):

    antes = [("b12", [], "sem cobertura", [("trauma_and_bleeding", 0.5)])]
    depois = [
        (
            "b12",
            [],
            "sem cobertura",
            [("gastric_dilatation_volvulus", 0.8), ("trauma_and_bleeding", 0.5)],
        )
    ]

    pendentes = comparar(
        tmp_path,
        antes,
        depois,
        indexed_topics_a={"trauma_and_bleeding": "dogs_and_cats"},
        indexed_topics_b={
            "trauma_and_bleeding": "dogs_and_cats",
            "gastric_dilatation_volvulus": "dog",
        },
    )["gabarito_a_atualizar"]

    assert len(pendentes) == 1
    assert pendentes[0]["apareceu"] == "gastric_dilatation_volvulus"
    assert pendentes[0]["acima_do_corte"] is True


def test_o_ima_no_caso_sem_cobertura_nao_pede_revisao(tmp_path):
    """
    O b12 (torção gástrica) recebe `trauma_and_bleeding` em primeiro lugar
    desde a rodada 11 — é o protocolo-ímã do B-02, não cobertura. Marcar isso
    como "gabarito a atualizar" apontaria os quatro casos sem cobertura em
    toda comparação, para sempre, e o bloco viraria ruído que ninguém lê.
    """

    casos = [("b12", [], "sem cobertura", [("trauma_and_bleeding", 0.5)])]

    assert comparar(tmp_path, casos, casos)["gabarito_a_atualizar"] == []


# ----------------------------------------------------------------------
# Ruído e porta
# ----------------------------------------------------------------------


def test_caso_leve_que_cruza_o_corte_e_contado(tmp_path):
    """
    É o mecanismo que custou 22 falsos não urgentes na rodada 10: trecho
    irrelevante entrando no prompt de quem não precisava dele.
    """

    antes = [("b05", [], "caso leve", [("trauma_and_bleeding", 0.5)])]
    depois = [("b05", [], "caso leve", [("trauma_and_bleeding", 0.8)])]

    ruido = comparar(tmp_path, antes, depois)["ruido"]

    assert ruido["leves"][0]["cruzou_o_corte"] is True
    assert ruido["leves_acima_do_corte"] == 1


def test_porta_reprova_quando_um_documento_domina_o_primeiro_lugar(tmp_path):

    casos = [
        ("b01", ["chocolate_toxicosis"], "com protocolo",
         [("trauma_and_bleeding", 0.5), ("chocolate_toxicosis", 0.4)]),
        ("b02", ["urethral_obstruction"], "com protocolo",
         [("trauma_and_bleeding", 0.5), ("urethral_obstruction", 0.4)]),
    ]

    porta = comparar(tmp_path, casos, casos)["porta"]
    ima = next(c for c in porta if c["eixo"] == "Ímã")

    assert ima["aprova"] is False


def test_porta_aprova_ordenacao_quando_nada_piorou(tmp_path):

    porta = comparar(tmp_path, UM_CASO, UM_CASO)["porta"]
    ordenacao = next(c for c in porta if c["eixo"] == "Ordenação")

    assert ordenacao["aprova"] is True


# ----------------------------------------------------------------------
# O relatório
# ----------------------------------------------------------------------


def test_base_igual_avisa_que_nada_foi_indexado(tmp_path):
    """
    Comparar duas rodadas da mesma base é teste de instrumento, não medição
    de curadoria. Sem o aviso, um "zero em tudo" seria lido como "a base nova
    não mudou nada" — conclusão oposta.
    """

    resultado = comparar(
        tmp_path, UM_CASO, UM_CASO, chunk_ids_b="hash-da-base"
    )

    assert resultado["base"]["mesma_base"] is True
    assert "Nenhum documento entrou" in escrever_compare_md(resultado)


def test_relatorio_tem_os_cinco_blocos(tmp_path):

    texto = escrever_compare_md(comparar(tmp_path, UM_CASO, UM_CASO))

    for titulo in (
        "## 1. Cobertura",
        "## 2. Ordenação",
        "## 3. Ruído",
        "## 4. Gabarito a atualizar",
        "## 5. A porta de decisão",
    ):
        assert titulo in texto, titulo


def test_relatorio_diz_quanto_vale_um_caso(tmp_path):
    """
    Com poucos casos com protocolo, uma linha move muito a Precision@1. O
    rodapé diz isso para ninguém ler um delta de uma casa decimal como
    tendência.
    """

    assert "da Precision@1" in escrever_compare_md(
        comparar(tmp_path, UM_CASO, UM_CASO)
    )


# ----------------------------------------------------------------------
# Teste dourado: os arquivos reais
# ----------------------------------------------------------------------


def test_rodada_citada_comparada_consigo_mesma_nao_muda_nada():
    """
    Teste dourado, sobre a rodada versionada em `data/retrieval/cited/`.

    Comparar uma rodada consigo mesma tem que dar zero em tudo. Se um dia
    der outra coisa, o defeito está no compare — não na base, não na
    curadoria. É a única asserção aqui que não depende de fixture.
    """

    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2]
    rodada = (
        raiz / "data" / "retrieval" / "cited"
        / "20260911-202505_linha_de_base"
    )

    with open(
        raiz / "data" / "curadoria" / "mapa-de-assuntos.csv",
        encoding="utf-8",
        newline="",
    ) as arquivo:
        import csv

        mapa = list(csv.DictReader(arquivo))

    fichas = [
        json.loads(caminho.read_text(encoding="utf-8"))
        for caminho in sorted(
            (raiz / "backend" / "data" / "documents").glob("*.json")
        )
    ]

    carregada = carregar_rodada(rodada)
    resultado = compute_compare(carregada, carregada, mapa, fichas)

    assert resultado["base"]["mesma_base"] is True
    assert resultado["ordenacao"]["melhoraram"] == 0
    assert resultado["ordenacao"]["pioraram"] == 0
    assert resultado["gabarito_a_atualizar"] == []
    assert resultado["cobertura"]["topicos_novos"] == []

    # O artefato histórico não gravou espécie por tópico. O fallback não
    # inventa essa cobertura a partir dos sidecars do checkout atual.
    assert resultado["cobertura"]["inventory_source"] == [
        "observed_results_fallback",
        "observed_results_fallback",
    ]
    assert resultado["cobertura"]["encontraveis"] == [0, 0]
    assert resultado["ruido"]["ima"]["depois"]["share"] == 0.5
