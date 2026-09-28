import { useState } from "react";
import type { Pet } from "../types";
import { api, errorText } from "../api";
import { ErrorNotice, Icon } from "./ui";
export const emptyPet: Pet = {
  name: "",
  species: "cao",
  age: "",
  weight_kg: null,
  breed: "",
  relevant_history: "",
};
export function PetFields({
  value,
  onChange,
}: {
  value: Pet;
  onChange: (pet: Pet) => void;
}) {
  return (
    <div className="form-grid">
      <label>
        Nome do animal
        <input
          required
          value={value.name}
          maxLength={100}
          onChange={(e) => onChange({ ...value, name: e.target.value })}
          placeholder="Como ele se chama?"
        />
      </label>
      <label>
        Espécie
        <select
          value={value.species}
          onChange={(e) =>
            onChange({ ...value, species: e.target.value as Pet["species"] })
          }
        >
          <option value="cao">Cachorro</option>
          <option value="gato">Gato</option>
        </select>
      </label>
      <label>
        Idade aproximada <small>opcional</small>
        <input
          value={value.age || ""}
          maxLength={80}
          onChange={(e) => onChange({ ...value, age: e.target.value })}
          placeholder="Ex.: 3 anos"
        />
      </label>
      <label>
        Peso em kg <small>opcional</small>
        <input
          type="number"
          step=".1"
          min=".1"
          max="150"
          value={value.weight_kg ?? ""}
          onChange={(e) =>
            onChange({
              ...value,
              weight_kg: e.target.value ? Number(e.target.value) : null,
            })
          }
          placeholder="Ex.: 8,5"
        />
      </label>
      <label className="span-2">
        Raça <small>opcional</small>
        <input
          value={value.breed || ""}
          maxLength={100}
          onChange={(e) => onChange({ ...value, breed: e.target.value })}
          placeholder="Pode deixar em branco"
        />
      </label>
      <label className="span-2">
        Histórico relevante <small>opcional</small>
        <textarea
          rows={3}
          maxLength={1000}
          value={value.relevant_history || ""}
          onChange={(e) =>
            onChange({ ...value, relevant_history: e.target.value })
          }
          placeholder="Condições conhecidas ou algo importante para a avaliação"
        />
      </label>
    </div>
  );
}
export function PetForm({
  token,
  initial,
  onSave,
  onCancel,
}: {
  token: string;
  initial?: Pet;
  onSave: (pet: Pet) => void;
  onCancel: () => void;
}) {
  const [value, setValue] = useState<Pet>(initial || emptyPet);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="panel pet-form"
      onSubmit={async (e) => {
        e.preventDefault();
        setBusy(true);
        try {
          onSave(await api.savePet(value, token));
        } catch (e) {
          setError(errorText(e));
        } finally {
          setBusy(false);
        }
      }}
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">Um cuidado mais próximo</p>
          <h2>{initial ? "Editar animal" : "Cadastrar animal"}</h2>
        </div>
        <button
          type="button"
          className="icon-button"
          aria-label="Fechar cadastro"
          onClick={onCancel}
        >
          <Icon name="close" />
        </button>
      </div>
      <p className="muted">
        Preencha o que souber. Você pode completar depois.
      </p>
      <ErrorNotice message={error} />
      <PetFields value={value} onChange={setValue} />
      <div className="button-row end">
        <button type="button" onClick={onCancel}>
          Voltar
        </button>
        <button className="primary" disabled={busy}>
          {busy ? "Salvando…" : "Salvar animal"}
        </button>
      </div>
    </form>
  );
}
