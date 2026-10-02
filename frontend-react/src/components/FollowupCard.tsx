import { useState } from "react";
import type { Followup } from "../types";

export function FollowupCard({
  followup,
  disabled,
  onSend,
}: {
  followup: Followup;
  disabled: boolean;
  onSend: (content: string, option: string) => void;
}) {
  const [option, setOption] = useState("");
  const [extra, setExtra] = useState("");
  if (followup.state === "completed") return null;
  if (followup.state === "insufficient")
    return <p role="status">{followup.guidance}</p>;
  if (followup.state === "asking")
    return (
      <p className="followup-question">
        <strong>{followup.question}</strong>
      </p>
    );
  return (
    <form
      className="followup-form"
      onSubmit={(e) => {
        e.preventDefault();
        if (option && !disabled)
          onSend(option + (extra.trim() ? " — " + extra.trim() : ""), option);
      }}
    >
      <fieldset disabled={disabled}>
        <legend>{followup.question}</legend>
        <p>Escolha o que você observou. Tudo bem não saber.</p>
        {followup.options.map((value) => (
          <label key={value}>
            <input
              type="radio"
              name={followup.question_id}
              value={value}
              checked={option === value}
              onChange={() => setOption(value)}
            />{" "}
            {value}
          </label>
        ))}
        <label>
          Complemento (opcional)
          <textarea
            value={extra}
            maxLength={3000}
            onChange={(e) => setExtra(e.target.value)}
          />
        </label>
        <button className="primary" disabled={!option || disabled}>
          Enviar resposta
        </button>
      </fieldset>
    </form>
  );
}
