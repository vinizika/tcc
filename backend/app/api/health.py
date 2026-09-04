from fastapi import APIRouter

from app.services.fingerprint_service import FingerprintService

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
def health():
    return {
        "status": "ok"
    }


@router.get("/fingerprint")
def fingerprint():
    """
    Identifica a versão exata do sistema que está respondendo.

    O runner de avaliação grava isto no manifesto de cada rodada. Sem essa
    identificação, duas rodadas com números diferentes não permitem
    distinguir "a mudança que fizemos funcionou" de "o modelo, a base de
    conhecimento ou os prompts mudaram no meio do caminho" — e o commit do
    repositório não serve como prova, porque o container pode estar rodando
    uma versão anterior do código.
    """

    return FingerprintService.collect()
