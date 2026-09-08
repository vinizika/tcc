"""
Contrato HTTP do /voice/.

O upload é entrada não confiável: o nome vem do cliente e o tamanho, sem
limite, fica à mercê dele. Estes testes fixam que o nome do cliente nunca
entra no caminho de escrita, que há teto de bytes e que nenhum arquivo
temporário sobrevive à requisição (evidencias/backlog.md#b-32).
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import voice
from app.main import app


class _Transcritor:
    """
    Dublê do Whisper. Registra o caminho recebido para os testes verificarem
    que o servidor gerou o nome, e pode ser configurado para falhar.
    """

    def __init__(self):
        self.resultado = ("relato transcrito", "pt", 3.2)
        self.erro: Exception | None = None
        self.caminhos: list[Path] = []

    def __call__(self, file_path):
        self.caminhos.append(Path(file_path))

        if self.erro is not None:
            raise self.erro

        return self.resultado


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(voice, "UPLOAD_FOLDER", tmp_path)
    return tmp_path


@pytest.fixture
def transcritor(monkeypatch):
    espia = _Transcritor()
    monkeypatch.setattr(voice.VoiceService, "transcribe", espia)
    return espia


@pytest.fixture
def client():
    return TestClient(app)


def _audio(nome="relato.wav", conteudo=b"conteudo de audio", tipo="audio/wav"):
    return {"audio": (nome, conteudo, tipo)}


def test_transcreve_e_remove_o_arquivo_temporario(
    client, upload_dir, transcritor
):

    resposta = client.post("/voice/", files=_audio())

    assert resposta.status_code == 200
    assert resposta.json() == {
        "transcription": "relato transcrito",
        "language": "pt",
        "duration": 3.2,
    }

    caminho = transcritor.caminhos[0]

    assert caminho.parent == upload_dir
    assert caminho.suffix == ".wav"
    assert "relato" not in caminho.name
    assert not caminho.exists()
    assert list(upload_dir.iterdir()) == []


def test_nome_do_cliente_nunca_entra_no_caminho_de_escrita(
    client, upload_dir, transcritor, tmp_path
):

    alvo = tmp_path.parent / "escrita_indevida.wav"

    resposta = client.post(
        "/voice/",
        files=_audio(nome="../../escrita_indevida.wav"),
    )

    assert resposta.status_code == 200

    caminho = transcritor.caminhos[0]

    assert caminho.parent == upload_dir
    assert caminho.suffix == ".wav"
    assert "escrita_indevida" not in caminho.name
    assert not alvo.exists()


def test_extensao_vem_do_tipo_quando_o_nome_nao_ajuda(
    client, upload_dir, transcritor
):

    resposta = client.post(
        "/voice/",
        files=_audio(nome="blob", tipo="audio/ogg"),
    )

    assert resposta.status_code == 200
    assert transcritor.caminhos[0].suffix == ".ogg"


def test_audio_acima_do_limite_e_recusado(
    client, upload_dir, transcritor, monkeypatch
):

    monkeypatch.setattr(voice.settings, "MAX_AUDIO_UPLOAD_MB", 1)

    resposta = client.post(
        "/voice/",
        files=_audio(conteudo=b"x" * (2 * 1024 * 1024)),
    )

    assert resposta.status_code == 413
    assert transcritor.caminhos == []
    assert list(upload_dir.iterdir()) == []


def test_arquivo_que_nao_e_audio_e_recusado(
    client, upload_dir, transcritor
):

    resposta = client.post(
        "/voice/",
        files=_audio(nome="notas.txt", conteudo=b"texto", tipo="text/plain"),
    )

    assert resposta.status_code == 415
    assert transcritor.caminhos == []
    assert list(upload_dir.iterdir()) == []


def test_audio_vazio_e_recusado(client, upload_dir, transcritor):

    resposta = client.post("/voice/", files=_audio(conteudo=b""))

    assert resposta.status_code == 422
    assert transcritor.caminhos == []
    assert list(upload_dir.iterdir()) == []


def test_falha_na_transcricao_ainda_remove_o_arquivo(upload_dir, transcritor):

    transcritor.erro = RuntimeError("modelo indisponível")

    cliente = TestClient(app, raise_server_exceptions=False)

    resposta = cliente.post("/voice/", files=_audio())

    assert resposta.status_code == 500
    assert transcritor.caminhos
    assert not transcritor.caminhos[0].exists()
    assert list(upload_dir.iterdir()) == []
