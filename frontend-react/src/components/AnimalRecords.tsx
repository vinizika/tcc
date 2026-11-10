// Histórico do animal como contexto da análise (rodada 34 do João):
// documentos que o tutor anexa e conversas anteriores do mesmo animal.
// O arquivo é lido uma vez; o que fica guardado é o resumo que o tutor revisa.
import { useEffect, useRef, useState } from "react";
import { api, errorText } from "../api";
import type { AnimalContext, DocumentDraft } from "../types";
import { Icon } from "./ui";

export type RecordsTarget = { petId?: string; conversationId?: string };
const MAX_MB = 10;
const ACCEPT = "application/pdf,image/jpeg,image/png,image/webp";
const EMPTY: AnimalContext = {
  scope: null,
  pet_name: null,
  documents: [],
  history: [],
};
// Uma resposta fora do formato (API antiga, rota simulada num teste) vira
// "sem histórico" em vez de derrubar a tela.
const safe = (c: unknown): AnimalContext => {
  const v = c as AnimalContext | null;
  return v && Array.isArray(v.documents) && Array.isArray(v.history)
    ? v
    : EMPTY;
};
const classLabel: Record<string, string> = {
  EMERGENCIA: "emergência",
  NAO_EMERGENCIA: "não emergência",
  INCERTO: "incerto",
};
const plural = (n: number, one: string, many: string) =>
  n + " " + (n === 1 ? one : many);

export function useAnimalRecords({
  token,
  provider,
  target,
  ensureTarget,
  onError,
  onChange,
}: {
  token: string;
  provider: "gemini" | "ollama";
  // Onde os documentos ficam: no animal ou, sem animal, na conversa.
  target: RecordsTarget | null;
  // Sem conversa nem animal ainda: cria a conversa na hora de guardar.
  ensureTarget?: () => Promise<RecordsTarget>;
  onError: (message: string) => void;
  onChange?: () => void;
}) {
  const [context, setContext] = useState<AnimalContext>(EMPTY);
  const [pending, setPending] = useState<File | null>(null);
  const [draft, setDraft] = useState<DocumentDraft | null>(null);
  const [busy, setBusy] = useState<"" | "reading" | "saving" | "removing">("");
  const key = target
    ? (target.petId || "") + "|" + (target.conversationId || "")
    : "";
  useEffect(() => {
    let current = true;
    if (!target) {
      setContext(EMPTY);
      return;
    }
    api
      .animalContext(target, token)
      .then((c) => current && setContext(safe(c)))
      .catch(() => current && setContext(EMPTY));
    return () => {
      current = false;
    };
  }, [key, token]);
  function pick(file: File) {
    onError("");
    if (file.size > MAX_MB * 1024 * 1024) {
      onError("O arquivo passa de " + MAX_MB + " MB. Envie um arquivo menor.");
      return;
    }
    setDraft(null);
    setPending(file);
  }
  async function read() {
    if (!pending) return;
    setBusy("reading");
    onError("");
    try {
      setDraft(await api.readDocument(pending, provider, token));
      setPending(null);
    } catch (e) {
      onError(errorText(e));
    } finally {
      setBusy("");
    }
  }
  async function save(value: DocumentDraft) {
    setBusy("saving");
    onError("");
    try {
      const where = target || (ensureTarget ? await ensureTarget() : null);
      if (!where) throw new Error("Escolha um animal ou abra uma conversa.");
      const { notice: _notice, ...data } = value;
      setContext(safe(await api.saveDocument(where, data, token)));
      setDraft(null);
      onChange?.();
    } catch (e) {
      onError(errorText(e));
    } finally {
      setBusy("");
    }
  }
  async function remove(documentId: string) {
    if (!target) return;
    setBusy("removing");
    onError("");
    try {
      setContext(safe(await api.removeDocument(target, documentId, token)));
      onChange?.();
    } catch (e) {
      onError(errorText(e));
    } finally {
      setBusy("");
    }
  }
  return {
    context,
    pending,
    draft,
    busy,
    provider,
    pick,
    read,
    save,
    remove,
    discard: () => {
      setPending(null);
      setDraft(null);
    },
  };
}
export type AnimalRecordsState = ReturnType<typeof useAnimalRecords>;

export function AttachDocumentButton({
  records,
  disabled,
  compact,
}: {
  records: AnimalRecordsState;
  disabled?: boolean;
  // Na caixa de mensagem do celular fica só o ícone.
  compact?: boolean;
}) {
  const input = useRef<HTMLInputElement>(null);
  const label = "Anexar documento do animal";
  return (
    <>
      <button
        type="button"
        className={"text-button attach-document" + (compact ? " compact" : "")}
        disabled={disabled || !!records.busy}
        onClick={() => input.current?.click()}
        title="Exame, receita, laudo ou carteira de vacinação (PDF ou foto)"
        aria-label={label}
      >
        <Icon name="clip" size={18} />
        <span>Anexar documento</span>
      </button>
      <input
        hidden
        type="file"
        accept={ACCEPT}
        ref={input}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) records.pick(file);
          e.target.value = "";
        }}
      />
    </>
  );
}

export function AnimalRecordsPanel({
  records,
  petName,
}: {
  records: AnimalRecordsState;
  petName?: string | null;
}) {
  const { context, pending, draft, busy, provider } = records;
  const [value, setValue] = useState<DocumentDraft | null>(null);
  const wrap = useRef<HTMLDivElement>(null);
  useEffect(() => setValue(draft), [draft]);
  useEffect(() => {
    // O cartão de leitura ou de revisão aparece acima da caixa de envio: a
    // tela vai até ele, para não abrir escondido no celular.
    if (pending || value)
      wrap.current
        ?.querySelector(".document-review")
        ?.scrollIntoView({ block: "start" });
  }, [!!pending, !!value]);
  const name = petName || context.pet_name;
  const where = name ? "no histórico de " + name : "nesta conversa";
  const total = context.documents.length + context.history.length;
  if (!pending && !value && total === 0) return null;
  return (
    <div className="animal-records" ref={wrap}>
      {pending && (
        <div
          className="document-review"
          role="group"
          aria-label="Ler documento"
        >
          <strong>Ler “{pending.name}”?</strong>
          <p className="tiny">
            {provider === "gemini"
              ? "O arquivo será enviado ao Google Gemini para leitura e não fica guardado. Você revisa o resumo antes de salvar."
              : "O arquivo será lido no servidor local e não fica guardado. O modelo local só aproveita PDF com texto."}
          </p>
          <div className="button-row">
            <button
              type="button"
              className="primary"
              disabled={!!busy}
              onClick={records.read}
            >
              {busy === "reading" ? "Lendo o documento…" : "Ler documento"}
            </button>
            <button type="button" disabled={!!busy} onClick={records.discard}>
              Cancelar
            </button>
          </div>
          {busy === "reading" && (
            <p className="tiny" role="status">
              Pode levar alguns segundos.
            </p>
          )}
        </div>
      )}
      {value && (
        <form
          className="document-review"
          aria-label="Revisar resumo do documento"
          onSubmit={(e) => {
            e.preventDefault();
            records.save(value);
          }}
        >
          <strong>Confira o que foi lido</strong>
          <p className="tiny">
            Só este resumo fica guardado {where}, e passa a ser considerado nas
            próximas análises. Corrija o que estiver errado e apague dados
            pessoais.
            {value.notice ? " " + value.notice : ""}
          </p>
          <div className="document-fields">
            <label>
              Tipo de documento
              <input
                required
                maxLength={80}
                value={value.kind}
                onChange={(e) => setValue({ ...value, kind: e.target.value })}
              />
            </label>
            <label>
              Data <small>opcional</small>
              <input
                maxLength={40}
                value={value.document_date}
                placeholder="DD/MM/AAAA"
                onChange={(e) =>
                  setValue({ ...value, document_date: e.target.value })
                }
              />
            </label>
          </div>
          <label>
            Resumo
            <textarea
              required
              rows={5}
              maxLength={1200}
              value={value.summary}
              onChange={(e) => setValue({ ...value, summary: e.target.value })}
            />
          </label>
          <div className="button-row">
            <button
              className="primary"
              disabled={!!busy || !value.summary.trim()}
            >
              {busy === "saving" ? "Guardando…" : "Guardar resumo"}
            </button>
            <button type="button" disabled={!!busy} onClick={records.discard}>
              Descartar
            </button>
          </div>
        </form>
      )}
      {total > 0 && (
        <details className="records-list">
          <summary>
            Contexto {name ? "de " + name : "desta conversa"} na análise:{" "}
            {[
              context.documents.length
                ? plural(context.documents.length, "documento", "documentos")
                : "",
              context.history.length
                ? plural(
                    context.history.length,
                    "conversa anterior",
                    "conversas anteriores",
                  )
                : "",
            ]
              .filter(Boolean)
              .join(" e ")}
          </summary>
          <ul>
            {context.documents.map((d) => (
              <li key={d.id}>
                <div>
                  <strong>
                    {d.kind}
                    {d.document_date ? " · " + d.document_date : ""}
                  </strong>
                  <p>{d.summary}</p>
                </div>
                <button
                  type="button"
                  className="text-button"
                  disabled={!!busy}
                  onClick={() => records.remove(d.id)}
                  aria-label={"Remover " + d.kind}
                >
                  Remover
                </button>
              </li>
            ))}
            {context.history.map((h) => (
              <li key={h.conversation_id}>
                <div>
                  <strong>
                    Conversa de {h.date} ({h.ago}) ·{" "}
                    {classLabel[h.classification] || h.classification}
                  </strong>
                  <p>“{h.report}”</p>
                </div>
              </li>
            ))}
          </ul>
          <p className="tiny">
            Documentos e conversas anteriores são contexto, não o relato de
            hoje. Eles só aumentam a cautela da análise.
          </p>
        </details>
      )}
    </div>
  );
}

// Na página "Meus animais": os documentos de um animal e o botão de anexar.
export function PetDocuments({
  token,
  provider,
  petId,
  petName,
  onError,
  onChange,
}: {
  token: string;
  provider: "gemini" | "ollama";
  petId: string;
  petName: string;
  onError: (message: string) => void;
  onChange?: () => void;
}) {
  const records = useAnimalRecords({
    token,
    provider,
    target: { petId },
    onError,
    onChange,
  });
  return (
    <div className="pet-documents">
      <AnimalRecordsPanel records={records} petName={petName} />
      <AttachDocumentButton records={records} />
    </div>
  );
}
