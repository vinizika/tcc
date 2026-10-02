import type { Triage } from "../types";
import { Icon } from "./ui";

// Presentation only: never changes the clinical result or calls another model.
// Keep the original explanation available, including for older conversations.
const COPY = {
  EMERGENCIA: {
    context:
      "Entendo sua preocupação. Os sinais descritos precisam de avaliação veterinária agora, para que seu animal receba o cuidado necessário.",
    title: "Procure atendimento agora",
    steps: [
      "Organize a ida a um atendimento veterinário; não espere outra resposta aqui para buscar ajuda.",
      "Se possível, avise a clínica sobre os sinais e peça orientação para o transporte, sem atrasar a saída.",
    ],
  },
  NAO_EMERGENCIA: {
    context:
      "Pelas informações disponíveis, a análise não identificou uma emergência. Uma consulta pode ajudar a entender a causa dos sinais e orientar os cuidados.",
    title: "Próximos cuidados",
    steps: [
      "Anote quando a mudança começou e o que você observou para contar ao veterinário.",
      "Se aparecerem novos sinais ou houver piora, procure orientação veterinária novamente.",
    ],
  },
  INCERTO: {
    context:
      "Entendo sua preocupação. Ainda faltam informações para orientar a urgência com segurança; isso não significa que esteja tudo bem.",
    title: "Precisamos entender melhor",
    steps: [
      "Conte apenas o que conseguiu observar; tudo bem responder que não sabe.",
      "Se houver piora ou você estiver em dúvida, entre em contato com uma clínica sem esperar concluir a conversa.",
    ],
  },
};

export function TriageGuidance({
  triage,
  onFindCare,
}: {
  triage: Triage;
  onFindCare: () => void;
}) {
  const copy = COPY[triage.classificacao];
  const signs = [...new Set(triage.sinais_de_alerta.map((s) => s.trim()))].filter(
    (s) => /[\p{L}\p{N}]/u.test(s),
  );
  return (
    <>
      <p className="message-content">{copy.context}</p>
      {signs.length > 0 && (
        <p className="reported-signs">
          <strong>Sinais identificados no relato: </strong>
          {signs.join("; ")}.
        </p>
      )}
      <div className={"triage-card " + triage.classificacao.toLowerCase()}>
        <strong>{copy.title}</strong>
        <p>{triage.recomendacao}</p>
        <ul className="care-steps">
          {copy.steps.map((step) => <li key={step}>{step}</li>)}
        </ul>
        {triage.classificacao === "EMERGENCIA" && (
          <button className="primary" onClick={onFindCare}>
            Encontrar atendimento <Icon name="arrow" />
          </button>
        )}
      </div>
      {triage.justificativa.trim() && (
        <details className="analysis-explanation">
          <summary>Ver justificativa original da análise</summary>
          <p>{triage.justificativa}</p>
        </details>
      )}
    </>
  );
}
