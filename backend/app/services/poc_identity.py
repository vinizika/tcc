"""Local academic accounts and opaque, revocable server-side sessions."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from app.clients.mongo_client import get_mongo_database
from app.core.config import settings
from app.schemas.auth import Principal, SessionResponse


def identity_db():
    db = get_mongo_database()
    db.poc_accounts.create_index("email", unique=True)
    db.poc_sessions.create_index("expires_at", expireAfterSeconds=0)
    return db


def password_hash(password: str, salt: str) -> str:
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()


def issue_session(principal: Principal) -> SessionResponse:
    token = "poc_" + secrets.token_urlsafe(32)
    ttl = settings.SESSION_TTL_HOURS * 3600
    identity_db().poc_sessions.insert_one({
        "_id": hashlib.sha256(token.encode()).hexdigest(),
        "principal": principal.model_dump(),
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=ttl),
    })
    return SessionResponse(access_token=token, principal=principal, expires_in=ttl)


def session_principal(token: str) -> Principal:
    db = identity_db()
    session = db.poc_sessions.find_one({"_id": hashlib.sha256(token.encode()).hexdigest(),
                                       "expires_at": {"$gt": datetime.now(timezone.utc)}})
    if not session:
        raise HTTPException(401, "Sua sessão expirou. Entre novamente.")
    principal = Principal(**session["principal"])
    if principal.demo:
        if not settings.POC_QUICK_LOGIN_ENABLED:
            raise HTTPException(401, "Acesso acadêmico desativado.")
        return principal
    account = db.poc_accounts.find_one({"_id": principal.user_id})
    if not account:
        raise HTTPException(401, "Conta indisponível.")
    return Principal(user_id=account["_id"], role=account["role"], display_name=account["display_name"],
                     clinic_id=account.get("clinic_id"), clinic_verified=account.get("clinic_verified", False))


def signup_local(request):
    salt = secrets.token_hex(16)
    account = {"_id": str(uuid4()), "email": request.email, "display_name": request.display_name,
               "role": request.role, "salt": salt, "password_hash": password_hash(request.password, salt),
               "created_at": datetime.now(timezone.utc).isoformat(), "clinic_verified": False}
    try:
        identity_db().poc_accounts.insert_one(account)
    except DuplicateKeyError:
        raise HTTPException(409, "Já existe uma conta com esse e-mail. Entre com sua senha.")
    return {"user_id": account["_id"], "email_confirmation_required": False}


def login_local(request):
    account = identity_db().poc_accounts.find_one({"email": request.email})
    # Run the same expensive comparison even for unknown addresses.
    salt = account["salt"] if account else "00" * 16
    calculated = password_hash(request.password, salt)
    if not account or not hmac.compare_digest(calculated, account["password_hash"]):
        raise HTTPException(401, "E-mail ou senha inválidos.")
    return issue_session(Principal(user_id=account["_id"], role=account["role"],
                                   display_name=account["display_name"], clinic_id=account.get("clinic_id"),
                                   clinic_verified=account.get("clinic_verified", False)))


def revoke_session(token: str):
    identity_db().poc_sessions.delete_one({"_id": hashlib.sha256(token.encode()).hexdigest()})
