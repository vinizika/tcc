import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { Clinic } from "../types";
declare global {
  interface Window {
    google: any;
    __vetMapPromise?: Promise<void>;
    gm_authFailure?: () => void;
  }
}
async function loadGoogle() {
  if (window.google?.maps?.Map) return;
  if (!window.__vetMapPromise)
    window.__vetMapPromise = api
      .config()
      .then(
        (config) =>
          new Promise<void>((resolve, reject) => {
            if (!config.maps_key) {
              reject(new Error("Mapa não configurado."));
              return;
            }
            window.gm_authFailure = () => {
              window.dispatchEvent(new Event("vetai-map-auth-error"));
              reject(new Error("O Google não autorizou o mapa."));
            };
            const script = document.createElement("script");
            script.src =
              "https://maps.googleapis.com/maps/api/js?key=" +
              encodeURIComponent(config.maps_key) +
              "&v=weekly";
            script.async = true;
            script.onload = () => resolve();
            script.onerror = () =>
              reject(new Error("Não foi possível carregar o mapa."));
            document.head.appendChild(script);
          }),
      )
      .catch((e) => {
        window.__vetMapPromise = undefined;
        throw e;
      });
  return window.__vetMapPromise;
}
export function MapPanel({
  clinics,
  center,
  selected,
  onSelect,
  mode,
}: {
  clinics: Clinic[];
  center: { lat: number; lng: number };
  selected?: string;
  onSelect: (id: string) => void;
  mode: "demo" | "real";
}) {
  const ref = useRef<HTMLDivElement>(null);
  const map = useRef<any>(null);
  const markers = useRef<any[]>([]);
  const callback = useRef(onSelect);
  callback.current = onSelect;
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let cancelled = false;
    if (mode === "demo") return;
    const authError = () =>
      setError("O Google não autorizou o mapa. A lista continua disponível.");
    window.addEventListener("vetai-map-auth-error", authError);
    loadGoogle()
      .then(() => {
        if (cancelled || !ref.current) return;
        map.current = new window.google.maps.Map(ref.current, {
          center,
          zoom: 13,
          disableDefaultUI: true,
          zoomControl: true,
          fullscreenControl: true,
          gestureHandling: "cooperative",
        });
        setReady(true);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
      window.removeEventListener("vetai-map-auth-error", authError);
      markers.current.forEach((m) => m.setMap(null));
    };
  }, [mode]);
  useEffect(() => {
    if (!ready || !map.current) return;
    markers.current.forEach((m) => m.setMap(null));
    markers.current = [];
    const g = window.google.maps;
    const bounds = new g.LatLngBounds();
    bounds.extend(center);
    markers.current.push(
      new g.Marker({
        map: map.current,
        position: center,
        title: "Ponto de partida",
        icon: {
          path: g.SymbolPath.CIRCLE,
          scale: 8,
          fillColor: "#235d4b",
          fillOpacity: 1,
          strokeColor: "#fff",
          strokeWeight: 3,
        },
      }),
    );
    clinics.forEach((c, i) => {
      const position = { lat: c.latitude, lng: c.longitude };
      bounds.extend(position);
      const marker = new g.Marker({
        map: map.current,
        position,
        title: c.name,
        label: { text: String(i + 1), color: "#fff" },
        zIndex: c.id === selected ? 100 : 1,
      });
      marker.addListener("click", () => callback.current(c.id));
      markers.current.push(marker);
    });
    if (clinics.length) map.current.fitBounds(bounds, 45);
    else map.current.setCenter(center);
  }, [ready, clinics, center]);
  useEffect(() => {
    const clinic = clinics.find((c) => c.id === selected);
    if (clinic && map.current)
      map.current.panTo({ lat: clinic.latitude, lng: clinic.longitude });
  }, [selected, clinics]);
  if (mode === "demo")
    return (
      <div className="map-unavailable">
        Mapa de teste. Ative a busca Google para consultar locais reais.
      </div>
    );
  return (
    <div className="map-wrap">
      <div
        className="map"
        ref={ref}
        aria-label="Mapa Google com ponto de partida e clínicas"
      />
      {(!ready || error) && (
        <div className="map-overlay">{error || "Carregando mapa…"}</div>
      )}
    </div>
  );
}
