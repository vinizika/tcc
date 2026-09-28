import { FormEvent, useEffect, useRef, useState } from "react";
import { api, errorText } from "../api";
import { Brand, ErrorNotice, Icon, Status, time } from "../components/ui";
import { ReferralChat } from "../components/ReferralChat";
import { MessageText } from "../components/MessageText";
import type { Dashboard, Referral, Session } from "../types";

export function ClinicDashboard({
  session,
  onLogout,
}: {
  session: Session;
  onLogout: () => void;
}) {
  const [data, setData] = useState<Dashboard | null>(null);
  const [selected, setSelected] = useState<Referral | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [filter, setFilter] = useState("active");
  const [offset, setOffset] = useState(0);
  const [tab, setTab] = useState("summary");
  const selectedId = useRef<string | null>(null);
  selectedId.current = selected?.id || null;
  const allowed = session.principal.clinic_verified;
  const token = session.access_token;
  async function load() {
    try {
      const d = await api.dashboard(token, offset, filter === "active");
      setData(d);
      setError("");
      if (selectedId.current) {
        const r = await api.referral(selectedId.current, token);
        if (r.id === selectedId.current) setSelected(r);
      }
    } catch (e) {
      setError(errorText(e));
    }
  }
  useEffect(() => {
    if (!allowed) return;
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      await load();
      if (active) timer = setTimeout(poll, 8000);
    }
    poll();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [token, allowed, offset, filter]);
  async function status(action: string) {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      setSelected(await api.status(selected.id, action, token));
      await load();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  const activeCases =
    data?.referrals.filter(
      (r) =>
        filter === "all" ||
        !["completed", "cancelled", "refused"].includes(r.status),
    ) || [];
  const fresh =
    selected?.location &&
    Date.now() - Date.parse(selected.location.updated_at) < 120000;
  return (
    <div className="clinic-shell">
      <header className="clinic-header">
        <Brand />
        <span className="header-context">
          <Icon name="clinic" />
          Espaço da clínica
        </span>
        <div className="clinic-profile">
          <span>
            {session.principal.display_name}
            <small>
              {session.principal.demo
                ? "Unidade acadêmica fictícia"
                : "Conta institucional"}
            </small>
          </span>
          <button className="icon-button" onClick={onLogout} aria-label="Sair">
            <Icon name="logout" />
          </button>
        </div>
      </header>
      {!allowed ? (
        !session.principal.clinic_id ? (
          <ClinicRegistration token={token} />
        ) : (
          <main className="content-page">
            <div className="empty-state">
              <Icon name="shield" size={40} />
              <h1>Cadastro em verificação</h1>
              <p>
                A unidade ainda não está autorizada a receber casos. A
                confirmação de titularidade é manual.
              </p>
              <button onClick={onLogout}>Voltar ao início</button>
            </div>
          </main>
        )
      ) : (
        <main className="dashboard-shell page-enter">
          <div className="page-heading section-heading">
            <div>
              <p className="eyebrow">Continuidade do cuidado</p>
              <h1>Uma visão de quem precisa de você.</h1>
              <p className="muted">
                Casos autorizados pelos tutores. Atualização a cada 8 segundos.
              </p>
            </div>
            <button onClick={load}>
              <Icon name="clock" />
              Atualizar
            </button>
          </div>
          <ErrorNotice message={error} />
          {!data ? (
            <p role="status">Carregando encaminhamentos…</p>
          ) : (
            <>
              <section
                className="metrics"
                aria-label="Indicadores de encaminhamento"
              >
                {[
                  [
                    "confirmed_on_the_way",
                    "A caminho",
                    "Confirmados pelo tutor",
                  ],
                  [
                    "awaiting_review",
                    "Aguardando análise",
                    "Novos ou visualizados",
                  ],
                  ["arrived_last_24h", "Chegaram", "Nas últimas 24 horas"],
                  ["total_received", "Recebidos", "Desde o início"],
                ].map(([key, title, detail]) => (
                  <article key={key} title={data.metrics.definitions[key]}>
                    <p>{title}</p>
                    <strong>
                      {data.metrics[key as keyof typeof data.metrics] as number}
                    </strong>
                    <small>{detail}</small>
                  </article>
                ))}
              </section>
              <div className="dashboard-grid">
                <section className="queue panel">
                  <div className="section-heading">
                    <h2>Encaminhamentos</h2>
                    <span className="count">{activeCases.length}</span>
                  </div>
                  <div className="tabs">
                    <button
                      className={filter === "active" ? "active" : ""}
                      onClick={() => {
                        setFilter("active");
                        setOffset(0);
                      }}
                    >
                      Em andamento
                    </button>
                    <button
                      className={filter === "all" ? "active" : ""}
                      onClick={() => {
                        setFilter("all");
                        setOffset(0);
                      }}
                    >
                      Todos
                    </button>
                  </div>
                  {activeCases.length === 0 ? (
                    <div className="empty-state">
                      <Icon name="chat" size={32} />
                      <h3>Nenhum caso por aqui</h3>
                      <p>Novos encaminhamentos aparecerão nesta lista.</p>
                    </div>
                  ) : (
                    activeCases.map((r) => (
                      <button
                        className={
                          "queue-item " +
                          (selected?.id === r.id ? "active" : "")
                        }
                        key={r.id}
                        onClick={async () => {
                          try {
                            setSelected(await api.referral(r.id, token));
                            setTab("summary");
                          } catch (e) {
                            setError(errorText(e));
                          }
                        }}
                      >
                        <div>
                          <Status value={r.status} />
                          <time>{time(r.created_at)}</time>
                        </div>
                        <strong>{r.pet?.name || "Animal não associado"}</strong>
                        <p>
                          {r.contact.name || "Tutor"} ·{" "}
                          {r.pet?.species === "cao"
                            ? "Cachorro"
                            : r.pet?.species === "gato"
                              ? "Gato"
                              : "Espécie não informada"}
                        </p>
                        <span
                          className={
                            "triage-label " +
                            r.triage.classification.toLowerCase()
                          }
                        >
                          {r.triage.classification === "EMERGENCIA"
                            ? "Sinalizado como emergência"
                            : r.triage.classification === "INCERTO"
                              ? "Avaliação incerta"
                              : "Orientação inicial"}
                        </span>
                      </button>
                    ))
                  )}
                  <div className="button-row">
                    {offset > 0 && (
                      <button
                        onClick={() => setOffset(Math.max(0, offset - 30))}
                      >
                        Anteriores
                      </button>
                    )}
                    {data.has_more && (
                      <button onClick={() => setOffset(offset + 30)}>
                        Próximos casos
                      </button>
                    )}
                  </div>
                </section>
                <section className="case-workspace">
                  {!selected ? (
                    <div className="detail-empty empty-state">
                      <Icon name="clinic" size={44} />
                      <h2>O cuidado começa pela escuta.</h2>
                      <p>
                        Selecione um caso para ver o resumo autorizado e
                        conversar com o tutor.
                      </p>
                    </div>
                  ) : (
                    <>
                      <article className="panel case-detail">
                        <div className="section-heading">
                          <div>
                            <p className="eyebrow">
                              Caso {selected.id.slice(0, 8)}
                            </p>
                            <h2>
                              {selected.pet?.name || "Animal não associado"}
                            </h2>
                            <p className="muted">
                              {selected.contact.name ||
                                "Tutor não identificado"}
                            </p>
                          </div>
                          <Status value={selected.status} />
                        </div>
                        <div className="tabs">
                          <button
                            className={tab === "summary" ? "active" : ""}
                            onClick={() => setTab("summary")}
                          >
                            Resumo
                          </button>
                          <button
                            className={tab === "full" ? "active" : ""}
                            onClick={() => setTab("full")}
                          >
                            Conversa original
                          </button>
                          <button
                            className={tab === "events" ? "active" : ""}
                            onClick={() => setTab("events")}
                          >
                            Histórico
                          </button>
                        </div>
                        {tab === "summary" && (
                          <>
                            <div className="source-block">
                              <span className="eyebrow">
                                Revisado e autorizado pelo tutor
                              </span>
                              <p>{selected.reviewed_summary}</p>
                            </div>
                            <details className="source-block">
                              <summary>Relato original</summary>
                              <p>{selected.triage.original_report}</p>
                            </details>
                            <div className="auto-summary">
                              <span className="eyebrow">
                                Pré-triagem automática · não é diagnóstico
                              </span>
                              <p>{selected.triage.justification}</p>
                              <p>{selected.triage.recommendation}</p>
                            </div>
                            <dl className="patient-info">
                              <dt>Animal</dt>
                              <dd>
                                {selected.pet
                                  ? [
                                      selected.pet.species === "cao"
                                        ? "Cachorro"
                                        : "Gato",
                                      selected.pet.age,
                                      selected.pet.weight_kg
                                        ? selected.pet.weight_kg + " kg"
                                        : null,
                                      selected.pet.breed,
                                    ]
                                      .filter(Boolean)
                                      .join(" · ")
                                  : "Não compartilhado"}
                              </dd>
                              {selected.pet?.relevant_history && (
                                <>
                                  <dt>Histórico informado</dt>
                                  <dd>{selected.pet.relevant_history}</dd>
                                </>
                              )}
                              <dt>Contato</dt>
                              <dd>
                                {selected.contact.phone ? (
                                  <a
                                    href={
                                      "tel:" +
                                      selected.contact.phone.replace(
                                        /[^+\d]/g,
                                        "",
                                      )
                                    }
                                  >
                                    {selected.contact.phone}
                                  </a>
                                ) : (
                                  "Telefone não compartilhado"
                                )}
                              </dd>
                            </dl>
                          </>
                        )}
                        {tab === "full" &&
                          (selected.share_full_conversation ? (
                            <div className="transcript">
                              {selected.shared_conversation.map((m) => (
                                <article
                                  className={"transcript-message " + m.role}
                                  key={m.id}
                                >
                                  <strong>
                                    {m.role === "tutor"
                                      ? "Tutor"
                                      : "VetAI · automático"}
                                  </strong>
                                  <MessageText text={m.content} />
                                  <time>{time(m.created_at)}</time>
                                </article>
                              ))}
                              <p className="tiny">
                                Cópia da conversa no momento do envio,
                                compartilhada com autorização.
                              </p>
                            </div>
                          ) : (
                            <div className="empty-state">
                              <Icon name="shield" size={32} />
                              <h3>Conversa não compartilhada</h3>
                              <p>
                                O tutor autorizou apenas o relato e o resumo.
                                Você pode conversar com ele no chat abaixo.
                              </p>
                            </div>
                          ))}
                        {tab === "events" && (
                          <ol className="timeline">
                            {selected.events.map((e, i) => (
                              <li key={i}>
                                <span className="timeline-dot" />
                                <div>
                                  <p>{e.description}</p>
                                  <time>{time(e.created_at)}</time>
                                </div>
                              </li>
                            ))}
                          </ol>
                        )}
                        {selected.status === "on_the_way" && (
                          <div className="travel-card">
                            <Icon name="pin" />
                            <div>
                              <strong>
                                {fresh
                                  ? "Localização compartilhada"
                                  : "A caminho · sem localização atual"}
                              </strong>
                              {fresh && selected.location ? (
                                <>
                                  <p>
                                    {selected.location.estimate
                                      ? "Cerca de " +
                                        Math.ceil(
                                          selected.location.estimate
                                            .duration_seconds / 60,
                                        ) +
                                        " min · " +
                                        (
                                          selected.location.estimate
                                            .distance_m / 1000
                                        ).toFixed(1) +
                                        " km de trajeto"
                                      : "Tempo de chegada indisponível"}
                                  </p>
                                  <small>
                                    Atualizada às{" "}
                                    {time(selected.location.updated_at)}
                                    {selected.location.estimate
                                      ? " · sem trânsito ao vivo"
                                      : ""}
                                  </small>
                                  <a
                                    target="_blank"
                                    rel="noreferrer"
                                    href={
                                      "https://www.google.com/maps/search/?api=1&query=" +
                                      selected.location.latitude +
                                      "," +
                                      selected.location.longitude
                                    }
                                  >
                                    Ver última posição no Google Maps
                                  </a>
                                </>
                              ) : (
                                <p>
                                  O tutor não compartilhou a posição ou ela está
                                  desatualizada. Nenhum tempo de chegada é
                                  presumido.
                                </p>
                              )}
                            </div>
                          </div>
                        )}
                        <div className="button-row">
                          {["delivered", "viewed"].includes(
                            selected.status,
                          ) && (
                            <button
                              disabled={busy}
                              onClick={() => status("acknowledge")}
                            >
                              Confirmar recebimento
                            </button>
                          )}
                          {["viewed", "acknowledged"].includes(
                            selected.status,
                          ) && (
                            <>
                              <button
                                disabled={busy}
                                className="primary"
                                onClick={() => status("accept")}
                              >
                                Aceitar caso
                                <Icon name="check" />
                              </button>
                              <button
                                disabled={busy}
                                onClick={() => status("refuse")}
                              >
                                Recusar
                              </button>
                            </>
                          )}
                          {["accepted", "on_the_way"].includes(
                            selected.status,
                          ) && (
                            <button
                              disabled={busy}
                              className="primary"
                              onClick={() => status("arrived")}
                            >
                              Registrar chegada
                            </button>
                          )}
                          {selected.status === "arrived" && (
                            <button
                              disabled={busy}
                              className="primary"
                              onClick={() => status("complete")}
                            >
                              Concluir caso
                            </button>
                          )}
                        </div>
                      </article>
                      <ReferralChat
                        recipient="tutor"
                        key={selected.id}
                        initial={selected}
                        token={token}
                        onChange={setSelected}
                      />
                    </>
                  )}
                </section>
              </div>
            </>
          )}
        </main>
      )}
    </div>
  );
}

function ClinicRegistration({ token }: { token: string }) {
  const [form, setForm] = useState({
    name: "",
    legal_name: "",
    tax_id: "",
    address: "",
    latitude: "",
    longitude: "",
    phone: "",
    opening_hours: "",
    responsible_name: "",
    responsible_document: "",
    google_place_id: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const result = await api.registerClinic(
        {
          ...form,
          latitude: Number(form.latitude),
          longitude: Number(form.longitude),
          google_place_id: form.google_place_id || null,
        },
        token,
      );
      setMessage(result.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha no cadastro");
    }
  }
  if (message)
    return (
      <main className="app-shell">
        <section className="blocked panel">
          <span>✓</span>
          <h1>Cadastro em verificação</h1>
          <p>{message}</p>
          <p>
            Entre novamente após a confirmação administrativa. Nenhum caso real
            está acessível enquanto isso.
          </p>
        </section>
      </main>
    );
  return (
    <main className="app-shell">
      <form className="panel registration-form" onSubmit={submit}>
        <p className="eyebrow">Cadastro institucional</p>
        <h1>Solicitar vínculo da clínica</h1>
        <p>
          Selecionar um local no Maps não prova titularidade. Envie os dados
          para conferência manual.
        </p>
        {error && <p className="error">{error}</p>}
        <div className="form-grid">
          {[
            ["name", "Nome da unidade"],
            ["legal_name", "Razão social"],
            ["tax_id", "CNPJ / identificação"],
            ["address", "Endereço completo"],
            ["latitude", "Latitude"],
            ["longitude", "Longitude"],
            ["phone", "Telefone"],
            ["opening_hours", "Horários declarados"],
            ["responsible_name", "Responsável pela conta"],
            ["responsible_document", "Documento do responsável"],
            ["google_place_id", "Place ID (opcional)"],
          ].map(([key, label]) => (
            <label key={key}>
              {label}
              <input
                required={key !== "google_place_id"}
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              />
            </label>
          ))}
        </div>
        <button className="primary">Enviar para verificação</button>
      </form>
    </main>
  );
}
