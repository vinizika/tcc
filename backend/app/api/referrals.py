from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, Query

from app.core.config import settings
from app.schemas.auth import Principal
from app.schemas.referral import DashboardResponse, ReferralCreate, ReferralMessageCreate, ReferralResponse, StatusTransitionRequest
from app.services.auth_service import get_current_principal, require_tutor, require_verified_clinic
from app.services.indicator_service import IndicatorService
from app.services.message_service import MessageService
from app.services.referral_service import ReferralService

router = APIRouter(prefix="/referrals", tags=["Referrals"])

from app.schemas.workspace import LocationInput
from app.services.travel_service import TravelService


@router.put("/{referral_id}/location", response_model=ReferralResponse)
def share_location(referral_id: str, data: LocationInput, principal: Annotated[Principal, Depends(get_current_principal)]):
    return TravelService.update(referral_id, data, principal)


@router.post("/", response_model=ReferralResponse)
def create(request: ReferralCreate, response: Response, principal: Annotated[Principal, Depends(require_tutor)]):
    referral, created = ReferralService.create(request, principal)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    response.headers["X-Idempotent-Replay"] = "false" if created else "true"
    return referral


@router.get("/", response_model=list[ReferralResponse])
def list_referrals(principal: Annotated[Principal, Depends(get_current_principal)], offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100)):
    return ReferralService.list_for(principal)[offset:offset + limit]


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(principal: Annotated[Principal, Depends(require_verified_clinic)], offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100), active_only: bool = False):
    referrals = ReferralService.list_for(principal)
    selected = [r for r in referrals if not active_only or r.status not in {"completed", "cancelled", "refused"}]
    return DashboardResponse(metrics=IndicatorService.calculate(referrals), referrals=selected[offset:offset+limit], polling_interval_s=settings.WORKFLOW_POLL_INTERVAL_S, has_more=len(selected)>offset+limit)


@router.get("/{referral_id}", response_model=ReferralResponse)
def get(referral_id: str, principal: Annotated[Principal, Depends(get_current_principal)]):
    return ReferralService.get(referral_id, principal)


@router.post("/{referral_id}/status", response_model=ReferralResponse)
def transition(referral_id: str, request: StatusTransitionRequest, principal: Annotated[Principal, Depends(get_current_principal)]):
    return ReferralService.transition(referral_id, request, principal)


@router.post("/{referral_id}/messages", response_model=ReferralResponse)
def send_message(referral_id: str, request: ReferralMessageCreate, principal: Annotated[Principal, Depends(get_current_principal)]):
    return MessageService.send(referral_id, request, principal)


@router.post("/{referral_id}/close-chat", response_model=ReferralResponse)
def close_chat(referral_id: str, principal: Annotated[Principal, Depends(get_current_principal)]):
    return MessageService.close(referral_id, principal)
