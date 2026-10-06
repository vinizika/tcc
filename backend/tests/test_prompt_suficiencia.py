"""
O prompt `v2_suficiencia` (rodada 23 do Ryu) é o `v1_grounded` com uma regra a
mais: frase vaga, sem frequência, duração nem estado do animal, não vira
NAO_EMERGENCIA. É uma proposta, fora do padrão: o v1 não pode mudar.
"""

from conftest import documento

from app.pipeline.config_resolver import resolve
from app.prompts.triage import REGRA_SUFICIENCIA, build_triage_messages
from app.schemas.triage import PipelineOptions


def sistema(settings, documentos, **opcoes):
    config = resolve(settings, PipelineOptions(**opcoes))
    return build_triage_messages("meu cachorro tá vomitando", documentos, config)[0]["content"]


def test_v1_continua_sem_a_regra(settings):

    assert REGRA_SUFICIENCIA not in sistema(settings, [documento()])
    assert REGRA_SUFICIENCIA not in sistema(settings, [])


def test_v2_e_o_v1_com_a_regra_logo_depois_da_do_incerto(settings):

    for documentos in ([documento()], []):
        v1 = sistema(settings, documentos, prompt_version="v1_grounded")
        v2 = sistema(settings, documentos, prompt_version="v2_suficiencia")

        assert v2.replace("\n" + REGRA_SUFICIENCIA, "") == v1
        assert "responda INCERTO.\n" + REGRA_SUFICIENCIA in v2


def test_v2_vale_tambem_com_chain_of_thought(settings):

    v2 = sistema(settings, [documento()], prompt_version="v2_suficiencia", cot_enabled=True)

    assert REGRA_SUFICIENCIA in v2
