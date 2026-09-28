import { useEffect, useState } from "react";
import { api, errorText } from "../api";
import type { Clinic, ClinicSearch, Session } from "../types";
import { MapPanel } from "./MapPanel";
import { ErrorNotice, Icon } from "./ui";
export function ClinicFinder({
  session,
  canShare,
  onChoose,
  onBack,
}: {
  session: Session;
  canShare: boolean;
  onChoose: (c: Clinic) => void;
  onBack: () => void;
}) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<ClinicSearch | null>(null);
  const [center, setCenter] = useState<{ lat: number; lng: number } | null>(
    null,
  );
  const [selected, setSelected] = useState("");
  const [origin, setOrigin] = useState("");
  const [participants, setParticipants] = useState<Clinic[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [openOnly, setOpenOnly] = useState(false);
  useEffect(() => {
    api
      .participants(session.access_token)
      .then(setParticipants)
      .catch(() => {});
  }, [session.access_token]);
  async function search(
    lat: number,
    lng: number,
    label: string,
    only = openOnly,
  ) {
    setBusy(true);
    setError("");
    setCenter({ lat, lng });
    setOrigin(label);
    setResult(null);
    try {
      setResult(await api.clinics(lat, lng, only));
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  async function manual() {
    setBusy(true);
    setError("");
    try {
      const p = await api.geocode(query);
      await search(p.latitude, p.longitude, p.formatted_address);
    } catch (e) {
      setError(errorText(e));
      setBusy(false);
    }
  }
  function locate() {
    if (!navigator.geolocation) {
      setError("Localização indisponível. Use CEP, endereço ou referência.");
      return;
    }
    setBusy(true);
    navigator.geolocation.getCurrentPosition(
      (p) =>
        search(p.coords.latitude, p.coords.longitude, "Sua localização atual"),
      () => {
        setBusy(false);
        setError(
          "Não conseguimos acessar sua localização. Digite um endereço, CEP ou ponto de referência.",
        );
      },
      { timeout: 12000, maximumAge: 60000 },
    );
  }
  return (
    <section className="finder page-enter">
      <button className="text-button" onClick={onBack}>
        ← Voltar à conversa
      </button>
      <div className="page-heading">
        <p className="eyebrow">Cuidado por perto</p>
        <h1>Encontre atendimento</h1>
        <p className="muted">
          Veja as opções próximas. Ligue para confirmar se a clínica pode
          receber seu animal.
        </p>
      </div>
      <div className="search-tools">
        <form
          className="location-search"
          onSubmit={(e) => {
            e.preventDefault();
            manual();
          }}
        >
          <Icon name="pin" />
          <input
            aria-label="CEP, endereço ou ponto de referência"
            value={query}
            minLength={3}
            required
            onChange={(e) => setQuery(e.target.value)}
            placeholder="CEP, endereço ou ponto de referência"
          />
          <button className="primary" disabled={busy}>
            Buscar
          </button>
        </form>
        <button onClick={locate} disabled={busy}>
          <Icon name="pin" />
          Usar minha localização
        </button>
      </div>
      <ErrorNotice message={error} />
      {busy && (
        <p className="notice" role="status">
          Buscando locais próximos…
        </p>
      )}
      {center && (
        <div className="finder-caption">
          <span>{origin}</span>
          <label className="check">
            <input
              type="checkbox"
              checked={openOnly}
              onChange={(e) => {
                setOpenOnly(e.target.checked);
                search(center.lat, center.lng, origin, e.target.checked);
              }}
            />
            Abertas agora
          </label>
        </div>
      )}
      {result && center ? (
        <>
          <div className="finder-grid">
            <div className="places-list">
              {result.clinics.length === 0 ? (
                <div className="empty-state">
                  <Icon name="pin" size={36} />
                  <h2>Nenhuma clínica encontrada</h2>
                  <p>Tente outro endereço ou remova o filtro de horário.</p>
                </div>
              ) : (
                result.clinics.map((c, i) => (
                  <ClinicCard
                    key={c.id}
                    clinic={c}
                    number={i + 1}
                    selected={selected === c.id}
                    onSelect={() => setSelected(c.id)}
                    onChoose={() => onChoose(c)}
                    canShare={canShare && !session.principal.demo}
                  />
                ))
              )}
            </div>
            <MapPanel
              clinics={result.clinics}
              center={center}
              selected={selected}
              onSelect={setSelected}
              mode={result.mode}
            />
          </div>
          <p className="tiny">
            {result.notice} Distâncias em linha reta, não estimativas de
            trajeto.
          </p>
        </>
      ) : (
        !busy &&
        !error && (
          <div className="map-placeholder">
            <Icon name="pin" size={44} />
            <h2>Onde você está buscando?</h2>
            <p>Informe um local para ver clínicas reais no mapa.</p>
          </div>
        )
      )}
      {participants.length > 0 && (
        <section className="academic-units">
          <p className="eyebrow">
            {session.principal.demo
              ? "Ambiente acadêmico separado"
              : "Unidades participantes"}
          </p>
          <h2>
            {session.principal.demo
              ? "Teste a continuidade do caso"
              : "Compartilhe com uma unidade habilitada"}
          </h2>
          <p className="muted">
            {session.principal.demo
              ? "Estas unidades são fictícias e não fazem parte dos resultados Google. O envio permite avaliar o painel e o chat com a equipe."
              : "Unidades cadastradas e verificadas na plataforma."}
          </p>
          {participants.map((c) => (
            <div className="academic-unit" key={c.id}>
              <Icon name="clinic" />
              <div>
                <strong>{c.name}</strong>
                <p>
                  {c.source === "demo"
                    ? "Conta acadêmica · nenhum atendimento real"
                    : c.address}
                </p>
              </div>
              <button disabled={!canShare} onClick={() => onChoose(c)}>
                Compartilhar caso
                <Icon name="arrow" />
              </button>
            </div>
          ))}
          {!canShare && (
            <p className="tiny">
              Conclua uma pré-triagem para preparar o resumo.
            </p>
          )}
        </section>
      )}
    </section>
  );
}
function ClinicCard({
  clinic: c,
  number,
  selected,
  onSelect,
  onChoose,
  canShare,
}: {
  clinic: Clinic;
  number: number;
  selected: boolean;
  onSelect: () => void;
  onChoose: () => void;
  canShare: boolean;
}) {
  return (
    <article className={"place-card " + (selected ? "selected" : "")}>
      <button className="place-select" onClick={onSelect}>
        <span className="place-number">{number}</span>
        <span>
          <h2>{c.name}</h2>
          <p>{c.address}</p>
        </span>
      </button>
      <div className="place-facts">
        <span>{c.distance_km} km em linha reta</span>
        <span className={c.open_now ? "open" : ""}>
          {c.open_now === true
            ? "Aberta agora"
            : c.open_now === false
              ? "Fechada agora"
              : "Horário não informado"}
        </span>
      </div>
      {c.opening_hours && (
        <details>
          <summary>Ver horários</summary>
          <p>{c.opening_hours}</p>
        </details>
      )}
      <div className="button-row">
        {c.phone ? (
          <a className="button" href={"tel:" + c.phone.replace(/[^+\d]/g, "")}>
            <Icon name="phone" />
            Ligar
          </a>
        ) : (
          <span className="tiny">Telefone não informado</span>
        )}
        <a
          className="button"
          target="_blank"
          rel="noreferrer"
          href={
            "https://www.google.com/maps/dir/?api=1&destination=" +
            c.latitude +
            "," +
            c.longitude
          }
        >
          <Icon name="pin" />
          Rota
        </a>
        {c.digital_referral_enabled && canShare && (
          <button className="primary" onClick={onChoose}>
            Escolher
          </button>
        )}
      </div>
      <p className="tiny">
        {c.digital_referral_enabled
          ? "Participante habilitada para receber casos"
          : "Informações públicas · sem encaminhamento pela plataforma"}
      </p>
    </article>
  );
}
