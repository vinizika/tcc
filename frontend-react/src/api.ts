import type {
  ChatResponse,
  Clinic,
  ClinicSearch,
  Conversation,
  Dashboard,
  Pet,
  Principal,
  PublicConfig,
  Referral,
  Session,
} from "./types";
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}
async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const response = await fetch(BASE + path, {
    ...options,
    headers: {
      ...(!(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...(token ? { Authorization: "Bearer " + token } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    let message =
      response.status === 504
        ? "A análise está demorando mais que o esperado. Seu relato foi preservado."
        : "Não foi possível concluir. Tente novamente.";
    try {
      const data = await response.json();
      if (typeof data.detail === "string") message = data.detail;
      else if (Array.isArray(data.detail))
        message =
          "Confira os campos preenchidos: " +
          data.detail.map((x: { msg: string }) => x.msg).join("; ");
      else if (data.message) message = data.message;
    } catch {}
    throw new ApiError(response.status, message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
const body = (data: unknown) => ({
  method: "POST",
  body: JSON.stringify(data),
});
export const api = {
  config: () => request<PublicConfig>("/auth/config"),
  me: (token: string) => request<Principal>("/auth/me", {}, token),
  logout: (token: string) =>
    request<void>("/auth/logout", { method: "POST" }, token),
  demoLogin: (account: string) =>
    request<Session>("/auth/demo", body({ account })),
  login: (email: string, password: string) =>
    request<Session>("/auth/login", body({ email, password })),
  signup: (data: unknown) =>
    request<{ user_id: string; email_confirmation_required: boolean }>(
      "/auth/signup",
      body(data),
    ),
  registerClinic: (data: unknown, token: string) =>
    request<{ id: string; status: string; message: string }>(
      "/clinics/register",
      body(data),
      token,
    ),
  chat: (question: string) =>
    request<ChatResponse>("/chat/", body({ question })),
  pets: (token: string, offset = 0) =>
    request<Pet[]>("/workspace/pets?limit=100&offset=" + offset, {}, token),
  savePet: (pet: Pet, token: string) => {
    const { id, name, species, age, weight_kg, breed, relevant_history } = pet;
    const data = { name, species, age, weight_kg, breed, relevant_history };
    return request<Pet>(
      "/workspace/pets" + (id ? "/" + id : ""),
      { method: id ? "PUT" : "POST", body: JSON.stringify(data) },
      token,
    );
  },
  conversations: (token: string, offset = 0) =>
    request<Conversation[]>(
      "/workspace/conversations?offset=" + offset,
      {},
      token,
    ),
  createConversation: (pet_id: string | null, token: string) =>
    request<Conversation>("/workspace/conversations", body({ pet_id }), token),
  conversation: (id: string, token: string) =>
    request<Conversation>("/workspace/conversations/" + id, {}, token),
  associate: (id: string, pet_id: string | null, token: string) =>
    request<Conversation>(
      "/workspace/conversations/" + id,
      { method: "PATCH", body: JSON.stringify({ pet_id }) },
      token,
    ),
  turn: (
    id: string,
    content: string,
    request_id: string,
    token: string,
    attendant_provider: "gemini" | "ollama" = "gemini",
    answer: {
      origin?: "text" | "form";
      question_id?: string;
      selected_option?: string;
    } = {},
  ) =>
    request<Conversation>(
      "/workspace/conversations/" + id + "/messages",
      body({ content, request_id, attendant_provider, ...answer }),
      token,
    ),
  voice: (file: Blob) => {
    const form = new FormData();
    form.append(
      "audio",
      file,
      file instanceof File ? file.name : "relato.webm",
    );
    return request<{ transcription: string }>("/voice/", {
      method: "POST",
      body: form,
    });
  },
  geocode: (query: string) =>
    request<{
      latitude: number;
      longitude: number;
      formatted_address: string;
      source: string;
    }>("/clinics/geocode", body({ query })),
  clinics: (
    latitude: number,
    longitude: number,
    open_now = false,
    radius_m = 10000,
  ) =>
    request<ClinicSearch>(
      "/clinics/search",
      body({ latitude, longitude, open_now, radius_m }),
    ),
  participants: (token: string, lat = 0, lng = 0) =>
    request<Clinic[]>(
      "/clinics/participants?latitude=" + lat + "&longitude=" + lng,
      {},
      token,
    ),
  createReferral: (data: unknown, token: string) =>
    request<Referral>("/referrals/", body(data), token),
  referrals: (token: string, offset = 0) =>
    request<Referral[]>("/referrals/?offset=" + offset, {}, token),
  referral: (id: string, token: string) =>
    request<Referral>("/referrals/" + id, {}, token),
  dashboard: (token: string, offset = 0, activeOnly = false) =>
    request<Dashboard>(
      "/referrals/dashboard?offset=" + offset + "&active_only=" + activeOnly,
      {},
      token,
    ),
  status: (id: string, action: string, token: string, reason?: string) =>
    request<Referral>(
      "/referrals/" + id + "/status",
      body({ action, reason }),
      token,
    ),
  message: (id: string, content: string, token: string) =>
    request<Referral>(
      "/referrals/" + id + "/messages",
      body({ content }),
      token,
    ),
  closeChat: (id: string, token: string) =>
    request<Referral>(
      "/referrals/" + id + "/close-chat",
      { method: "POST" },
      token,
    ),
  location: (id: string, data: unknown, token: string) =>
    request<Referral>(
      "/referrals/" + id + "/location",
      { method: "PUT", body: JSON.stringify(data) },
      token,
    ),
};
export const errorText = (e: unknown) =>
  e instanceof Error
    ? e.message
    : "Não foi possível concluir. Tente novamente.";
