import { useEffect, useRef, useState } from "react";
import { api, errorText } from "../api";
import type { Referral } from "../types";
import { ReferralChat } from "./ReferralChat";
import { ErrorNotice, Icon, Status, statusLabels, time } from "./ui";
export function CaseView({
  referral,
  token,
  onChange,
  onAlternatives,
}: {
  referral: Referral;
  token: string;
  onChange: (r: Referral) => void;
  onAlternatives: () => void;
}) {
  const [error, setError] = useState("");
  const [tracking, setTracking] = useState(false);
  const [busy, setBusy] = useState(false);
  const watch = useRef<number | null>(null);
  const last = useRef(0);
  const sending = useRef(false);
  const callback = useRef(onChange);
  callback.current = onChange;
  const terminal = ["refused", "cancelled", "completed"].includes(
    referral.status,
  );
  useEffect(
    () => () => {
      if (watch.current !== null) {
        navigator.geolocation.clearWatch(watch.current);
        watch.current = null;
        void api
          .location(referral.id, { consent: false }, token)
          .catch(() => {});
      }
    },
    [],
  );
  useEffect(() => {
    if (referral.status !== "on_the_way" && watch.current !== null) {
      navigator.geolocation.clearWatch(watch.current);
      watch.current = null;
      setTracking(false);
    }
  }, [referral.status]);
  async function action(name: string) {
    setBusy(true);
    setError("");
    try {
      onChange(await api.status(referral.id, name, token));
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  async function stop() {
    if (watch.current !== null) navigator.geolocation.clearWatch(watch.current);
    watch.current = null;
    setTracking(false);
    try {
      onChange(await api.location(referral.id, { consent: false }, token));
    } catch (e) {
      setError(
        "A captura parou neste navegador, mas não conseguimos remover a última posição do servidor. Tente novamente. " +
          errorText(e),
      );
    }
  }
  function start() {
    if (!navigator.geolocation) {
      setError("Localização não disponível neste navegador.");
      return;
    }
    setError("");
    last.current = 0;
    watch.current = navigator.geolocation.watchPosition(
      async (p) => {
        if (sending.current || Date.now() - last.current < 30000) return;
        sending.current = true;
        last.current = Date.now();
        try {
          const r = await api.location(
            referral.id,
            {
              consent: true,
              latitude: p.coords.latitude,
              longitude: p.coords.longitude,
              accuracy_m: p.coords.accuracy,
            },
            token,
          );
          callback.current(r);
          setTracking(true);
        } catch (e) {
          setError(errorText(e));
        } finally {
          sending.current = false;
        }
      },
      () => {
        setError(
          "Não foi possível obter a localização. Verifique a permissão do navegador.",
        );
        stop();
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 },
    );
    setTracking(true);
  }
  return (
    <section className="case-page page-enter">
      <div className="page-heading">
        <p className="eyebrow">Continuidade do cuidado</p>
        <h1>Seu encaminhamento</h1>
      </div>
      <ErrorNotice message={error} />
      <div className="case-columns">
        <div>
          <article className="panel">
            <Status value={referral.status} />
            <h2>{referral.clinic_name}</h2>
            <p className="muted">Enviado em {time(referral.created_at)}</p>
            <p>
              Você pode acompanhar a resposta da clínica e conversar com a
              equipe por aqui.
            </p>
            <div className="button-row">
              {referral.status === "accepted" && (
                <button
                  className="primary"
                  disabled={busy}
                  onClick={() => action("confirm_on_the_way")}
                >
                  Estou a caminho
                  <Icon name="arrow" />
                </button>
              )}
              {!terminal && referral.status !== "arrived" && (
                <button disabled={busy} onClick={() => action("cancel")}>
                  Cancelar envio
                </button>
              )}
              <button onClick={onAlternatives}>Ver outras clínicas</button>
            </div>
          </article>
          {referral.status === "on_the_way" && (
            <article className="panel">
              <h2>Compartilhar localização?</h2>
              <p className="muted">
                Ao ativar, você autoriza esta clínica a ver sua posição. Só
                funciona enquanto esta página estiver aberta e conectada.
              </p>
              {tracking || referral.location ? (
                <>
                  <p className="notice">
                    {tracking
                      ? "Compartilhamento ativo neste navegador."
                      : "Há uma última posição salva. A captura não está ativa nesta página."}
                  </p>
                  <button onClick={stop}>Interromper e remover posição</button>
                  {!tracking && (
                    <button onClick={start}>Retomar compartilhamento</button>
                  )}
                </>
              ) : (
                <button onClick={start}>
                  <Icon name="pin" />
                  Autorizar e compartilhar
                </button>
              )}
            </article>
          )}
          <article className="panel">
            <h2>Histórico do caso</h2>
            <ol className="timeline">
              {referral.events.map((e, i) => (
                <li key={i}>
                  <span className="timeline-dot" />
                  <div>
                    <strong>{statusLabels[e.type] || e.type}</strong>
                    <p>{e.description}</p>
                    <time>{time(e.created_at)}</time>
                  </div>
                </li>
              ))}
            </ol>
          </article>
        </div>
        <ReferralChat initial={referral} token={token} onChange={onChange} />
      </div>
    </section>
  );
}
