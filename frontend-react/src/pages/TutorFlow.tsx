import { useEffect, useRef, useState } from "react";
import { api, errorText } from "../api";
import type { Clinic, Conversation, Pet, Referral, Session } from "../types";
import { Brand, ErrorNotice, Icon, Status, time } from "../components/ui";
import { PetForm } from "../components/PetForm";
import { ClinicFinder } from "../components/ClinicFinder";
import { ShareReview } from "../components/ShareReview";
import { CaseView } from "../components/CaseView";
import { VoiceInput } from "../components/VoiceInput";

export function TutorFlow({
  session,
  onLogout,
}: {
  session: Session;
  onLogout: () => void;
}) {
  const token = session.access_token;
  const key = "vetai.chat." + session.principal.user_id;
  const [view, setView] = useState("chat");
  const [menu, setMenu] = useState(false);
  const [pets, setPets] = useState<Pet[]>([]);
  const [history, setHistory] = useState<Conversation[]>([]);
  const [cases, setCases] = useState<Referral[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [petId, setPetId] = useState("");
  const [draft, setDraft] = useState(
    () => sessionStorage.getItem(key + ".draft") || "",
  );
  const [error, setError] = useState(
    () => sessionStorage.getItem("vetai.notice") || "",
  );
  useEffect(() => {
    sessionStorage.removeItem("vetai.notice");
  }, []);
  const [busy, setBusy] = useState(false);
  const [editPet, setEditPet] = useState<Pet | null | undefined>(undefined);
  const [clinic, setClinic] = useState<Clinic | null>(null);
  const [referral, setReferral] = useState<Referral | null>(null);
  const [end, setEnd] = useState(true);
  const [moreBusy, setMoreBusy] = useState(false);
  const bottom = useRef<HTMLDivElement>(null);
  const pending = useRef<{ content: string; id: string } | null>(null);
  async function refresh() {
    try {
      const [p, h, r] = await Promise.all([
        api.pets(token),
        api.conversations(token),
        api.referrals(token),
      ]);
      setPets(p);
      setHistory(h);
      setEnd(h.length < 30);
      setCases(r);
    } catch (e) {
      setError(errorText(e));
    }
  }
  useEffect(() => {
    refresh();
    const id = sessionStorage.getItem(key);
    if (id)
      api
        .conversation(id, token)
        .then((c) => {
          setConversation(c);
          setPetId(c.pet_id || "");
        })
        .catch(() => sessionStorage.removeItem(key));
  }, [token]);
  useEffect(() => {
    sessionStorage.setItem(key + ".draft", draft);
  }, [draft, key]);
  useEffect(() => {
    if (conversation) sessionStorage.setItem(key, conversation.id);
  }, [conversation?.id, key]);
  useEffect(() => {
    if (conversation?.status !== "processing") return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const c = await api.conversation(conversation!.id, token);
        if (cancelled) return;
        setConversation(c);
        if (c.status === "processing") timer = setTimeout(poll, 2500);
        else refresh();
      } catch (e) {
        if (!cancelled) {
          setError(errorText(e));
          timer = setTimeout(poll, 5000);
        }
      }
    }
    timer = setTimeout(poll, 2000);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [conversation?.id, conversation?.status, token]);
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [conversation?.messages.length, conversation?.status, view]);
  function navigate(v: string) {
    setView(v);
    setMenu(false);
    setError("");
    if (v === "cases") refresh();
  }
  async function open(c: Conversation) {
    setError("");
    try {
      const full = await api.conversation(c.id, token);
      setConversation(full);
      setPetId(full.pet_id || "");
      navigate("chat");
    } catch (e) {
      setError(errorText(e));
    }
  }
  function fresh() {
    setConversation(null);
    sessionStorage.removeItem(key);
    setDraft("");
    pending.current = null;
    navigate("chat");
  }
  async function send(content = draft) {
    if (!content.trim() || busy || conversation?.status === "processing")
      return;
    setBusy(true);
    setError("");
    try {
      const c =
        conversation || (await api.createConversation(petId || null, token));
      setConversation(c);
      if (!pending.current || pending.current.content !== content)
        pending.current = { content, id: crypto.randomUUID() };
      const updated = await api.turn(c.id, content, pending.current.id, token);
      setConversation(updated);
      setDraft("");
      pending.current = null;
      refresh();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  async function associate(id: string) {
    try {
      if (conversation)
        setConversation(
          await api.associate(conversation.id, id || null, token),
        );
      setPetId(id);
    } catch (e) {
      setError(errorText(e));
    }
  }
  const latest = conversation?.messages.filter((m) => m.triage).at(-1);
  const processing = conversation?.status === "processing";
  const currentPet = pets.find((p) => p.id === petId);
  return (
    <div className="workspace">
      <aside className={"sidebar " + (menu ? "mobile-open" : "")}>
        <Brand />
        <button className="new-chat primary" onClick={fresh}>
          <Icon name="plus" />
          Nova conversa
        </button>
        <nav aria-label="Navegação principal">
          <button
            className={view === "chat" ? "active" : ""}
            onClick={() => navigate("chat")}
          >
            <Icon name="chat" />
            Conversa
          </button>
          <button
            className={view === "pets" ? "active" : ""}
            onClick={() => navigate("pets")}
          >
            <Icon name="paw" />
            Meus animais
          </button>
          <button
            className={view === "map" ? "active" : ""}
            onClick={() => navigate("map")}
          >
            <Icon name="pin" />
            Encontrar atendimento
          </button>
          <button
            className={view === "cases" || view === "case" ? "active" : ""}
            onClick={() => navigate("cases")}
          >
            <Icon name="clinic" />
            Encaminhamentos
          </button>
        </nav>
        <div className="history-label">Conversas anteriores</div>
        <div className="history-list">
          {history.length === 0 ? (
            <p className="tiny">Suas conversas aparecerão aqui.</p>
          ) : (
            history.map((c) => (
              <button
                title={c.title}
                className={conversation?.id === c.id ? "active" : ""}
                key={c.id}
                onClick={() => open(c)}
              >
                <span>{c.title}</span>
                <small>
                  {c.status === "processing"
                    ? "Analisando…"
                    : c.pet?.name || "Sem animal associado"}
                </small>
              </button>
            ))
          )}
          {!end && (
            <button
              disabled={moreBusy}
              onClick={async () => {
                setMoreBusy(true);
                try {
                  const page = await api.conversations(token, history.length);
                  setHistory([...history, ...page]);
                  setEnd(page.length < 30);
                } catch (e) {
                  setError(errorText(e));
                } finally {
                  setMoreBusy(false);
                }
              }}
            >
              Carregar mais
            </button>
          )}
        </div>
        <div className="sidebar-profile">
          <span className="avatar">
            {session.principal.display_name.slice(0, 1)}
          </span>
          <div>
            <strong>{session.principal.display_name}</strong>
            <small>
              {session.principal.demo
                ? "Conta acadêmica compartilhada"
                : "Tutor"}
            </small>
          </div>
          <button className="icon-button" onClick={onLogout} aria-label="Sair">
            <Icon name="logout" />
          </button>
        </div>
      </aside>
      <div className="workspace-main">
        <header className="workspace-header">
          <button
            className="icon-button mobile-menu"
            aria-label="Abrir navegação"
            onClick={() => setMenu(!menu)}
          >
            <Icon name="menu" />
          </button>
          <span className="header-context">
            <Icon name={view === "chat" ? "chat" : "paw"} />
            {view === "chat" ? "Orientação inicial" : "Seu espaço de cuidado"}
          </span>
          <div className="pet-switch">
            <Icon name="paw" />
            <label className="sr-only" htmlFor="current-pet">
              Animal desta conversa
            </label>
            <select
              id="current-pet"
              value={petId}
              disabled={processing}
              onChange={(e) => associate(e.target.value)}
            >
              <option value="">Associar animal depois</option>
              {pets.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </header>
        <ErrorNotice message={error} />
        {view === "chat" && (
          <main className="chat-page page-enter">
            {!conversation?.messages.length ? (
              <div className="chat-welcome">
                <span className="welcome-symbol">
                  <Icon name="paw" size={32} />
                </span>
                <p className="eyebrow">Vamos entender juntos</p>
                <h1>
                  {currentPet
                    ? "Como " + currentPet.name + " está hoje?"
                    : "O que está acontecendo?"}
                </h1>
                <p>
                  Conte o que mudou, há quanto tempo e os sinais que você
                  percebeu. Não precisa saber o nome do problema.
                </p>
                <div className="chat-prompts">
                  {[
                    "Mudou o comportamento",
                    "Parou de comer",
                    "Algo aconteceu agora",
                  ].map((s) => (
                    <button key={s} onClick={() => setDraft(s + ". ")}>
                      {s}
                      <Icon name="plus" size={16} />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="chat-messages" aria-live="polite">
                {conversation.messages.map((m) => (
                  <article className={"chat-message " + m.role} key={m.id}>
                    <div className="message-author">
                      {m.role === "assistant" ? (
                        <>
                          <span className="mini-brand">
                            <Icon name="paw" size={15} />
                          </span>
                          VetAI{" "}
                          <span className="tiny">· Orientação automática</span>
                        </>
                      ) : (
                        <>
                          Você <time>{time(m.created_at)}</time>
                        </>
                      )}
                    </div>
                    <div className="message-content">
                      {m.triage ? m.triage.justificativa : m.content}
                    </div>
                    {m.triage && (
                      <div
                        className={
                          "triage-card " + m.triage.classificacao.toLowerCase()
                        }
                      >
                        <strong>
                          {m.triage.classificacao === "EMERGENCIA"
                            ? "Procure atendimento agora"
                            : m.triage.classificacao === "INCERTO"
                              ? "Precisamos de mais informações"
                              : "Orientação inicial"}
                        </strong>
                        <p>{m.triage.recomendacao}</p>
                        {m.triage.sinais_de_alerta.length > 0 && (
                          <details>
                            <summary>Sinais que merecem atenção</summary>
                            <ul>
                              {m.triage.sinais_de_alerta.map((s, i) => (
                                <li key={i}>{s}</li>
                              ))}
                            </ul>
                          </details>
                        )}
                        {m.triage.classificacao === "EMERGENCIA" && (
                          <button
                            className="primary"
                            onClick={() => navigate("map")}
                          >
                            Encontrar atendimento
                            <Icon name="arrow" />
                          </button>
                        )}
                      </div>
                    )}
                    {m.retrieval && (
                      <details className="sources">
                        <summary>
                          {m.retrieval.used_count > 0
                            ? m.retrieval.used_count +
                              " trechos de referência usados"
                            : "Nenhuma referência relevante utilizada"}
                        </summary>
                        <p>
                          A consulta à base não garante que a orientação esteja
                          correta.
                        </p>
                        {m.sources?.map((s, i) => (
                          <p key={i}>
                            {s.title || s.source}
                            {s.cited ? " · citado na resposta" : ""}
                          </p>
                        ))}
                      </details>
                    )}
                  </article>
                ))}
                {processing && (
                  <div className="analysis-status" role="status">
                    <span className="pulse-dot" />
                    <div>
                      <strong>
                        Analisando seu relato e consultando a base…
                      </strong>
                      <p>
                        O processamento local pode levar alguns minutos. Seu
                        relato está salvo; você pode voltar depois.
                      </p>
                      <button
                        className="text-button"
                        onClick={() => navigate("map")}
                      >
                        Preciso encontrar atendimento agora →
                      </button>
                    </div>
                  </div>
                )}
                {conversation.status === "failed" && (
                  <div className="error" role="alert">
                    <p>{conversation.error}</p>
                    <button
                      onClick={() =>
                        send(
                          conversation.messages
                            .filter((m) => m.role === "tutor")
                            .at(-1)?.content || "",
                        )
                      }
                    >
                      Tentar análise novamente
                    </button>
                  </div>
                )}
                <div ref={bottom} />
              </div>
            )}
            <div className="composer-wrap">
              <form
                className="composer"
                onSubmit={(e) => {
                  e.preventDefault();
                  send();
                }}
              >
                <label className="sr-only" htmlFor="report">
                  Conte o que está acontecendo
                </label>
                <textarea
                  id="report"
                  value={draft}
                  maxLength={4000}
                  onChange={(e) => setDraft(e.target.value)}
                  placeholder={
                    currentPet
                      ? "Conte o que você percebeu com " + currentPet.name + "…"
                      : "Descreva com suas palavras…"
                  }
                  rows={2}
                  onKeyDown={(e) => {
                    if (
                      e.key === "Enter" &&
                      !e.shiftKey &&
                      !e.nativeEvent.isComposing
                    ) {
                      e.preventDefault();
                      send();
                    }
                  }}
                />
                <div className="composer-bottom">
                  <VoiceInput
                    onError={setError}
                    onText={(text) => setDraft(text)}
                    disabled={busy || processing}
                  />
                  <button
                    className="send-button"
                    disabled={!draft.trim() || busy || processing}
                    aria-label="Enviar relato"
                  >
                    <Icon name="arrow" />
                  </button>
                </div>
              </form>
              <p className="chat-disclaimer">
                A orientação automática pode errar e não é um diagnóstico. Em
                piora rápida, procure atendimento.{" "}
                <button className="text-button" onClick={() => navigate("map")}>
                  Ver clínicas
                </button>
              </p>
            </div>
          </main>
        )}
        {view === "pets" && (
          <main className="content-page page-enter">
            <div className="page-heading section-heading">
              <div>
                <p className="eyebrow">Um cuidado mais próximo</p>
                <h1>Meus animais</h1>
                <p className="muted">
                  Só o essencial. Você pode completar depois.
                </p>
              </div>
              <button className="primary" onClick={() => setEditPet(null)}>
                <Icon name="plus" />
                Cadastrar animal
              </button>
            </div>
            {editPet !== undefined ? (
              <PetForm
                key={editPet?.id || "new"}
                token={token}
                initial={editPet || undefined}
                onCancel={() => setEditPet(undefined)}
                onSave={() => {
                  setEditPet(undefined);
                  refresh();
                }}
              />
            ) : (
              <div className="pet-grid">
                {pets.length === 0 ? (
                  <div className="empty-state">
                    <Icon name="paw" size={40} />
                    <h2>Cada animal tem sua história</h2>
                    <p>
                      Cadastre quando quiser. Você também pode conversar sem
                      associar um animal.
                    </p>
                  </div>
                ) : (
                  pets.map((p) => (
                    <article className="panel pet-card" key={p.id}>
                      <span className="pet-avatar">
                        <Icon name="paw" size={30} />
                      </span>
                      <h2>{p.name}</h2>
                      <p>
                        {p.species === "cao" ? "Cachorro" : "Gato"}
                        {p.age ? " · " + p.age : ""}
                        {p.weight_kg ? " · " + p.weight_kg + " kg" : ""}
                      </p>
                      <p className="muted">{p.breed || "Raça não informada"}</p>
                      <button onClick={() => setEditPet(p)}>
                        Editar informações
                      </button>
                    </article>
                  ))
                )}
              </div>
            )}
          </main>
        )}
        {view === "map" && (
          <ClinicFinder
            session={session}
            canShare={!!latest && !processing}
            onBack={() => navigate("chat")}
            onChoose={(c) => {
              setClinic(c);
              navigate("review");
            }}
          />
        )}
        {view === "review" && clinic && conversation && (
          <ShareReview
            key={clinic.id + conversation.id}
            clinic={clinic}
            conversation={conversation}
            session={session}
            onBack={() => navigate("map")}
            onSent={(r) => {
              setReferral(r);
              navigate("case");
              refresh();
            }}
          />
        )}
        {view === "cases" && (
          <main className="content-page page-enter">
            <div className="page-heading">
              <p className="eyebrow">Continuidade do cuidado</p>
              <h1>Encaminhamentos</h1>
            </div>
            {cases.length === 0 ? (
              <div className="empty-state">
                <Icon name="clinic" size={40} />
                <h2>Nenhum envio por enquanto</h2>
                <p>Os casos que você autorizar compartilhar aparecerão aqui.</p>
                <button onClick={() => navigate("map")}>
                  Encontrar atendimento
                </button>
              </div>
            ) : (
              cases.map((r) => (
                <button
                  className="referral-row"
                  key={r.id}
                  onClick={() => {
                    setReferral(r);
                    navigate("case");
                  }}
                >
                  <div>
                    <strong>
                      {r.pet?.name || "Animal não associado"} · {r.clinic_name}
                    </strong>
                    <p>{time(r.created_at)}</p>
                  </div>
                  <Status value={r.status} />
                  <Icon name="arrow" />
                </button>
              ))
            )}
            {cases.length > 0 && cases.length % 30 === 0 && (
              <button
                onClick={async () => {
                  try {
                    setCases([
                      ...cases,
                      ...(await api.referrals(token, cases.length)),
                    ]);
                  } catch (e) {
                    setError(errorText(e));
                  }
                }}
              >
                Carregar mais
              </button>
            )}
          </main>
        )}
        {view === "case" && referral && (
          <CaseView
            key={referral.id}
            referral={referral}
            token={token}
            onChange={setReferral}
            onAlternatives={() => navigate("map")}
          />
        )}
      </div>
    </div>
  );
}
