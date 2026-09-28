import { useEffect, useRef, useState } from "react";
import { api, errorText } from "../api";
import { Icon } from "./ui";
export function VoiceInput({
  onText,
  onError,
  disabled,
}: {
  onText: (text: string) => void;
  onError: (message: string) => void;
  disabled: boolean;
}) {
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const file = useRef<HTMLInputElement>(null);
  const mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      if (recorder.current?.state === "recording") recorder.current.stop();
      recorder.current?.stream.getTracks().forEach((t) => t.stop());
    };
  }, []);
  async function transcribe(blob: Blob) {
    setBusy(true);
    try {
      const r = await api.voice(blob);
      if (mounted.current) onText(r.transcription);
    } catch (e) {
      onError(errorText(e));
    } finally {
      if (mounted.current) setBusy(false);
    }
  }
  async function toggle() {
    if (recording) {
      recorder.current?.stop();
      setRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (!mounted.current) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }
      const r = new MediaRecorder(stream);
      recorder.current = r;
      chunks.current = [];
      r.ondataavailable = (e) => chunks.current.push(e.data);
      r.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        if (mounted.current)
          transcribe(new Blob(chunks.current, { type: r.mimeType }));
      };
      r.start();
      setRecording(true);
    } catch {
      onError("Microfone indisponível. Você pode anexar um áudio ou digitar.");
    }
  }
  return (
    <>
      <button
        type="button"
        disabled={(disabled && !recording) || busy}
        className={"icon-button " + (recording ? "recording" : "")}
        onClick={toggle}
        title={recording ? "Parar e transcrever" : "Gravar relato"}
        aria-label={recording ? "Parar e transcrever" : "Gravar relato"}
      >
        <Icon name="mic" />
      </button>
      <button
        type="button"
        className="text-button"
        disabled={disabled || busy || recording}
        onClick={() => file.current?.click()}
      >
        {busy ? "Transcrevendo…" : "Anexar áudio"}
      </button>
      <input
        hidden
        type="file"
        accept="audio/*"
        ref={file}
        onChange={(e) => {
          const audio = e.target.files?.[0];
          if (audio) transcribe(audio);
          e.target.value = "";
        }}
      />
      {recording && (
        <span className="recording-label">Gravando · toque para parar</span>
      )}
    </>
  );
}
