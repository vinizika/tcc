"""Supported Maps Demo Key services, explicit fields and sanitized errors."""
import requests
from fastapi import HTTPException
from app.core.config import settings


def google_request(method, url, *, fields, **kwargs):
    if not settings.GOOGLE_MAPS_SERVER_KEY:
        raise HTTPException(503, "A busca de locais ainda não foi configurada.")
    try:
        response = requests.request(method, url, headers={
            "X-Goog-Api-Key": settings.GOOGLE_MAPS_SERVER_KEY, "X-Goog-FieldMask": fields,
        }, timeout=15, **kwargs)
    except requests.RequestException:
        raise HTTPException(503, "Não conseguimos acessar o Google Maps agora. Tente novamente.")
    if response.status_code == 429:
        raise HTTPException(429, "O limite de consultas ao Google Maps foi atingido. Tente novamente mais tarde.")
    if response.status_code in {401, 403}:
        raise HTTPException(503, "O Google Maps recusou o acesso. Confira a chave e as APIs habilitadas.")
    if not response.ok:
        raise HTTPException(503, "O serviço de mapas não conseguiu concluir a busca.")
    return response.json()


def route_estimate(latitude, longitude, clinic):
    data = google_request("POST", "https://routes.googleapis.com/directions/v2:computeRoutes",
        fields="routes.duration,routes.distanceMeters", json={
            "origin": {"location": {"latLng": {"latitude": latitude, "longitude": longitude}}},
            "destination": {"location": {"latLng": {"latitude": clinic["latitude"], "longitude": clinic["longitude"]}}},
            "travelMode": "DRIVE", "routingPreference": "TRAFFIC_UNAWARE", "languageCode": "pt-BR",
        })
    routes = data.get("routes", [])
    if not routes:
        return None
    return {"duration_seconds": float(routes[0]["duration"].removesuffix("s")),
            "distance_m": routes[0]["distanceMeters"], "mode": "DRIVE", "traffic_included": False}
