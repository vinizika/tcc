from app.clients import topic_router
from app.clients.reranker_client import RerankerClient
from app.models.retrieved_document import RetrievedDocument


def document(
    identifier: str,
    *,
    content: str,
    score: float,
    source_file: str,
    anchors: tuple[str, ...] = (),
    species: str = "",
    chunk_index: int | None = None,
) -> RetrievedDocument:
    return RetrievedDocument(
        id=identifier,
        chunk_id=identifier,
        title=identifier,
        content=content,
        source="teste",
        score=score,
        source_file=source_file,
        retrieval_anchors=anchors,
        species=species,
        chunk_index=chunk_index,
    )


def test_fonte_ancorada_nao_entra_sem_evidencia_no_relato():
    toxin = document(
        "toxina",
        content="vomiting lethargy abdominal pain",
        score=0.91,
        source_file="toxina.pdf",
        anchors=("grape", "grapes", "xylitol", "uva"),
    )
    general = document(
        "geral",
        content="vomiting in dogs",
        score=0.70,
        source_file="geral.pdf",
    )

    ranked = RerankerClient.rerank(
        ["dog vomiting and lethargy"], [toxin, general]
    )

    assert [item.id for item in ranked] == ["geral"]


def test_ancora_precisa_ser_uma_palavra_completa():
    toxin = document(
        "toxina",
        content="grape and raisin poisoning",
        score=0.91,
        source_file="toxina.pdf",
        anchors=("passa",),
    )

    ranked = RerankerClient.rerank(
        ["Meu cachorro está passando mal"],
        [toxin],
    )

    assert ranked == []


def test_documento_de_outra_especie_nao_entra():
    feline = document(
        "felino", content="vomiting", score=0.95,
        source_file="cat.pdf", species="cat",
    )
    canine = document(
        "canino", content="vomiting", score=0.80,
        source_file="dog.pdf", species="dog",
    )
    shared = document(
        "ambos", content="vomiting", score=0.75,
        source_file="both.pdf", species="dog_and_cat",
    )

    ranked = RerankerClient.rerank(
        ["Animal: Dog. Sintomas observados: vomiting"],
        [feline, canine, shared],
    )

    assert [item.id for item in ranked] == ["canino", "ambos"]


def test_fonte_ancorada_entra_quando_exposicao_esta_no_relato():
    toxin = document(
        "toxina",
        content="vomiting after grape ingestion",
        score=0.91,
        source_file="toxina.pdf",
        anchors=("grape", "grapes", "xylitol", "uva"),
    )

    ranked = RerankerClient.rerank(["dog ate grapes and is vomiting"], [toxin])

    assert [item.id for item in ranked] == ["toxina"]


def test_consulta_gerada_nao_pode_inventar_ancora():
    toxin = document(
        "toxina",
        content="xylitol poisoning vomiting",
        score=0.91,
        source_file="toxina.pdf",
        anchors=("xylitol",),
    )

    ranked = RerankerClient.rerank(
        ["dog vomiting", "possible xylitol poisoning"],
        [toxin],
        eligibility_query="dog vomiting",
    )

    assert ranked == []


def test_reordena_pela_relacao_lexical_sem_adulterar_score():
    generic = document(
        "generico",
        content="general veterinary information",
        score=0.72,
        source_file="a.pdf",
    )
    matching = document(
        "compativel",
        content="cat cannot urinate painful bladder",
        score=0.70,
        source_file="b.pdf",
    )

    ranked = RerankerClient.rerank(
        ["cat cannot urinate painful bladder"], [generic, matching]
    )

    assert [item.id for item in ranked] == ["compativel", "generico"]
    assert ranked[0].score == 0.70


def test_vocabulario_do_mapa_aplica_bonus_ao_assunto(monkeypatch):
    monkeypatch.setattr(
        topic_router,
        "TOPIC_TERMS",
        {
            "chocolate_toxicosis": (
                "comeu chocolate",
                "tremendo",
                "vomitando",
            ),
            "generic": ("vomitando",),
        },
    )
    generic = document(
        "generico",
        content="vomiting",
        score=0.75,
        source_file="generic.pdf",
    )
    generic.topic = "generic"
    chocolate = document(
        "chocolate",
        content="theobromine",
        score=0.65,
        source_file="chocolate.pdf",
    )
    chocolate.topic = "chocolate_toxicosis"

    ranked = RerankerClient.rerank(
        ["meu cachorro comeu chocolate e está tremendo"],
        [generic, chocolate],
    )

    assert [item.id for item in ranked] == ["chocolate", "generico"]
    assert chocolate.score == 0.65


def test_rota_de_alta_confianca_passa_o_corte_sem_mudar_score_vetorial(
    monkeypatch,
):
    monkeypatch.setattr(
        topic_router,
        "TOPIC_TERMS",
        {
            "allium_toxicosis": ("comeu cebola", "gengiva palida"),
            "generic": ("animal",),
        },
    )
    allium = document(
        "allium",
        content="oxidative damage",
        score=0.52,
        source_file="allium.pdf",
    )
    allium.topic = "allium_toxicosis"

    ranked = RerankerClient.rerank(
        ["cachorro comeu cebola e está com gengiva pálida"],
        [allium],
        eligibility_query="cachorro comeu cebola e está com gengiva pálida",
    )

    assert ranked[0].score == 0.52
    assert ranked[0].ranking_score >= 0.72


def test_rota_de_baixa_confianca_nao_forca_documento_acima_do_corte(
    monkeypatch,
):
    monkeypatch.setattr(
        topic_router,
        "TOPIC_TERMS",
        {
            "topic_a": ("vomitando", "quieto"),
            "topic_b": ("vomitando", "diarreia"),
        },
    )
    candidate = document(
        "a",
        content="outro texto",
        score=0.40,
        source_file="a.pdf",
    )
    candidate.topic = "topic_a"

    ranked = RerankerClient.rerank(
        ["cachorro vomitando"],
        [candidate],
        eligibility_query="cachorro vomitando",
    )

    assert ranked[0].ranking_score < 0.72


def test_rota_prefere_chunk_de_sinais_sem_achatar_a_ordem(monkeypatch):
    monkeypatch.setattr(
        topic_router,
        "TOPIC_TERMS",
        {
            "allium_toxicosis": ("comeu cebola", "gengiva palida"),
            "generic": ("vomitando",),
        },
    )
    exposure = document(
        "exposicao",
        content="onion and garlic are ingredients in several dishes",
        score=0.52,
        source_file="allium.pdf",
    )
    exposure.topic = "allium_toxicosis"
    signs = document(
        "sinais",
        content="Clinical signs include pale mucous membranes and weakness",
        score=0.51,
        source_file="allium.pdf",
    )
    signs.topic = "allium_toxicosis"

    ranked = RerankerClient.rerank(
        ["cachorro comeu cebola e está com gengiva pálida"],
        [exposure, signs],
        eligibility_query="cachorro comeu cebola e está com gengiva pálida",
    )

    assert [item.id for item in ranked] == ["sinais", "exposicao"]
    assert all(item.ranking_score >= 0.72 for item in ranked)


def test_rota_confiante_reserva_dois_chunks_do_assunto(monkeypatch):
    monkeypatch.setattr("app.clients.reranker_client.settings.TOP_K", 3)
    monkeypatch.setattr(
        topic_router,
        "TOPIC_TERMS",
        {
            "allium_toxicosis": ("comeu cebola", "gengiva palida"),
            "generic": ("vomitando",),
        },
    )
    first = document(
        "allium-1", content="Clinical signs appear later", score=0.55,
        source_file="allium.pdf",
    )
    second = document(
        "allium-2", content="pale membranes and weakness", score=0.54,
        source_file="allium.pdf",
    )
    distractor = document(
        "outro", content="generic", score=0.70,
        source_file="outro.pdf",
    )
    first.topic = second.topic = "allium_toxicosis"
    distractor.topic = "generic"

    ranked = RerankerClient.rerank(
        ["cachorro comeu cebola e está com gengiva pálida"],
        [distractor, first, second],
        eligibility_query="cachorro comeu cebola e está com gengiva pálida",
    )

    assert [item.id for item in ranked[:2]] == ["allium-1", "allium-2"]


def test_rota_confiante_continua_nos_chunks_seguintes(monkeypatch):
    monkeypatch.setattr("app.clients.reranker_client.settings.TOP_K", 3)
    monkeypatch.setattr(
        topic_router,
        "TOPIC_TERMS",
        {
            "allium_toxicosis": ("comeu cebola", "gengiva palida"),
            "generic": ("vomitando",),
        },
    )
    anchor = document(
        "chunk-7", content="Clinical signs appear later", score=0.55,
        source_file="allium.pdf", chunk_index=7,
    )
    next_one = document(
        "chunk-8", content="vomiting and depression", score=0.30,
        source_file="allium.pdf", chunk_index=8,
    )
    next_two = document(
        "chunk-9", content="anemia pale membranes weakness", score=0.29,
        source_file="allium.pdf", chunk_index=9,
    )
    higher_but_isolated = document(
        "chunk-20", content="reported case", score=0.50,
        source_file="allium.pdf", chunk_index=20,
    )
    for candidate in (anchor, next_one, next_two, higher_but_isolated):
        candidate.topic = "allium_toxicosis"

    ranked = RerankerClient.rerank(
        ["cachorro comeu cebola e está com gengiva pálida"],
        [higher_but_isolated, next_two, next_one, anchor],
        eligibility_query="cachorro comeu cebola e está com gengiva pálida",
    )

    assert [item.id for item in ranked] == ["chunk-7", "chunk-8", "chunk-9"]


def test_diversifica_fontes_depois_de_reordenar(monkeypatch):
    monkeypatch.setattr("app.clients.reranker_client.settings.TOP_K", 3)
    candidates = [
        document("a1", content="pain", score=0.90, source_file="a.pdf"),
        document("a2", content="pain", score=0.89, source_file="a.pdf"),
        document("b1", content="pain", score=0.88, source_file="b.pdf"),
        document("c1", content="pain", score=0.87, source_file="c.pdf"),
    ]

    ranked = RerankerClient.rerank(["pain"], candidates)

    assert [item.id for item in ranked] == ["a1", "b1", "c1"]
