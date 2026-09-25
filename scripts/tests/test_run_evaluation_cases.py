"""
O runner em lotes no formato da prova (`--cases`), rodada 25 do João.
Sem `--cases`, o runner faz o que fazia (os testes de test_run_evaluation.py
continuam valendo).
"""

import json

import pandas as pd
import pytest

import prova_freeze
import run_evaluation as runner
from test_run_evaluation import ClienteFalso


def _csv(tmp_path, linhas, nome="casos.csv"):
    caminho = tmp_path / nome
    pd.DataFrame(linhas).to_csv(caminho, index=False)
    return caminho


def test_cases_roda_o_lote_e_grava_o_id_textual(tmp_path, monkeypatch):
    caminho = _csv(tmp_path, [
        {"id": "p01", "text": "meu cão comeu chocolate", "expected_class": "EMERGENCIA",
         "topic": "chocolate_toxicosis", "split": "dev"},
        {"id": "p02", "text": "espirrou duas vezes", "expected_class": "NAO_EMERGENCIA",
         "topic": "mild_upper_respiratory_signs", "split": "dev"},
        {"id": "p03", "text": "outro lote", "expected_class": "NAO_EMERGENCIA",
         "topic": "", "split": "teste"},
    ])
    monkeypatch.setattr(runner, "DIRETORIO_RODADAS", tmp_path / "runs")
    cliente = ClienteFalso()
    monkeypatch.setattr(runner, "ApiClient", lambda *a, **k: cliente)

    runner.main(["--cases", str(caminho), "--split", "dev", "--preset", "llm_only", "--name", "t"])

    rodada = next((tmp_path / "runs").iterdir())
    manifesto = json.loads((rodada / "manifest.json").read_text(encoding="utf-8"))
    previsoes = runner.ler_previsoes(rodada / "predictions.jsonl")

    assert manifesto["cases"]["split"] == "dev"
    assert manifesto["cases"]["n"] == 2
    assert manifesto["row_ids"] == ["p01", "p02"]
    assert "dataset" not in manifesto
    assert manifesto["relato_lang"] == "pt"
    assert [p["row_id"] for p in previsoes] == ["p01", "p02"]
    assert previsoes[0]["expected"] == "EMERGENCIA"
    assert previsoes[0]["topic"] == "chocolate_toxicosis"
    # A primeira chamada é o aquecimento; depois, um relato por caso.
    assert [c["relato"] for c in cliente.chamadas][1:] == [
        "meu cão comeu chocolate",
        "espirrou duas vezes",
    ]


def test_cases_recusa_lote_congelado_que_mudou(tmp_path):
    linhas = [{"id": "p01", "text": "a", "expected_class": "EMERGENCIA", "split": "teste"}]
    caminho = _csv(tmp_path, linhas)
    prova_freeze.main(["--cases", str(caminho), "--split", "teste", "--freeze"])

    runner.carregar_casos(caminho, "teste")  # congelado e intacto: passa

    linhas[0]["text"] = "a, editado depois de congelar"
    _csv(tmp_path, linhas)

    with pytest.raises(SystemExit, match="congelamento"):
        runner.carregar_casos(caminho, "teste")


def test_cases_exige_as_colunas_do_formato(tmp_path):
    caminho = _csv(tmp_path, [{"id": "p01", "texto": "a"}])

    with pytest.raises(SystemExit, match="expected_class"):
        runner.carregar_casos(caminho)


def test_split_sem_cases_e_recusado():
    with pytest.raises(SystemExit):
        runner.main(["--split", "dev"])


def test_linha_grava_a_procedencia_do_atendente():
    resposta = ClienteFalso().classify("x", {})
    resposta["provenance"] = {
        "attendant": {"provider": "gemini", "model": "gemini-3.5-flash-lite",
                      "model_version": "v1", "thinking": None},
        "query_stage": {"calls": []},
    }
    resposta["sources"][0]["topic"] = "chocolate_toxicosis"

    linha = runner.achatar(resposta, {"row_id": "p01"})

    assert linha["attendant_provider"] == "gemini"
    assert linha["attendant_model_version"] == "v1"
    assert linha["attendant_fallback_from"] is None
    assert linha["used_topics"] == ["chocolate_toxicosis"]


def test_cota_esgotada_para_a_rodada_com_a_dica_do_resume(tmp_path, monkeypatch):
    import requests

    class Resposta503:
        status_code = 503
        text = "cota"

        def json(self):
            return {"code": "quota_exhausted", "details": {"provider": "gemini"}}

    class ClienteSemCota(ClienteFalso):
        def classify(self, relato, options):
            if len(self.chamadas) >= 1:
                erro = requests.HTTPError("HTTP 503")
                erro.response = Resposta503()
                self.chamadas.append({"relato": relato})
                raise erro
            return super().classify(relato, options)

    caminho = _csv(tmp_path, [
        {"id": "p01", "text": "a", "expected_class": "EMERGENCIA"},
        {"id": "p02", "text": "b", "expected_class": "NAO_EMERGENCIA"},
    ])
    monkeypatch.setattr(runner, "DIRETORIO_RODADAS", tmp_path / "runs")
    monkeypatch.setattr(runner, "ApiClient", lambda *a, **k: ClienteSemCota())

    with pytest.raises(SystemExit, match="--resume"):
        runner.main(["--cases", str(caminho), "--preset", "producao", "--name", "t"])
