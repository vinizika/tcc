import pytest

import run_ingestion_cycle as cycle


def test_plano_sem_ativacao_para_em_staging():
    result = cycle.plan("lote", "curated", False)

    assert "stop_after_staging" in result["steps"]
    assert "activate_candidate" not in result["steps"]
    assert "run_after_retrieval_evaluation" not in result["steps"]


def test_plano_com_ativacao_inclui_avaliacao_e_compare():
    result = cycle.plan("lote", "curated", True)

    assert "activate_candidate" in result["steps"]
    assert result["steps"][-2:] == ["compare_runs", "write_cycle_receipt"]


def test_comando_com_falha_interrompe_ciclo(monkeypatch):
    class Result:
        returncode = 9
        stdout = ""
        stderr = ""

    monkeypatch.setattr(cycle.subprocess, "run", lambda *args, **kwargs: Result())

    with pytest.raises(cycle.CycleError, match=r"Etapa falhou \(9\)"):
        cycle.run_command(["python", "etapa.py"])


def test_fingerprint_precisa_ser_objeto(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return []

    monkeypatch.setattr(cycle.requests, "get", lambda *args, **kwargs: Response())

    with pytest.raises(cycle.CycleError, match="não é um objeto"):
        cycle.api_fingerprint("http://api", 10)


def test_nome_do_ciclo_nao_aceita_caminho():
    with pytest.raises(cycle.CycleError, match="slug"):
        cycle.execute_cycle(
            name="../fora",
            profile="curated",
            api_url="http://api",
            timeout=10,
            activate=False,
        )
