from fastapi import APIRouter, HTTPException, Depends, Header

from app.clients.supabase_client import get_supabase_client
from app.core.config import settings
from app.schemas.auth import DemoLoginRequest, PasswordLoginRequest, SessionResponse, SignupRequest
from app.services.auth_service import DEMO_ACCOUNTS, demo_token, resolve_principal
from app.services.auth_service import get_current_principal
from app.services.poc_identity import issue_session, signup_local, login_local, revoke_session
from supabase import create_client


def auth_client():
    # Never install a user's session into the shared service-role data client.
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/demo", response_model=SessionResponse)
def login_demo(request: DemoLoginRequest):
    if settings.POC_QUICK_LOGIN_ENABLED:
        return issue_session(DEMO_ACCOUNTS[request.account])
    if settings.WORKFLOW_MODE != "demo":
        raise HTTPException(404, "Login demonstrativo desativado.")
    principal = DEMO_ACCOUNTS[request.account]
    return SessionResponse(access_token=demo_token(request.account), principal=principal)


@router.post("/login", response_model=SessionResponse)
def login(request: PasswordLoginRequest):
    if settings.AUTH_PROVIDER == "local":
        return login_local(request)
    if settings.WORKFLOW_MODE not in {"real", "poc"}:
        raise HTTPException(409, "Use as contas fictícias no modo demonstrativo.")
    try:
        response = auth_client().auth.sign_in_with_password(request.model_dump())
        if not response.session:
            raise HTTPException(401, "E-mail ou senha inválidos.")
        token = response.session.access_token
        return SessionResponse(access_token=token, expires_in=response.session.expires_in, principal=resolve_principal(token))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(401, "E-mail ou senha inválidos.") from exc


@router.post("/signup", status_code=201)
def signup(request: SignupRequest):
    if settings.AUTH_PROVIDER == "local":
        return signup_local(request)
    if settings.WORKFLOW_MODE not in {"real", "poc"}:
        raise HTTPException(409, "Cadastro real desativado no modo demonstrativo.")
    try:
        response = auth_client().auth.sign_up({
            "email": str(request.email),
            "password": request.password,
            "options": {"data": {"display_name": request.display_name, "requested_role": request.role}},
        })
        return {"user_id": str(response.user.id), "email_confirmation_required": response.session is None, "clinic_status": "pending_manual_verification" if request.role == "clinic" else None}
    except Exception as exc:
        raise HTTPException(400, "Não foi possível criar a conta.") from exc


@router.get("/me")
def me(principal=Depends(get_current_principal)):
    return principal


@router.post("/logout", status_code=204)
def logout(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ")
    if token.startswith("poc_"):
        revoke_session(token)


@router.get("/config")
def public_config():
    return {
        "quick_login_enabled": settings.POC_QUICK_LOGIN_ENABLED or settings.WORKFLOW_MODE == "demo",
        "own_accounts_enabled": settings.AUTH_PROVIDER == "local" or bool(settings.SUPABASE_URL),
        "maps_key": settings.GOOGLE_MAPS_WEB_KEY,
        "maps_key_kind": settings.MAPS_KEY_KIND,
        "maps_provider": settings.MAPS_PROVIDER,
        "map_id": settings.GOOGLE_MAP_ID,
    }
