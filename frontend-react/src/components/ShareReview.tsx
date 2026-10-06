import { useRef, useState } from "react";
import { api, errorText } from "../api";
import type { Clinic, Conversation, Pet, Referral, Session } from "../types";
import { ErrorNotice, Icon } from "./ui";
import { describeSexAndStatus } from "./PetForm";
export function ShareReview({
  clinic,
  conversation,
  session,
  onBack,
  onSent,
}: {
  clinic: Clinic;
  conversation: Conversation;
  session: Session;
  onBack: () => void;
  onSent: (r: Referral) => void;
}) {
  const responses = conversation.messages.filter((m) => m.triage);
  const triage = responses[responses.length - 1]?.triage;
  const [summary, setSummary] = useState(
    conversation.messages
      .filter((m) => m.role === "tutor")
      .map((m) => m.content)
      .join("\n\n"),
  );
  const [pet, setPet] = useState<Pet | null>(conversation.pet);
  const [name, setName] = useState(session.principal.display_name);
  const [phone, setPhone] = useState("");
  const [consent, setConsent] = useState(false);
  const [full, setFull] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const key = useRef(crypto.randomUUID());
  if (!triage) return <p>Conclua a pré-triagem antes de compartilhar.</p>;
  async function send() {
    setBusy(true);
    setError("");
    try {
      const r = await api.createReferral(
        {
          clinic_id: clinic.id,
          idempotency_key: key.current,
          conversation_id: conversation.id,
          pet,
          contact: { name, phone },
          triage: {
            schema_version: "triage_snapshot.v1",
            original_report: conversation.messages.find(
              (m) => m.role === "tutor",
            )!.content,
            classification: triage!.classificacao,
            justification: triage!.justificativa,
            warning_signs: triage!.sinais_de_alerta,
            recommendation: triage!.recomendacao,
            automatic: true,
          },
          reviewed_summary: summary,
          consent_to_share: consent,
          share_full_conversation: full,
        },
        session.access_token,
      );
      onSent(r);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="review-page page-enter">
      <button className="text-button" onClick={onBack}>
        ← Voltar às clínicas
      </button>
      <div className="page-heading">
        <p className="eyebrow">Você decide o que compartilhar</p>
        <h1>Revise antes de enviar</h1>
        <p>
          Destino: <strong>{clinic.name}</strong>
        </p>
      </div>
      <ErrorNotice message={error} />
      <div className="review-columns">
        <div className="panel">
          <h2>Seu relato, com suas palavras</h2>
          <p className="muted">Corrija ou acrescente o que for importante.</p>
          <label>
            Resumo do caso
            <textarea
              rows={8}
              maxLength={5000}
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
            />
          </label>
          <div className="auto-summary">
            <p className="eyebrow">Pré-triagem automática</p>
            <strong>{triage.classificacao.replaceAll("_", " ")}</strong>
            <p>{triage.justificativa}</p>
          </div>
          <p className="tiny">
            O relato original e a resposta automática também acompanham o
            resumo. A conversa completa só será enviada se você autorizar
            abaixo.
          </p>
        </div>
        <div className="panel">
          <h2>Animal e contato</h2>
          {pet ? (
            <div className="selected-pet">
              <Icon name="paw" />
              <div>
                <strong>{pet.name}</strong>
                <p>
                  {pet.species === "cao" ? "Cachorro" : "Gato"}
                  {pet.age ? " · " + pet.age : ""}
                  {pet.weight_kg ? " · " + pet.weight_kg + " kg" : ""}
                  {describeSexAndStatus(pet)
                    ? " · " + describeSexAndStatus(pet)
                    : ""}
                </p>
              </div>
              <button className="text-button" onClick={() => setPet(null)}>
                Não compartilhar dados do animal
              </button>
            </div>
          ) : (
            <p className="muted">
              Sem cadastro de animal compartilhado. Você pode descrever o animal
              no resumo.
            </p>
          )}
          <label>
            Nome para contato
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={200}
            />
          </label>
          <label>
            Telefone <small>opcional</small>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              maxLength={30}
            />
          </label>
          <label className="consent">
            <input
              type="checkbox"
              checked={full}
              onChange={(e) => setFull(e.target.checked)}
            />
            <span>
              Também autorizo compartilhar a conversa completa desta
              pré-triagem.
            </span>
          </label>
          <label className="consent">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
            />
            <span>
              Autorizo enviar o resumo, o relato original, a pré-triagem e os
              dados preenchidos acima para esta clínica.
            </span>
          </label>
          <button
            className="primary full-width"
            disabled={!consent || !summary.trim() || busy}
            onClick={send}
          >
            {busy ? "Enviando…" : "Confirmar e compartilhar"}
            <Icon name="arrow" />
          </button>
          <p className="tiny">
            O envio não confirma uma vaga. A clínica ainda precisa responder.
          </p>
        </div>
      </div>
    </section>
  );
}
