from math import asin, cos, radians, sin, sqrt
from urllib.parse import quote

from fastapi import HTTPException
from app.core.config import settings
from app.clients.maps_client import google_request
from app.clients.supabase_client import get_supabase_client
from app.clients.mongo_client import get_mongo_database
from app.repositories.workflow_repository import get_workflow_repository
from app.schemas.clinic import ClinicResponse, ClinicSearchResponse, GeocodeResponse, ClinicRegistrationResponse


def _distance_km(a_lat, a_lng, b_lat, b_lng):
    dlat, dlng = radians(b_lat - a_lat), radians(b_lng - a_lng)
    value = sin(dlat / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2
    return round(6371 * 2 * asin(sqrt(min(1, value))), 1)


def fixture_maps():
    return settings.MAPS_PROVIDER == "fixtures" or (settings.MAPS_PROVIDER == "auto" and settings.WORKFLOW_MODE == "demo")


class ClinicDiscoveryService:
    @staticmethod
    def register(data, principal):
        if principal.demo:
            raise HTTPException(403, "Use uma conta própria para cadastrar uma unidade.")
        if principal.clinic_id:
            raise HTTPException(409, "Esta conta já está vinculada a uma unidade.")
        clinic_id = "unit-" + principal.user_id
        document = data.model_dump() | {"id": clinic_id, "owner_user_id": principal.user_id, "source": "platform", "participant": True,
            "verified": False, "enabled": False, "verification_status": "pending_manual_verification"}
        existing = get_workflow_repository().get_clinic(clinic_id)
        if existing and existing.get("verified"):
            raise HTTPException(409, "Unidade já verificada. Solicite alteração à administração.")
        get_workflow_repository().save_clinic(document)
        if settings.AUTH_PROVIDER == "local":
            get_mongo_database().poc_accounts.update_one({"_id": principal.user_id}, {"$set": {"clinic_id": clinic_id, "clinic_verified": False}})
        else:
            get_supabase_client().table("profiles").update({"clinic_id": clinic_id, "clinic_verified": False}).eq("user_id", principal.user_id).execute()
        return ClinicRegistrationResponse(id=clinic_id, status="pending_manual_verification",
            message="Cadastro recebido. A equipe deve confirmar o vínculo com a unidade antes de liberar casos.")

    @staticmethod
    def participants(principal, latitude, longitude):
        return [ClinicDiscoveryService._response(c, latitude, longitude) for c in get_workflow_repository().list_clinics()
                if c.get("enabled") and c.get("verified") and (c.get("source") == "demo") == principal.demo]

    @staticmethod
    def search(latitude, longitude, radius_m, open_now):
        records = get_workflow_repository().list_clinics()
        if fixture_maps():
            clinics = [ClinicDiscoveryService._response(c, latitude, longitude) for c in records if c.get("source") == "demo"]
            return ClinicSearchResponse(mode="demo", clinics=sorted([c for c in clinics if not open_now or c.open_now is True], key=lambda c: c.distance_km), notice="Dados fictícios de teste. Nenhuma unidade externa será contatada.")
        participants = {c["google_place_id"]: c for c in records if c.get("google_place_id") and c.get("verified") and c.get("source") != "demo"}
        fields = "places.id,places.displayName,places.formattedAddress,places.location,places.nationalPhoneNumber,places.regularOpeningHours,places.currentOpeningHours,places.googleMapsUri"
        if settings.MAPS_KEY_KIND == "standard":
            fields += ",places.rating,places.userRatingCount"
        result = google_request("POST", "https://places.googleapis.com/v1/places:searchNearby", fields=fields, json={
            "includedTypes": ["veterinary_care"], "maxResultCount": 20, "rankPreference": "DISTANCE",
            "languageCode": "pt-BR", "locationRestriction": {"circle": {"center": {"latitude": latitude, "longitude": longitude}, "radius": radius_m}},
        })
        clinics = []
        for place in result.get("places", []):
            loc = place.get("location", {})
            if "latitude" not in loc or "longitude" not in loc:
                continue
            participant = participants.get(place["id"], {})
            opening = place.get("currentOpeningHours") or place.get("regularOpeningHours") or {}
            item = {"id": participant.get("id") or "google:" + place["id"],
                "name": place.get("displayName", {}).get("text", "Clínica veterinária"),
                "address": place.get("formattedAddress"), **loc, "phone": place.get("nationalPhoneNumber"),
                "opening_hours": "; ".join(opening.get("weekdayDescriptions", [])) or None, "open_now": opening.get("openNow"),
                "google_maps_uri": place.get("googleMapsUri"), "source": "google", "participant": bool(participant),
                "verified": participant.get("verified", False), "enabled": participant.get("enabled", False),
                "rating": place.get("rating"), "review_count": place.get("userRatingCount")}
            if not open_now or item["open_now"] is True:
                clinics.append(ClinicDiscoveryService._response(item, latitude, longitude))
        return ClinicSearchResponse(mode="real", clinics=sorted(clinics, key=lambda c: c.distance_km),
            notice="Informações do Google Maps. Ligue para confirmar se a unidade pode receber o animal.", google_attribution_required=True)

    @staticmethod
    def _response(item, origin_lat, origin_lng):
        fields = {k: v for k, v in item.items() if k in ClinicResponse.model_fields and k not in {"distance_km", "digital_referral_enabled"}}
        return ClinicResponse(**fields, distance_km=_distance_km(origin_lat, origin_lng, item["latitude"], item["longitude"]),
            digital_referral_enabled=bool(item.get("participant") and item.get("verified") and item.get("enabled")))

    @staticmethod
    def geocode(query):
        if fixture_maps():
            return GeocodeResponse(latitude=-23.5617, longitude=-46.6559, formatted_address=f"Local fictício: {query}", source="demo")
        data = google_request("POST", "https://places.googleapis.com/v1/places:searchText",
            fields="places.location,places.formattedAddress,places.displayName", json={"textQuery": query, "languageCode": "pt-BR", "regionCode": "BR", "pageSize": 1})
        places = data.get("places", [])
        if places:
            item = places[0]
            return GeocodeResponse(**item["location"], formatted_address=item.get("formattedAddress") or item.get("displayName", {}).get("text", query), source="google")
        data = google_request("GET", "https://geocode.googleapis.com/v4/geocode/address/" + quote(query, safe=""),
            fields="results.location,results.formattedAddress", params={"languageCode": "pt-BR", "regionCode": "BR"})
        if not data.get("results"):
            raise HTTPException(404, "Local não encontrado. Inclua cidade ou CEP na busca.")
        item = data["results"][0]
        return GeocodeResponse(**item["location"], formatted_address=item["formattedAddress"], source="google")
