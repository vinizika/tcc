from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


Role = Literal["tutor", "clinic"]


class Principal(BaseModel):
    user_id: str
    role: Role
    display_name: str
    clinic_id: Optional[str] = None
    clinic_verified: bool = False
    demo: bool = False


class DemoLoginRequest(BaseModel):
    account: Literal["tutor-a", "tutor-b", "clinic-a", "clinic-b", "clinic-pending"]


class PasswordLoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("E-mail inválido.")
        return value


class SignupRequest(PasswordLoginRequest):
    display_name: str = Field(min_length=2, max_length=200)
    role: Role = "tutor"


class SessionResponse(BaseModel):
    access_token: str
    principal: Principal
    expires_in: Optional[int] = None
