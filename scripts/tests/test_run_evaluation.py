"""
Testes do runner.

O HTTP fica atrás de um cliente injetável, então tudo aqui roda sem API e
sem modelo. O teste mais valioso é o de regressão dos relatos: se o texto
enviado ao modelo mudar, a comparação com a medição de 04/05 deixa de valer,
e isso precisa falhar alto em vez de virar uma diferença inexplicada nos
números.
"""

import json
from pathlib import Path

import pandas as pd
import pytest
import requests

import run_evaluation as runner


RAIZ = Path(__file__).resolve().parents[2]
RESULTADO_HISTORICO = RAIZ / "data" / "evaluation" / "accuracy_results.csv"


class RespostaFalsa:
    def __init__(self, status):
        self.status_code = status
        self.text = f"erro simulado {status}"


class ClienteFalso:
    """
    Substitui a API. `roteiro` permite encenar falhas antes do sucesso.
    """

    def __init__(self, roteiro=None, classificacao="EMERGENCIA"):
        self.roteiro = list(roteiro or [])
        self.classificacao = classificacao
        self.chamadas = []

    def health(self):
        return True

    def fingerprint(self):
        return {"model": {"name": "modelo-de-teste"}}

    def classify(self, relato, options):
        self.chamadas.append({"relato": relato, "options": dict(options)})

        if self.roteiro:
            proximo = self.roteiro.pop(0)

            if isinstance(proximo, int):
                erro = requests.HTTPError(f"HTTP {proximo}")
                erro.response = RespostaFalsa(proximo)
                raise erro

            if isinstance(proximo, Exception):
                raise proximo

        return {
            "answer": "texto",
            "sources": [
                {"chunk_id": "c1", "title": "Protocolo", "score": 0.8}
            ],
            "triage": {
                "classificacao": self.classificacao,
                "justificativa": "porque sim",
                "sinais_de_alerta": ["febre"],
                "recomendacao": "procure atendimento",
                "fontes": [{"index": 1, "chunk_id": "c1"}],
                "json_parsed": True,
                "schema_valid": True,
                "attempts": 1,
                "done_reason": "stop",
                "invalid_source_indices": [],
            },
            "retrieval": {
                "returned_count": 3,
                "used_count": 1,
                "above_threshold_count": 1,
                "max_score": 0.8,
                "threshold": 0.7,
            },
            "config": {"model": "modelo-de-teste", "seed": 42},
            "timings": {"total_s": 1.0, "prompt_tokens": 100},
            "debug": {"queries": ["consulta"]},
        }


# ----------------------------------------------------------------------
# Regressão dos relatos
# ----------------------------------------------------------------------


def test_relatos_identicos_aos_de_04_05():
    """
    Compara o texto gerado hoje com os 98 relatos registrados na medição
    antiga. Se divergir, os resultados novos não são comparáveis com ela.
    """

    historico = pd.read_csv(RESULTADO_HISTORICO).set_index("index")
    atual = runner.carregar_dataset()

    assert len(historico) == 98

    for row_id, linha_historica in historico.iterrows():
        assert runner.build_relato(atual.loc[row_id]) == (
            linha_historica["relato"]
        )


def test_rotulo_esperado_vem_da_coluna_dangerous():

    assert runner.get_expected_label("Yes") == "EMERGENCIA"
    assert runner.get_expected_label("No") == "NAO_EMERGENCIA"
    assert runner.get_expected_label("") == "INVALID_LABEL"


# ----------------------------------------------------------------------
# Configuração
# ----------------------------------------------------------------------


def test_coercao_dos_tipos_da_linha_de_comando():

    assert runner.coagir("true") is True
    assert runner.coagir("False") is False
    assert runner.coagir("none") is None
    assert runner.coagir("3") == 3
    assert runner.coagir("0.8") == 0.8
    assert runner.coagir("v0_legacy") == "v0_legacy"


def test_ajuste_sobrescreve_o_preset():

    opcoes = runner.montar_opcoes("naive_rag", ["hyde_enabled=true"])

    assert opcoes["hyde_enabled"] is True
    assert opcoes["retrieval_enabled"] is True


def test_opcao_desconhecida_falha_antes_de_qualquer_requisicao():
    """
    Um erro de digitação aceito em silêncio produziria uma rodada inteira
    medindo a configuração padrão, sem ninguém perceber.
    """

    with pytest.raises(SystemExit, match="não existe"):
        runner.montar_opcoes("llm_only", ["hyde_enable=true"])

    with pytest.raises(SystemExit, match="chave=valor"):
        runner.montar_opcoes("llm_only", ["hyde_enabled"])


def test_preset_inexistente_falha_com_a_lista_de_opcoes():

    with pytest.raises(SystemExit, match="Disponíveis"):
        runner.montar_opcoes("inventado", [])


def test_presets_declarados_usam_apenas_opcoes_validas():

    for nome, opcoes in runner.carregar_presets().items():
        desconhecidas = set(opcoes) - runner.OPCOES_VALIDAS
        assert not desconhecidas, f"preset {nome}: {desconhecidas}"


# ----------------------------------------------------------------------
# Seleção
# ----------------------------------------------------------------------


def test_subconjuntos_mantem_as_duas_classes():

    df = runner.carregar_dataset()

    for subset, minimo in (("smoke", 20), ("balanced", 50)):
        escolhido = runner.selecionar(df, subset, None)
        classes = escolhido["Dangerous"].value_counts()

        assert len(escolhido) >= minimo
        assert classes.get("Yes", 0) > 0
        assert classes.get("No", 0) > 0

    assert len(runner.selecionar(df, "full", None)) == 98


def test_amostragem_e_deterministica():

    df = runner.carregar_dataset()

    primeira = list(runner.selecionar(df, "smoke", None).index)
    segunda = list(runner.selecionar(df, "smoke", None).index)

    assert primeira == segunda


# ----------------------------------------------------------------------
# Achatamento da resposta
# ----------------------------------------------------------------------


def test_saida_nao_estruturada_vira_invalid_json():
    """
    Quando o modelo falha, a API devolve INCERTO com schema_valid falso. A
    avaliação precisa contar isso como saída inválida, que é a taxonomia da
    medição de 04/05.
    """

    resposta = {
        "triage": {
            "classificacao": "INCERTO",
            "schema_valid": False,
            "json_parsed": False,
            "attempts": 2,
        },
        "sources": [],
    }

    linha = runner.achatar(resposta, {"row_id": 1})

    assert linha["predicted"] == "INVALID_JSON"
    assert linha["classificacao_raw"] == "INCERTO"
    assert linha["attempts"] == 2


def test_incerto_legitimo_continua_incerto():

    resposta = {
        "triage": {"classificacao": "INCERTO", "schema_valid": True},
        "sources": [],
    }

    assert runner.achatar(resposta, {})["predicted"] == "INCERTO"


def test_resposta_sem_recuperacao_nao_inventa_numeros():

    resposta = {
        "triage": {"classificacao": "EMERGENCIA", "schema_valid": True},
        "sources": [],
        "retrieval": {"returned_count": 0, "max_score": None},
    }

    linha = runner.achatar(resposta, {})

    assert linha["n_sources_used"] == 0
    assert linha["retrieval_max_score"] is None


# ----------------------------------------------------------------------
# Execução, retomada e falhas
# ----------------------------------------------------------------------


def preparar(tmp_path, cliente, repeticoes=1, base_seed=None, linhas=2):

    manifesto = {
        "run_id": "teste",
        "requested_options": {"retrieval_enabled": False},
        "repeats": repeticoes,
    }

    df = runner.carregar_dataset().head(linhas)

    runner.executar_rodada(
        tmp_path, manifesto, df, cliente, repeticoes, base_seed
    )

    return runner.ler_previsoes(tmp_path / "predictions.jsonl")


def test_rodada_grava_uma_linha_por_relato(tmp_path):

    registros = preparar(tmp_path, ClienteFalso())

    assert len(registros) == 2
    assert all(r["status"] == "ok" for r in registros)
    assert all(r["predicted"] == "EMERGENCIA" for r in registros)


def test_seed_avanca_a_cada_repeticao(tmp_path):
    """
    Sem seed diferente por repetição, a API usa a seed fixa e as repetições
    viram cópias da mesma execução — medindo nada.
    """

    cliente = ClienteFalso()

    preparar(tmp_path, cliente, repeticoes=2, base_seed=1000, linhas=1)

    seeds = [c["options"]["seed"] for c in cliente.chamadas]

    assert seeds == [1000, 1001]


def test_sem_base_seed_a_api_decide(tmp_path):

    cliente = ClienteFalso()

    preparar(tmp_path, cliente, linhas=1)

    assert "seed" not in cliente.chamadas[0]["options"]


def test_depuracao_e_sempre_pedida(tmp_path):
    """
    O bloco de depuração traz as consultas geradas e a saída bruta; sem ele
    não é possível investigar depois por que uma linha errou.
    """

    cliente = ClienteFalso()

    preparar(tmp_path, cliente, linhas=1)

    assert cliente.chamadas[0]["options"]["include_debug"] is True


def test_configuracao_inaceitavel_aborta_a_rodada(tmp_path):
    """
    Erro de configuração não é dado: melhor parar do que gravar 98 linhas
    de uma medição que não é a pedida.
    """

    with pytest.raises(SystemExit, match="recusou a configuração"):
        preparar(tmp_path, ClienteFalso(roteiro=[400]), linhas=1)


def test_falha_transitoria_e_repetida_e_a_linha_e_salva(
    tmp_path, monkeypatch
):

    monkeypatch.setattr(runner, "ESPERAS", [0, 0, 0])

    registros = preparar(
        tmp_path,
        ClienteFalso(roteiro=[502]),
        linhas=1,
    )

    assert len(registros) == 1
    assert registros[0]["status"] == "ok"


def test_falhas_seguidas_abortam_a_rodada(tmp_path, monkeypatch):

    monkeypatch.setattr(runner, "ESPERAS", [0, 0, 0])

    erro = ConnectionError("api fora do ar")

    with pytest.raises(SystemExit, match="falharam"):
        preparar(
            tmp_path,
            ClienteFalso(roteiro=[erro] * 40),
            linhas=5,
        )


def test_mudanca_de_configuracao_no_meio_aborta(tmp_path):
    """
    Um backend reiniciado com outro .env produziria linhas incomparáveis
    dentro da mesma rodada.
    """

    class ClienteQueMuda(ClienteFalso):
        def classify(self, relato, options):
            resposta = super().classify(relato, options)
            resposta["config"] = {
                "model": f"modelo-{len(self.chamadas)}",
                "seed": 42,
            }
            return resposta

    with pytest.raises(SystemExit, match="configuração efetiva mudou"):
        preparar(tmp_path, ClienteQueMuda(), linhas=3)


def test_retomada_nao_refaz_o_que_ja_foi_feito(tmp_path):

    cliente = ClienteFalso()

    preparar(tmp_path, cliente, linhas=2)

    assert len(cliente.chamadas) == 2

    # Segunda passada no mesmo diretório: nada a fazer.
    preparar(tmp_path, cliente, linhas=2)

    assert len(cliente.chamadas) == 2


def test_ultima_linha_truncada_e_refeita(tmp_path):
    """
    Uma interrupção no meio da escrita deixa a última linha pela metade.
    Ela precisa ser descartada e refeita, sem derrubar a retomada.
    """

    caminho = tmp_path / "predictions.jsonl"

    completa = {
        "row_id": 0,
        "repeat": 0,
        "status": "ok",
        "predicted": "EMERGENCIA",
    }

    caminho.write_text(
        json.dumps(completa) + "\n" + '{"row_id": 1, "repe',
        encoding="utf-8",
    )

    assert runner.ler_previsoes(caminho) == [completa]

    cliente = ClienteFalso()
    registros = preparar(tmp_path, cliente, linhas=2)

    ids = sorted(r["row_id"] for r in registros)

    assert ids == [0, 1]
    assert len(cliente.chamadas) == 1


def test_linha_com_erro_e_refeita_na_retomada(tmp_path, monkeypatch):

    monkeypatch.setattr(runner, "ESPERAS", [0, 0, 0])

    erro = ConnectionError("instabilidade")

    preparar(tmp_path, ClienteFalso(roteiro=[erro] * 4), linhas=1)

    registros = runner.ler_previsoes(tmp_path / "predictions.jsonl")
    assert registros[0]["status"] == "error"

    cliente = ClienteFalso()
    registros = preparar(tmp_path, cliente, linhas=1)

    assert len(cliente.chamadas) == 1
    assert [r["status"] for r in registros] == ["ok"]


def test_escrita_atomica_substitui_o_arquivo(tmp_path):

    caminho = tmp_path / "manifest.json"

    runner.escrever_atomico(caminho, '{"a": 1}')
    runner.escrever_atomico(caminho, '{"a": 2}')

    assert json.loads(caminho.read_text(encoding="utf-8")) == {"a": 2}
    assert list(tmp_path.iterdir()) == [caminho]


def test_limite_preserva_as_duas_classes():
    """
    As emergências ocupam os menores índices do arquivo, então um corte
    pelas primeiras linhas traria só uma classe — e acurácia medida sobre
    uma classe só não diz nada.
    """

    df = runner.carregar_dataset()

    escolhido = runner.selecionar(df, "smoke", 4)

    classes = escolhido["Dangerous"].value_counts()

    assert len(escolhido) == 4
    assert classes.get("Yes", 0) == 2
    assert classes.get("No", 0) == 2
