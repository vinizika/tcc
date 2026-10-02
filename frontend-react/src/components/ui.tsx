import type { ReactNode } from "react";
export function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, ReactNode> = {
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    plus: <path d="M12 5v14M5 12h14" />,
    chat: (
      <path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4l-1 1v-9.5a8.5 8.5 0 0 1 18 0ZM7 9h10M7 13h6" />
    ),
    pin: (
      <>
        <path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 0 1 14 0Z" />
        <circle cx="12" cy="10" r="2" />
      </>
    ),
    paw: (
      <>
        <ellipse cx="12" cy="16" rx="6" ry="4" />
        <ellipse cx="5" cy="9" rx="2" ry="3" />
        <ellipse cx="10" cy="5" rx="2" ry="3" />
        <ellipse cx="16" cy="6" rx="2" ry="3" />
        <ellipse cx="20" cy="11" rx="2" ry="3" />
      </>
    ),
    clinic: (
      <>
        <path d="M4 21V7l8-4 8 4v14H4ZM9 21v-6h6v6M9 9h6m-3-3v6" />
      </>
    ),
    logout: (
      <>
        <path d="M9 4H4v16h5m5-13 5 5-5 5m-7-5h12" />
      </>
    ),
    check: <path d="m5 12 4 4L19 6" />,
    close: <path d="m6 6 12 12M6 18 18 6" />,
    mic: (
      <>
        <rect x="9" y="2" width="6" height="13" rx="3" />
        <path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-4 0h8" />
      </>
    ),
    phone: (
      <path d="M6 3H3v4c1 7 7 13 14 14h4v-4l-5-2-2 2c-4-2-6-4-7-7l2-2-3-5Z" />
    ),
    clock: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
    shield: (
      <>
        <path d="m12 2 8 4v6c0 5-8 10-8 10S4 17 4 12V6l8-4Z" />
        <path d="m8 12 3 3 5-6" />
      </>
    ),
    menu: <path d="M4 6h16M4 12h16M4 18h16" />,
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] || paths.paw}
    </svg>
  );
}
export function Brand() {
  return (
    <span className="brand">
      <span className="brand-mark">
        <Icon name="paw" size={23} />
      </span>
      vet<span className="brand-light">ia</span>
      <span className="brand-dot">.</span>
    </span>
  );
}
export function ErrorNotice({ message }: { message: string }) {
  return message ? (
    <div className="error" role="alert">
      {message}
    </div>
  ) : null;
}
export const statusLabels: Record<string, string> = {
  delivered: "Enviado",
  viewed: "Visualizado",
  acknowledged: "Recebido",
  accepted: "Aceito",
  refused: "Recusado",
  on_the_way: "A caminho",
  arrived: "Chegada registrada",
  completed: "Concluído",
  cancelled: "Cancelado",
  submitted: "Envio autorizado",
  chat_closed: "Conversa encerrada",
};
export function Status({ value }: { value: string }) {
  return (
    <span className={"status status-" + value}>
      <span className="status-dot" />
      {statusLabels[value] || value}
    </span>
  );
}
export const time = (value: string) =>
  new Date(value).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
