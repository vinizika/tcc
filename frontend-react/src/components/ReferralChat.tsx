import { useEffect, useRef, useState } from "react";
import { api, errorText } from "../api";
import type { Referral } from "../types";
import { ErrorNotice, Icon, time } from "./ui";
export function ReferralChat({
  initial,
  token,
  onChange,
  recipient = "clínica",
}: {
  initial: Referral;
  token: string;
  onChange: (r: Referral) => void;
  recipient?: "clínica" | "tutor";
}) {
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const callback = useRef(onChange);
  callback.current = onChange;
  const closed =
    !!initial.chat_closed_at ||
    ["refused", "cancelled", "completed"].includes(initial.status);
  // Continue refreshing status even if the separate human chat was closed.
  useEffect(() => {
    let live = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const r = await api.referral(initial.id, token);
        if (live) callback.current(r);
      } catch (e) {
        if (live) setError(errorText(e));
      } finally {
        if (live) timer = setTimeout(poll, 8000);
      }
    }
    timer = setTimeout(poll, 8000);
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [initial.id, token]);
  return (
    <section className="panel referral-chat">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Conversa com pessoas</p>
          <h2>Contato com {recipient === "tutor" ? "o tutor" : "a clínica"}</h2>
        </div>
        <Icon name="chat" />
      </div>
      <p className="tiny">
        Este canal é entre tutor e equipe. A pré-triagem automática não responde
        aqui.
      </p>
      <div className="human-messages">
        {initial.messages.length === 0 && (
          <p className="muted empty-chat">
            A conversa começa aqui. Envie uma mensagem.
          </p>
        )}
        {initial.messages.map((m) => (
          <article className={"human-message " + m.author_type} key={m.id}>
            <strong>{m.author_name}</strong>
            <p>{m.content}</p>
            <time>{time(m.created_at)}</time>
          </article>
        ))}
      </div>
      <ErrorNotice message={error} />
      {closed ? (
        <p className="notice">
          Conversa encerrada. O histórico continua disponível.
        </p>
      ) : (
        <>
          <form
            className="human-composer"
            onSubmit={async (e) => {
              e.preventDefault();
              if (!text.trim() || busy) return;
              setBusy(true);
              setError("");
              try {
                onChange(await api.message(initial.id, text, token));
                setText("");
              } catch (e) {
                setError(errorText(e));
              } finally {
                setBusy(false);
              }
            }}
          >
            <input
              aria-label="Mensagem para a clínica ou tutor"
              value={text}
              maxLength={2000}
              onChange={(e) => setText(e.target.value)}
              placeholder="Escreva uma mensagem…"
            />
            <button className="primary" disabled={busy || !text.trim()}>
              {busy ? "Enviando…" : "Enviar"}
              <Icon name="arrow" />
            </button>
          </form>
          <button
            className="text-button tiny"
            onClick={async () => {
              try {
                onChange(await api.closeChat(initial.id, token));
              } catch (e) {
                setError(errorText(e));
              }
            }}
          >
            Encerrar esta conversa
          </button>
        </>
      )}
    </section>
  );
}
