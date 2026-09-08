"""
A única implementação de Whisper do projeto.

Estes testes fixam o contrato do `VoiceService` sem carregar um modelo real:
o tamanho vem das settings e a saída é (texto, idioma, duração).
"""

from pathlib import Path

import pytest

from app.services import voice_service
from app.services.voice_service import VoiceService


class _Segmento:

    def __init__(self, text: str):
        self.text = text


class _Info:
    language = "pt"
    language_probability = 0.98
    duration = 2.5


@pytest.fixture(autouse=True)
def _modelo_limpo(monkeypatch):
    # O modelo é estado de classe; garante que cada teste parte do zero e não
    # deixa um dublê para o próximo.
    monkeypatch.setattr(VoiceService, "_model", None)
    yield
    VoiceService._model = None


def test_load_model_usa_o_tamanho_das_settings(monkeypatch):

    capturado = {}

    class ModeloFalso:
        def __init__(self, size, **kwargs):
            capturado["size"] = size
            capturado["kwargs"] = kwargs

    monkeypatch.setattr(voice_service, "WhisperModel", ModeloFalso)
    monkeypatch.setattr(voice_service.settings, "WHISPER_MODEL_SIZE", "tiny")

    VoiceService.load_model()

    assert capturado["size"] == "tiny"
    assert capturado["kwargs"] == {"device": "cpu", "compute_type": "int8"}


def test_load_model_carrega_uma_vez_so(monkeypatch):

    contador = {"n": 0}

    class ModeloFalso:
        def __init__(self, *args, **kwargs):
            contador["n"] += 1

    monkeypatch.setattr(voice_service, "WhisperModel", ModeloFalso)

    VoiceService.load_model()
    VoiceService.load_model()

    assert contador["n"] == 1


def test_transcribe_junta_os_segmentos_e_devolve_idioma_e_duracao(monkeypatch):

    class ModeloFalso:
        def transcribe(self, caminho, **kwargs):
            assert kwargs["language"] == "pt"
            return [_Segmento("  meu cão "), _Segmento(" comeu chocolate  ")], _Info()

    monkeypatch.setattr(VoiceService, "_model", ModeloFalso())

    texto, idioma, duracao = VoiceService.transcribe(Path("relato.wav"))

    assert texto == "meu cão comeu chocolate"
    assert idioma == "pt"
    assert duracao == 2.5
