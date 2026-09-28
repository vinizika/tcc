from typing import Literal, Optional

from pydantic import BaseModel, Field


class ClinicSearchRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_m: int = Field(default=10000, ge=500, le=50000)
    open_now: bool = False


class ManualLocationRequest(BaseModel):
    query: str = Field(min_length=3, max_length=300)


class ClinicResponse(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    distance_km: float
    distance_kind: Literal["straight_line", "route"] = "straight_line"
    phone: Optional[str] = None
    opening_hours: Optional[str] = None
    open_now: Optional[bool] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    source: Literal["demo", "google", "platform"]
    participant: bool = False
    verified: bool = False
    digital_referral_enabled: bool = False
    google_maps_uri: Optional[str] = None


class ClinicSearchResponse(BaseModel):
    mode: Literal["demo", "real"]
    clinics: list[ClinicResponse]
    notice: str
    google_attribution_required: bool = False


class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float
    formatted_address: str
    source: Literal["demo", "google"]


class ClinicRegistrationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    legal_name: str = Field(min_length=2, max_length=240)
    tax_id: str = Field(min_length=8, max_length=30)
    address: str = Field(min_length=5, max_length=400)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    phone: str = Field(min_length=8, max_length=30)
    opening_hours: str = Field(min_length=2, max_length=500)
    responsible_name: str = Field(min_length=2, max_length=200)
    responsible_document: str = Field(min_length=5, max_length=60)
    google_place_id: Optional[str] = Field(default=None, max_length=300)


class ClinicRegistrationResponse(BaseModel):
    id: str
    status: Literal["pending_manual_verification"]
    message: str
