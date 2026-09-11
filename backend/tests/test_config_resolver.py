"""
A resolução de configuração define a semântica de cada braço do estudo de
ablação. Se ela estiver errada, uma rodada inteira de avaliação mede outra
coisa sem que ninguém perceba.
"""

import pytest
from pydantic import ValidationError

from app.exceptions.pipeline_exception import UnsupportedOptionException
from app.pipeline.config_resolver import resolve
from app.schemas.triage import PipelineOptions


def test_sem_opcoes_usa_os_padroes_das_settings(settings):

    config = resolve(settings, None)

    assert config.prompt_version == "v1_grounded"
    assert config.retrieval_enabled is True
    assert config.context_top_k == 3
    assert config.model == "modelo-de-teste"
    assert config.temperature == 0.0
    assert config.seed == 42


def test_opcao_da_requisicao_vence_a_setting(settings):

    config = resolve(
        settings,
        PipelineOptions(context_top_k=5, temperature=0.7),
    )

    assert config.context_top_k == 5
    assert config.temperature == 0.7


def test_none_significa_usar_o_padrao(settings):
    """
    Um campo ausente não pode ser confundido com "desligado".
    """

    config = resolve(
        settings,
        PipelineOptions(context_top_k=None, hyde_enabled=None),
    )

    assert config.context_top_k == 3
    assert config.hyde_enabled is True


def test_sem_busca_desliga_as_etapas_de_consulta(settings):
    """
    Sem recuperação não há consulta a otimizar: reescrever ou gerar
    variações seria gastar chamadas ao modelo sem efeito, e a configuração
    ecoada mentiria sobre o que rodou.
    """

    config = resolve(settings, PipelineOptions(retrieval_enabled=False))

    assert config.query_rewriting_enabled is False
    assert config.multi_query_enabled is False
    assert config.hyde_enabled is False


def test_modo_legado_reproduz_as_condicoes_da_medicao_antiga(settings):
    """
    O braço v0_legacy existe para comparar com o baseline de 04/05, que
    rodou sem RAG, com format=json e sem teto de tokens.
    """

    config = resolve(settings, PipelineOptions(prompt_version="v0_legacy"))

    assert config.retrieval_enabled is False
    assert config.structured_output_mode == "json"
    assert config.num_predict == -1


def test_modo_legado_ignora_pedido_de_busca(settings):
    """
    Pedir busca junto do prompt antigo seria um braço sem significado.
    A configuração ecoada mostra o que de fato valeu.
    """

    config = resolve(
        settings,
        PipelineOptions(
            prompt_version="v0_legacy",
            retrieval_enabled=True,
        ),
    )

    assert config.retrieval_enabled is False


def test_etapa_nao_implementada_falha_em_vez_de_ser_ignorada(settings):
    """
    Aceitar uma etapa que não existe produziria uma linha de ablação
    idêntica à do braço sem ela, sugerindo que a técnica não teve efeito.
    """

    with pytest.raises(UnsupportedOptionException) as erro:
        resolve(settings, PipelineOptions(self_refine_enabled=True))

    assert erro.value.status_code == 400


def test_etapa_nao_implementada_desligada_nao_incomoda(settings):

    config = resolve(
        settings,
        PipelineOptions(cot_enabled=False, self_refine_enabled=False),
    )

    assert config.cot_enabled is False
    assert config.self_refine_enabled is False


# ----------------------------------------------------------------------
# Chain-of-Thought
# ----------------------------------------------------------------------


def test_cot_desligado_por_padrao(settings):
    """
    O braço com raciocínio é opcional: ligá-lo sem querer mudaria o que
    todas as rodadas anteriores mediram.
    """

    config = resolve(settings, None)

    assert config.cot_enabled is False
    assert config.cot_position == "first"


def test_cot_ligado_pela_requisicao(settings):

    config = resolve(settings, PipelineOptions(cot_enabled=True))

    assert config.cot_enabled is True
    assert config.cot_position == "first"


def test_posicao_do_raciocinio_pode_ser_invertida(settings):
    """
    O braço de controle escreve o raciocínio depois da conclusão. É o que
    separa "a ordem importa" de "a rubrica importa".
    """

    config = resolve(
        settings,
        PipelineOptions(cot_enabled=True, cot_position="last"),
    )

    assert config.cot_position == "last"


def test_modo_legado_ignora_o_cot(settings):
    """
    O braço v0_legacy reproduz a medição de 04/05, feita sem raciocínio
    nenhum. Pedir as duas coisas juntas é contradição, e quem manda é o
    braço histórico.
    """

    config = resolve(
        settings,
        PipelineOptions(prompt_version="v0_legacy", cot_enabled=True),
    )

    assert config.cot_enabled is False


def test_cot_sem_gramatica_e_recusado(settings):
    """
    Em modo json puro a ordem dos campos não é garantida — e a ordem é o
    experimento. Um braço assim não mediria nada.
    """

    with pytest.raises(UnsupportedOptionException) as erro:
        resolve(
            settings,
            PipelineOptions(
                cot_enabled=True,
                structured_output_mode="json",
            ),
        )

    assert erro.value.status_code == 400
    assert "schema" in str(erro.value)


def test_nome_de_opcao_desconhecido_e_rejeitado():
    """
    Um erro de digitação no runner tem que falhar alto, e não virar uma
    rodada que mediu a configuração padrão sem ninguém notar.
    """

    with pytest.raises(ValidationError):
        PipelineOptions(retrieval_enable=False)
