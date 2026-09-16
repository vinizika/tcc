"""Smoke test do caminho principal sem abrir navegador ou backend."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).parents[1] / "streamlit_app_mock.py"


def _click(app: AppTest, label: str) -> AppTest:
    next(button for button in app.button if button.label == label).click()
    return app.run()


def test_full_referral_flow_reaches_only_selected_clinic_dashboard():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception

    for label in (
        "Enviar relato",
        "Sim",
        "Encontrar clínicas próximas",
        "Visualizar detalhes",
        "Selecionar esta clínica",
    ):
        app = _click(app, label)
        assert not app.exception

    submit = next(
        button for button in app.button if button.label == "Concluir envio simulado"
    )
    assert submit.disabled
    app.checkbox[0].check()
    app = app.run()
    app = _click(app, "Concluir envio simulado")

    assert not app.exception
    assert any(
        "nenhum dado foi enviado a uma clínica real" in item.value
        for item in app.success
    )
    stores = app.session_state["demo"]["cases_by_clinic"]
    counts = [len(cases) for cases in stores.values()]
    assert counts == [1, 0, 0]

    app = _click(app, "Abrir painel da clínica selecionada")
    assert not app.exception
    assert app.metric[0].label == "Aguardando análise"
    assert app.metric[0].value == "1"
