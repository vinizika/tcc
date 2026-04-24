from fastapi import FastAPI
from pydantic import BaseModel
from app.llm import chamar_llm_triagem


app = FastAPI(title="TCC Vet RAG API")


class TriagemRequest(BaseModel):
    relato: str
    especie: str | None = None
    idade: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triagem")
def triagem(payload: TriagemRequest):
    resposta = chamar_llm_triagem(
        relato=payload.relato,
        especie=payload.especie,
        idade=payload.idade,
    )

    return {
        "entrada": payload.model_dump(),
        "resposta_modelo": resposta,
    }