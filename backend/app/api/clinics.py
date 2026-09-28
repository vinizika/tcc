from fastapi import APIRouter

from typing import Annotated
from fastapi import Depends, Query
from app.schemas.auth import Principal
from app.schemas.clinic import ClinicSearchRequest, ClinicSearchResponse, GeocodeResponse, ManualLocationRequest, ClinicRegistrationRequest, ClinicRegistrationResponse
from app.services.clinic_discovery_service import ClinicDiscoveryService
from app.services.auth_service import require_clinic, get_current_principal

router = APIRouter(prefix="/clinics", tags=["Clinics"])


@router.get("/participants")
def participants(latitude: float = Query(0, ge=-90, le=90), longitude: float = Query(0, ge=-180, le=180), principal=Depends(get_current_principal)):
    return ClinicDiscoveryService.participants(principal, latitude, longitude)


@router.post("/search", response_model=ClinicSearchResponse)
def search(request: ClinicSearchRequest):
    return ClinicDiscoveryService.search(request.latitude, request.longitude, request.radius_m, request.open_now)


@router.post("/geocode", response_model=GeocodeResponse)
def geocode(request: ManualLocationRequest):
    return ClinicDiscoveryService.geocode(request.query)


@router.post("/register", response_model=ClinicRegistrationResponse, status_code=201)
def register(request: ClinicRegistrationRequest, principal: Annotated[Principal, Depends(require_clinic)]):
    return ClinicDiscoveryService.register(request, principal)
