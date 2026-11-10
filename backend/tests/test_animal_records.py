"""
Histórico do animal no app (rodada 34 do João): ler um documento, guardar o
resumo revisado, listar, remover e levar à análise, junto das conversas
anteriores do mesmo animal. O que muda no prompt está em
`test_prompt_historico.py`.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import mongomock
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from conftest import LLMClientFalso, QueryClientFalso, RerankerFalso, RetrievalClientFalso, documento

from app.clients.gemini_llm_client import GeminiLLMClient
from app.core.config import settings as runtime
from app.main import app
from app.pipeline.chat_pipeline import ChatPipeline
from app.prompts.triage import REGRA_HISTORICO
from app.repositories import workflow_repository
from app.schemas.auth import Principal
from app.schemas.workspace import AnimalInput, DocumentInput, TurnInput
from app.services import animal_records_service as records
from app.services import poc_identity, workspace_service
from app.services.auth_service import DEMO_ACCOUNTS
from app.services.workspace_service import WorkspaceService as Workspace

# --- Leitura do documento -----------------------------------------------------

def _pdf(linhas, paginas=1):
    import pymupdf
    doc = pymupdf.open()
    for _ in range(paginas):
        pagina = doc.new_page()
        for i, linha in enumerate(linhas):
            pagina.insert_text((50, 70 + i * 20), linha, fontsize=11)
    return doc.tobytes()


EXAME = ["Laboratório veterinário (teste)", "Paciente: Mel, canina, 9 anos", "Creatinina 2,9 mg/dL (referência 0,5 a 1,5) ALTO",
         "Ureia 112 mg/dL (referência 21 a 60) ALTO", "Compatível com doença renal crônica. Em uso de benazepril."]
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


class LeitorFalso:
    def __init__(self, fatos):
        self.fatos, self.chamadas = fatos, []

    def read_document(self, data, mime_type, instruction, output_model):
        self.chamadas.append({"bytes": len(data), "mime": mime_type, "instruction": instruction})
        return self.fatos


def _fatos(**campos):
    base = dict(e_documento_veterinario=True, legivel=True, tipo_de_documento="Exame laboratorial", data_do_documento="02/11/2026",
                diagnosticos_ou_suspeitas=["doença renal crônica"], resultados_alterados=["creatinina 2,9 mg/dL (alto)"],
                medicacoes_em_uso=["benazepril 5 mg 1x/dia"], alergias=["dipirona"])
    return records.DocumentFacts(**(base | campos))


def test_tipo_do_arquivo_vem_do_conteudo():

    assert records.detect_type(_pdf(EXAME)) == "application/pdf"
    assert records.detect_type(b"\xff\xd8\xff\xe0resto") == "image/jpeg"
    assert records.detect_type(PNG) == "image/png"
    assert records.detect_type(b"RIFF\x00\x00\x00\x00WEBPVP8 ") == "image/webp"
    assert records.detect_type(b"MZ\x90\x00executavel") is None


def test_gemini_le_o_arquivo_e_o_resumo_sai_por_regra():

    leitor = LeitorFalso(_fatos())
    lido = records.read_document(PNG, "exame da mel.png", "gemini", client=leitor)

    assert leitor.chamadas == [{"bytes": len(PNG), "mime": "image/png", "instruction": records.INSTRUCAO_DE_LEITURA}]
    assert lido == {"name": "exame da mel.png", "kind": "Exame laboratorial", "document_date": "02/11/2026", "source": "gemini", "notice": "",
                    "summary": "Diagnósticos ou suspeitas: doença renal crônica. Resultados alterados: creatinina 2,9 mg/dL (alto). "
                               "Medicações em uso: benazepril 5 mg 1x/dia. Alergias: dipirona."}
    assert "não instrução" in records.INSTRUCAO_DE_LEITURA and "CPF" in records.INSTRUCAO_DE_LEITURA


@pytest.mark.parametrize("fatos, trecho", [
    (None, "Não foi possível ler"),
    (_fatos(legivel=False), "Não foi possível ler"),
    (_fatos(e_documento_veterinario=False), "não parece um documento veterinário"),
    (_fatos(diagnosticos_ou_suspeitas=[], resultados_alterados=[], medicacoes_em_uso=[], alergias=[]), "Não encontramos informação clínica"),
])
def test_documento_que_nao_serve_e_recusado_com_motivo(fatos, trecho):

    with pytest.raises(HTTPException) as erro:
        records.read_document(PNG, "x.png", "gemini", client=LeitorFalso(fatos))

    assert erro.value.status_code == 422 and trecho in erro.value.detail


def test_modelo_local_aproveita_so_o_texto_do_pdf():

    lido = records.read_document(_pdf(EXAME), "exame.pdf", "ollama")

    assert lido["source"] == "pdf_text" and "Creatinina 2,9 mg/dL" in lido["summary"]
    assert "sem resumo" in lido["notice"]
    assert len(lido["summary"]) <= records.MAX_SUMMARY_CHARS

    for arquivo, trecho in ((PNG, "não lê imagens"), (_pdf(["a"]), "não tem texto selecionável")):
        with pytest.raises(HTTPException) as erro:
            records.read_document(arquivo, "x", "ollama")
        assert erro.value.status_code == 422 and trecho in erro.value.detail


def test_arquivo_vazio_de_outro_tipo_ou_longo_demais():

    for arquivo, status in ((b"", 422), (b"MZ\x90\x00", 415), (_pdf(EXAME, paginas=records.MAX_PDF_PAGES + 1), 413), (b"%PDF-1.7 lixo", 422)):
        with pytest.raises(HTTPException) as erro:
            records.read_document(arquivo, "x", "gemini", client=LeitorFalso(_fatos()))
        assert erro.value.status_code == status


def test_cliente_gemini_envia_o_arquivo_e_valida_a_saida(monkeypatch):
    from test_gemini_atendente import GenaiClientFalso

    monkeypatch.setattr(runtime, "GEMINI_MIN_INTERVAL_S", 0.0)
    valido = _fatos().model_dump_json()
    falso = GenaiClientFalso(["isto não é json", valido])
    fatos = GeminiLLMClient(client=falso, dormir=lambda _: None).read_document(PNG, "image/png", "leia", records.DocumentFacts)

    assert fatos.alergias == ["dipirona"]
    assert len(falso.models.chamadas) == 2  # a 1ª saída veio inválida
    arquivo, pedido = falso.models.chamadas[0]["contents"]
    assert pedido == "leia" and arquivo.inline_data.mime_type == "image/png"

    sempre_invalido = GenaiClientFalso(["x", "y"])
    assert GeminiLLMClient(client=sempre_invalido, dormir=lambda _: None).read_document(PNG, "image/png", "leia", records.DocumentFacts) is None


# --- O bloco que vai ao prompt -------------------------------------------------

def test_sem_documento_e_sem_conversa_nao_ha_bloco():

    assert records.records_block([], []) == (None, None)


def test_bloco_traz_documentos_e_conversas_e_diz_o_que_usou():

    docs = [{"id": "d1", "kind": "Exame laboratorial", "document_date": "02/11/2026", "summary": "Resultados alterados: creatinina alta."}]
    hist = [{"conversation_id": "c1", "date": "08/11/2026", "ago": "ontem", "report": "Não consegue andar.", "classification": "EMERGENCIA"}]
    bloco, usado = records.records_block(docs, hist)

    assert bloco == ("Documentos enviados pelo tutor:\n"
                     "- Exame laboratorial, 02/11/2026: Resultados alterados: creatinina alta.\n"
                     "Conversas anteriores sobre este animal neste aplicativo:\n"
                     '- 08/11/2026 (ontem): o tutor relatou: "Não consegue andar." Classificação na ocasião: EMERGENCIA.')
    assert usado == {"documents": [{"id": "d1", "kind": "Exame laboratorial", "document_date": "02/11/2026"}],
                     "history": [{"conversation_id": "c1", "date": "08/11/2026", "classification": "EMERGENCIA"}]}


def test_bloco_respeita_o_teto_e_registra_so_o_que_coube():

    docs = [{"id": f"d{i}", "kind": "Exame", "document_date": "", "summary": "x" * 1100} for i in range(6)]
    bloco, usado = records.records_block(docs, [])

    assert len(bloco) <= records.MAX_BLOCK_CHARS + 40
    assert [d["id"] for d in usado["documents"]] == ["d0", "d1", "d2"]


# --- No app: guardar, listar, remover e usar ----------------------------------

@pytest.fixture
def env(monkeypatch):
    db = mongomock.MongoClient(tz_aware=True).test
    monkeypatch.setattr(runtime, "WORKFLOW_MODE", "poc")
    monkeypatch.setattr(runtime, "AUTH_PROVIDER", "local")
    monkeypatch.setattr(runtime, "POC_QUICK_LOGIN_ENABLED", True)
    monkeypatch.setattr(runtime, "ANIMAL_RECORDS_ENABLED", True)
    monkeypatch.setattr(workspace_service, "get_mongo_database", lambda: db)
    monkeypatch.setattr(workspace_service, "active_collection_name", lambda: "fichas-test-collection")
    monkeypatch.setattr(poc_identity, "get_mongo_database", lambda: db)
    monkeypatch.setattr(workflow_repository, "get_mongo_database", lambda: db)
    monkeypatch.setattr(workflow_repository, "_mongo_repository", workflow_repository.MongoWorkflowRepository())
    proprio = Principal(user_id="tutor-proprio", role="tutor", display_name="Tutor com conta própria")
    return SimpleNamespace(db=db, client=TestClient(app), tutor=proprio, demo=DEMO_ACCOUNTS["tutor-a"], outro=DEMO_ACCOUNTS["tutor-b"])


def headers(client, account="tutor-a"):
    return {"Authorization": "Bearer " + client.post("/auth/demo", json={"account": account}).json()["access_token"]}


RESUMO = {"name": "exame.pdf", "kind": "Exame laboratorial", "document_date": "02/11/2026",
          "summary": "Diagnósticos ou suspeitas: doença renal crônica.", "source": "gemini"}


def _analisar(env, conversa_id, relato, request_id):
    """Roda a análise com o pipeline de verdade e um modelo falso; devolve o que o modelo recebeu."""
    Workspace.submit(env.tutor, conversa_id, TurnInput(content=relato, request_id=request_id))
    llm = LLMClientFalso()
    busca = RetrievalClientFalso([documento()])
    pipeline = ChatPipeline(query_client=QueryClientFalso(), retrieval_client=busca, reranker=RerankerFalso, llm_client=llm)
    Workspace.process(env.tutor, conversa_id, request_id, pipeline=pipeline)
    return llm.chamadas[0]["messages"], busca


def test_documento_fica_no_animal_e_vale_para_as_proximas_conversas(env):
    c, h = env.client, headers(env.client)
    pet = c.post("/workspace/pets", json={"name": "Mel", "species": "cao"}, headers=h).json()
    conversa = c.post("/workspace/conversations", json={"pet_id": pet["id"]}, headers=h).json()

    r = c.post(f"/workspace/conversations/{conversa['id']}/documents", json=RESUMO, headers=h)

    assert r.status_code == 201
    contexto = r.json()
    assert contexto["scope"] == "pet" and contexto["pet_name"] == "Mel"
    assert [d["kind"] for d in contexto["documents"]] == ["Exame laboratorial"]
    assert c.get("/workspace/pets", headers=h).json()[0]["documents"][0]["summary"] == RESUMO["summary"]
    # Editar o cadastro não apaga os documentos, e a cópia da conversa não os carrega.
    c.put(f"/workspace/pets/{pet['id']}", json={"name": "Mel", "species": "cao", "age": "9 anos"}, headers=h)
    assert len(c.get("/workspace/pets", headers=h).json()[0]["documents"]) == 1
    nova = c.post("/workspace/conversations", json={"pet_id": pet["id"]}, headers=h).json()
    assert "documents" not in nova["pet"]
    assert len(c.get("/workspace/context", params={"conversation_id": nova["id"]}, headers=h).json()["documents"]) == 1

    doc_id = contexto["documents"][0]["id"]
    assert c.delete(f"/workspace/pets/{pet['id']}/documents/{doc_id}", headers=h).json()["documents"] == []
    assert c.delete(f"/workspace/pets/{pet['id']}/documents/{doc_id}", headers=h).status_code == 404


def test_sem_animal_o_documento_fica_so_na_conversa(env):
    c, h = env.client, headers(env.client)
    conversa = c.post("/workspace/conversations", json={}, headers=h).json()
    antes = c.get(f"/workspace/conversations/{conversa['id']}", headers=h).json()["updated_at"]

    contexto = c.post(f"/workspace/conversations/{conversa['id']}/documents", json=RESUMO, headers=h).json()

    assert contexto["scope"] == "conversation" and len(contexto["documents"]) == 1
    depois = c.get(f"/workspace/conversations/{conversa['id']}", headers=h).json()
    assert depois["updated_at"] == antes  # a trava do envio de mensagem não foi tocada
    outra = c.post("/workspace/conversations", json={}, headers=h).json()
    assert c.get("/workspace/context", params={"conversation_id": outra["id"]}, headers=h).json()["documents"] == []
    doc_id = contexto["documents"][0]["id"]
    assert c.delete(f"/workspace/conversations/{conversa['id']}/documents/{doc_id}", headers=h).json()["documents"] == []


def test_documentos_sao_de_quem_enviou_e_tem_limite(env):
    c, a, b = env.client, headers(env.client), headers(env.client, "tutor-b")
    pet = c.post("/workspace/pets", json={"name": "Mel", "species": "cao"}, headers=a).json()
    conversa = c.post("/workspace/conversations", json={"pet_id": pet["id"]}, headers=a).json()
    doc_id = c.post(f"/workspace/pets/{pet['id']}/documents", json=RESUMO, headers=a).json()["documents"][0]["id"]

    assert c.post(f"/workspace/pets/{pet['id']}/documents", json=RESUMO, headers=b).status_code == 404
    assert c.delete(f"/workspace/pets/{pet['id']}/documents/{doc_id}", headers=b).status_code == 404
    assert c.get("/workspace/context", params={"pet_id": pet["id"]}, headers=b).status_code == 404
    assert c.get("/workspace/context", params={"conversation_id": conversa["id"]}, headers=b).status_code == 404
    assert c.post(f"/workspace/pets/{pet['id']}/documents", json=RESUMO, headers=headers(c, "clinic-a")).status_code == 403
    assert c.post(f"/workspace/pets/{pet['id']}/documents", json=RESUMO | {"summary": "x" * 1201}, headers=a).status_code == 422

    for _ in range(records.MAX_DOCUMENTS - 1):
        assert c.post(f"/workspace/pets/{pet['id']}/documents", json=RESUMO, headers=a).status_code == 201
    assert c.post(f"/workspace/pets/{pet['id']}/documents", json=RESUMO, headers=a).status_code == 409


def test_leitura_exige_tutor_e_respeita_tamanho_e_tipo(env, monkeypatch):
    c, h = env.client, headers(env.client)
    arquivo = {"file": ("exame.pdf", _pdf(EXAME), "application/pdf")}

    assert c.post("/workspace/documents/read", files=arquivo).status_code == 401
    assert c.post("/workspace/documents/read", files=arquivo, headers=headers(c, "clinic-a")).status_code == 403
    assert c.post("/workspace/documents/read", files={"file": ("x.exe", b"MZ\x90\x00", "application/pdf")}, headers=h).status_code == 415

    lido = c.post("/workspace/documents/read", files=arquivo, data={"attendant_provider": "ollama"}, headers=h)
    assert lido.status_code == 200 and lido.json()["source"] == "pdf_text"
    assert env.db.poc_pets.count_documents({}) == 0  # ler não guarda nada

    monkeypatch.setattr(runtime, "MAX_DOCUMENT_UPLOAD_MB", 1)
    grande = {"file": ("grande.pdf", b"%PDF-" + b"0" * (1024 * 1024 + 10), "application/pdf")}
    assert c.post("/workspace/documents/read", files=grande, headers=h).status_code == 413


def test_conversas_anteriores_do_mesmo_animal_entram_no_historico(env):
    mel = Workspace.save_pet(env.tutor, AnimalInput(name="Mel", species="cao"))
    lua = Workspace.save_pet(env.tutor, AnimalInput(name="Lua", species="gato"))
    agora = datetime.now(timezone.utc)

    def conversa(pet_id, relato, classificacao, dias_atras, dono=env.tutor):
        c = Workspace.create(dono, pet_id) if dono is env.tutor else {"id": "de-outro", "owner_id": dono.user_id, "pet_id": pet_id}
        campos = {"created_at": (agora - timedelta(days=dias_atras)).isoformat(),
                  "messages": [{"id": "m", "role": "tutor", "content": relato, "created_at": agora.isoformat()}]}
        if classificacao:
            campos["latest_triage"] = {"classificacao": classificacao}
        if dono is env.tutor:
            env.db.poc_conversations.update_one({"id": c["id"]}, {"$set": campos})
        else:
            env.db.poc_conversations.insert_one(c | campos)
        return c["id"]

    conversa(mel["id"], "Não consegue andar com as patas de trás. " + "detalhe " * 60, "EMERGENCIA", 1)
    conversa(mel["id"], "Espirrou duas vezes.", "NAO_EMERGENCIA", 12)
    conversa(mel["id"], "Rascunho sem análise.", None, 2)
    conversa(lua["id"], "A Lua vomitou.", "INCERTO", 1)
    conversa(mel["id"], "Conversa de outra conta.", "EMERGENCIA", 1, dono=env.outro)
    atual = conversa(mel["id"], "Está mais quieta hoje.", "NAO_EMERGENCIA", 0)

    historico = records.history_of(env.db, env.tutor.user_id, mel["id"], atual)

    assert [(h["ago"], h["classification"]) for h in historico] == [("ontem", "EMERGENCIA"), ("há 12 dias", "NAO_EMERGENCIA")]
    assert historico[0]["report"].startswith("Não consegue andar") and len(historico[0]["report"]) <= records.HISTORY_REPORT_CHARS
    assert records.history_of(env.db, env.tutor.user_id, None, atual) == []

    for dia in range(3, 3 + records.HISTORY_LIMIT + 2):
        conversa(mel["id"], f"Relato do dia {dia}.", "NAO_EMERGENCIA", dia)
    assert len(records.history_of(env.db, env.tutor.user_id, mel["id"], atual)) == records.HISTORY_LIMIT


def test_analise_recebe_documento_e_conversa_anterior_e_registra_o_que_usou(env):
    pet = Workspace.save_pet(env.tutor, AnimalInput(name="Mel", species="cao", age="9 anos"))
    primeira = Workspace.create(env.tutor, pet["id"])
    mensagens, _ = _analisar(env, primeira["id"], "A Mel não consegue andar com as patas de trás.", "primeira-conversa-1")
    assert "Histórico do animal" not in str(mensagens) and REGRA_HISTORICO not in mensagens[0]["content"]
    assert "context_used" not in Workspace.get(env.tutor, primeira["id"])["messages"][-1]

    Workspace.add_document(env.tutor, DocumentInput(**RESUMO), pet_id=pet["id"])
    segunda = Workspace.create(env.tutor, pet["id"])
    mensagens, busca = _analisar(env, segunda["id"], "A Mel está mais quieta hoje.", "segunda-conversa-1")

    sistema, usuario = mensagens[0]["content"], mensagens[-1]["content"]
    assert REGRA_HISTORICO in sistema
    assert "- Exame laboratorial, 02/11/2026: Diagnósticos ou suspeitas: doença renal crônica." in usuario
    assert '(hoje): o tutor relatou: "A Mel não consegue andar com as patas de trás."' in usuario
    assert "name: Mel; species: cao; age: 9 anos" in usuario
    # A busca recebe só o relato de hoje: nem documento nem conversa anterior.
    consulta = str(busca.chamadas)
    assert "A Mel está mais quieta hoje." in consulta and "renal" not in consulta and "patas de trás" not in consulta
    usado = Workspace.get(env.tutor, segunda["id"])["messages"][-1]["context_used"]
    assert [d["kind"] for d in usado["documents"]] == ["Exame laboratorial"]
    assert [h["conversation_id"] for h in usado["history"]] == [primeira["id"]]


def test_conta_academica_compartilhada_usa_documento_mas_nao_conversas_de_outros(env):
    pet = Workspace.save_pet(env.demo, AnimalInput(name="Thor", species="cao"))
    anterior = Workspace.create(env.demo, pet["id"])
    env.db.poc_conversations.update_one({"id": anterior["id"]}, {"$set": {
        "latest_triage": {"classificacao": "EMERGENCIA"},
        "messages": [{"id": "m", "role": "tutor", "content": "Relato de outra pessoa na conta compartilhada.", "created_at": anterior["created_at"]}]}})
    Workspace.add_document(env.demo, DocumentInput(**RESUMO), pet_id=pet["id"])
    conversa = Workspace.create(env.demo, pet["id"])

    contexto = Workspace.context(env.demo, conversation_id=conversa["id"])
    assert len(contexto["documents"]) == 1 and contexto["history"] == []

    Workspace.submit(env.demo, conversa["id"], TurnInput(content="O Thor espirrou.", request_id="conta-compartilhada-1"))
    llm = LLMClientFalso()
    pipeline = ChatPipeline(query_client=QueryClientFalso(), retrieval_client=RetrievalClientFalso([documento()]), reranker=RerankerFalso, llm_client=llm)
    Workspace.process(env.demo, conversa["id"], "conta-compartilhada-1", pipeline=pipeline)
    usuario = llm.chamadas[0]["messages"][-1]["content"]
    assert "Exame laboratorial" in usuario and "Relato de outra pessoa" not in usuario


def test_desligado_o_app_volta_a_mandar_so_relato_e_cadastro(env, monkeypatch):
    monkeypatch.setattr(runtime, "ANIMAL_RECORDS_ENABLED", False)
    pet = Workspace.save_pet(env.tutor, AnimalInput(name="Mel", species="cao"))
    Workspace.add_document(env.tutor, DocumentInput(**RESUMO), pet_id=pet["id"])
    conversa = Workspace.create(env.tutor, pet["id"])

    mensagens, _ = _analisar(env, conversa["id"], "A Mel vomitou duas vezes.", "desligado-conversa-1")

    assert "Histórico do animal" not in str(mensagens) and REGRA_HISTORICO not in mensagens[0]["content"]


def test_sem_historico_o_pipeline_e_chamado_como_antes(env):
    """Um pipeline que não conhece `animal_records` (o de antes desta rodada) segue servindo."""

    class PipelineDeAntes(ChatPipeline):
        def execute(self, question, options=None, animal_context=None, *, retrieval_question=None):
            return super().execute(question, options, animal_context, retrieval_question=retrieval_question)

    conversa = Workspace.create(env.tutor)
    Workspace.submit(env.tutor, conversa["id"], TurnInput(content="Meu gato espirrou.", request_id="pipeline-de-antes-1"))
    pipeline = PipelineDeAntes(query_client=QueryClientFalso(), retrieval_client=RetrievalClientFalso([documento()]),
                               reranker=RerankerFalso, llm_client=LLMClientFalso())
    Workspace.process(env.tutor, conversa["id"], "pipeline-de-antes-1", pipeline=pipeline)

    assert Workspace.get(env.tutor, conversa["id"])["status"] == "idle"
