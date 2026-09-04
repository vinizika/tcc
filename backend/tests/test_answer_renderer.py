"""
O texto da resposta é montado em código, e não pedido ao modelo, para o
formato ser sempre o mesmo. O conteúdo clínico, porém, vem do modelo e
pode conter caracteres que quebram a formatação da tela.
"""

from app.pipeline.answer_renderer import escapar, render
from app.schemas.triage_output import CitedSource, TriageResult


def triagem(**campos) -> TriageResult:

    base = {
        "classificacao": "EMERGENCIA",
        "justificativa": "sinais compatíveis com risco à vida",
        "sinais_de_alerta": ["tremores", "vômito"],
        "recomendacao": "procure atendimento agora",
    }
    base.update(campos)

    return TriageResult(**base)


def test_pontuacao_comum_nao_e_escapada():
    """
    Escapar toda pontuação deixaria o texto sujo de barras invertidas.
    """

    assert escapar("A gata não urina desde ontem.") == (
        "A gata não urina desde ontem."
    )


def test_caracteres_que_alteram_a_formatacao_sao_neutralizados():

    assert escapar("*urgente*") == r"\*urgente\*"
    assert escapar("custa R$ 300") == r"custa R\$ 300"
    assert escapar(":red[perigo]") == r"\:red\[perigo\]"


def test_marcador_no_inicio_da_linha_nao_vira_estrutura():

    assert escapar("- item") == r"\- item"
    assert escapar("# titulo") == r"\# titulo"
    assert escapar("1. primeiro") == r"1\. primeiro"


def test_quebra_de_linha_do_modelo_nao_parte_o_item():

    assert escapar("linha um\nlinha dois") == "linha um linha dois"


def test_resposta_traz_classificacao_sinais_recomendacao_e_aviso():

    texto = render(triagem())

    assert "Emergência" in texto
    assert "tremores" in texto
    assert "procure atendimento agora" in texto
    assert "não substitui a avaliação" in texto


def test_fontes_citadas_aparecem_na_resposta():

    texto = render(
        triagem(
            fontes=[
                CitedSource(
                    index=1,
                    chunk_id="c1",
                    title="Obstrução urinária em gatos",
                    source="protocolo.pdf",
                )
            ]
        )
    )

    assert "Baseado em" in texto
    assert "Obstrução urinária em gatos" in texto


def test_falha_de_formato_e_dita_ao_tutor():
    """
    Quando o modelo não devolve uma resposta utilizável, o tutor precisa
    saber que o caso não foi classificado, em vez de receber um texto que
    parece uma avaliação.
    """

    texto = render(
        triagem(
            classificacao="INCERTO",
            schema_valid=False,
            justificativa="",
            sinais_de_alerta=[],
        )
    )

    assert "Não foi possível estruturar" in texto
    assert "não substitui a avaliação" in texto
