from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.clients.supabase_client import get_supabase_client
from app.core.config import settings
from app.schemas.auth import Principal


DEMO_ACCOUNTS = {
    "tutor-a": Principal(user_id="demo-tutor-a", role="tutor", display_name="Ana (demo)", demo=True),
    "tutor-b": Principal(user_id="demo-tutor-b", role="tutor", display_name="Bruno (demo)", demo=True),
    "clinic-a": Principal(user_id="demo-clinic-user-a", role="clinic", display_name="Plantão Aurora (demo)", clinic_id="demo-clinic-a", clinic_verified=True, demo=True),
    "clinic-b": Principal(user_id="demo-clinic-user-b", role="clinic", display_name="Centro Vet Horizonte (demo)", clinic_id="demo-clinic-b", clinic_verified=True, demo=True),
    "clinic-pending": Principal(user_id="demo-clinic-pending", role="clinic", display_name="Clínica pendente (demo)", clinic_id="demo-clinic-pending", clinic_verified=False, demo=True),
}


def demo_token(account: str) -> str:
    return f"demo:{account}"


def _unauthorized(detail: str = "Sessão ausente ou inválida.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def _extract_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise _unauthorized()
    return authorization.removeprefix("Bearer ").strip()


def resolve_principal(token: str) -> Principal:
    if token.startswith("poc_"):
        from app.services.poc_identity import session_principal
        return session_principal(token)
    if settings.WORKFLOW_MODE == "demo":
        if not token.startswith("demo:"):
            raise _unauthorized("O modo demonstrativo aceita somente contas fictícias da tela de entrada.")
        account = token.split(":", 1)[1]
        principal = DEMO_ACCOUNTS.get(account)
        if not principal:
            raise _unauthorized()
        return principal

    if settings.WORKFLOW_MODE not in {"real", "poc"}:
        raise HTTPException(503, "WORKFLOW_MODE deve ser 'demo' ou 'real'.")

    try:
        client = get_supabase_client()
        response = client.auth.get_user(token)
        user = response.user
        if not user:
            raise _unauthorized()
        profile = client.table("profiles").select("*").eq("user_id", str(user.id)).single().execute().data
        return Principal(
            user_id=str(user.id),
            role=profile["role"],
            display_name=profile["display_name"],
            clinic_id=profile.get("clinic_id"),
            clinic_verified=bool(profile.get("clinic_verified", False)),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _unauthorized("Não foi possível validar a sessão no Supabase.") from exc


def get_current_principal(authorization: Annotated[str | None, Header()] = None) -> Principal:
    return resolve_principal(_extract_bearer(authorization))


def require_tutor(principal: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
    if principal.role != "tutor":
        raise HTTPException(403, "Esta ação é exclusiva do tutor.")
    return principal


def require_verified_clinic(principal: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
    if principal.role != "clinic":
        raise HTTPException(403, "Esta ação é exclusiva da clínica.")
    if not principal.clinic_id or not principal.clinic_verified:
        raise HTTPException(403, "O cadastro da clínica ainda não foi verificado.")
    return principal


def require_clinic(principal: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
    if principal.role != "clinic":
        raise HTTPException(403, "Esta ação é exclusiva da clínica.")
    return principal


def optional_legacy_tutor(
    authorization: Annotated[str | None, Header()] = None,
) -> Principal | None:
    """Keep demo compatibility while protecting legacy personal data in real mode."""

    if settings.WORKFLOW_MODE == "demo":
        return None

    principal = resolve_principal(_extract_bearer(authorization))
    if principal.role != "tutor":
        raise HTTPException(403, "Esta ação é exclusiva do tutor.")
    return principal
