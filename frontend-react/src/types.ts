export type Role = "tutor" | "clinic";
export type Principal = {
  user_id: string;
  role: Role;
  display_name: string;
  clinic_id?: string;
  clinic_verified: boolean;
  demo: boolean;
};
export type Session = { access_token: string; principal: Principal };
export type PublicConfig = {
  quick_login_enabled: boolean;
  own_accounts_enabled: boolean;
  maps_key: string;
  map_id: string;
  maps_key_kind: string;
  maps_provider: string;
};
export type Triage = {
  classificacao: "EMERGENCIA" | "NAO_EMERGENCIA" | "INCERTO";
  justificativa: string;
  sinais_de_alerta: string[];
  recomendacao: string;
};
export type Pet = {
  id?: string;
  name: string;
  species: "cao" | "gato";
  age?: string | null;
  weight_kg?: number | null;
  breed?: string | null;
  relevant_history?: string | null;
  sex?: "macho" | "femea" | null;
  neutered?: boolean | null;
  reproductive_status?: "prenhe" | "amamentando" | null;
};
export type Followup = {
  state: "asking" | "form" | "completed" | "insufficient";
  question_id?: string;
  question?: string | null;
  options: string[];
  guidance?: string;
};
export type ChatMessage = {
  followup?: Followup;
  origin?: "text" | "form";
  question_id?: string;
  selected_option?: string;
  id: string;
  role: "tutor" | "assistant";
  content: string;
  created_at: string;
  triage?: Triage;
  retrieval?: { used_count: number; returned_count: number };
  sources?: {
    title: string;
    display_title?: string;
    source: string;
    cited: boolean;
    references?: {
      title: string;
      url?: string;
      year?: number | string;
      journal?: string;
    }[];
  }[];
  provenance?: {
    attendant?: {
      provider: string;
      model: string;
      fallback_from?: string | null;
    };
  } | null;
};
export type Conversation = {
  followup?: Followup;
  id: string;
  title: string;
  pet_id: string | null;
  pet: Pet | null;
  messages: ChatMessage[];
  status: "idle" | "processing" | "failed";
  error: string | null;
  updated_at: string;
  request_id?: string;
};
export type ChatResponse = {
  answer: string;
  triage?: Triage;
  conversation_id?: string;
};
export type Clinic = {
  id: string;
  name: string;
  address?: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  distance_kind: "straight_line" | "route";
  phone?: string;
  opening_hours?: string;
  open_now?: boolean;
  rating?: number;
  review_count?: number;
  source: "demo" | "google" | "platform";
  participant: boolean;
  verified: boolean;
  digital_referral_enabled: boolean;
  google_maps_uri?: string;
};
export type ClinicSearch = {
  mode: "demo" | "real";
  clinics: Clinic[];
  notice: string;
  google_attribution_required: boolean;
};
export type ReferralEvent = {
  type: string;
  description: string;
  actor_type: string;
  created_at: string;
};
export type Message = {
  id: string;
  author_type: Role;
  author_name: string;
  content: string;
  created_at: string;
};
export type TravelLocation = {
  latitude: number;
  longitude: number;
  accuracy_m?: number;
  updated_at: string;
  estimate?: {
    duration_seconds: number;
    distance_m: number;
    mode: string;
    traffic_included: boolean;
  } | null;
};
export type Referral = {
  id: string;
  tutor_id: string;
  clinic_id: string;
  clinic_name: string;
  status: string;
  pet: Pet | null;
  conversation_id?: string;
  share_full_conversation: boolean;
  shared_conversation: ChatMessage[];
  location?: TravelLocation | null;
  contact: { name?: string; phone?: string; email?: string };
  triage: {
    original_report: string;
    classification: Triage["classificacao"];
    justification: string;
    warning_signs: string[];
    recommendation: string;
    automatic: true;
  };
  reviewed_summary: string;
  created_at: string;
  updated_at: string;
  events: ReferralEvent[];
  messages: Message[];
  chat_closed_at?: string;
};
export type Dashboard = {
  has_more: boolean;
  metrics: {
    confirmed_on_the_way: number;
    awaiting_review: number;
    arrived_last_24h: number;
    total_received: number;
    definitions: Record<string, string>;
  };
  referrals: Referral[];
  polling_interval_s: number;
};
