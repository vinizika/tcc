import { useEffect, useState } from "react";
import { api, errorText } from "./api";
import { ClinicDashboard } from "./pages/ClinicDashboard";
import { TutorFlow } from "./pages/TutorFlow";
import { Brand, ErrorNotice, Icon } from "./components/ui";
import { PetFields, emptyPet } from "./components/PetForm";
import { loadSession, saveSession } from "./session";
import type { Pet, PublicConfig, Session } from "./types";

export function App() {
  const [session, setSession] = useState<Session | null>(loadSession());
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const [own, setOwn] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    api
      .config()
      .then(setConfig)
      .catch((e) => setError(errorText(e)));
    const s = loadSession();
    if (s)
      api
        .me(s.access_token)
        .then((p) => setSession({ ...s, principal: p }))
        .catch(() => {
          saveSession(null);
          setSession(null);
        });
  }, []);
  function enter(s: Session) {
    saveSession(s);
    setSession(s);
  }
  async function quick(account: string) {
    setBusy(true);
    setError("");
    try {
      enter(await api.demoLogin(account));
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  async function logout() {
    if (session) await api.logout(session.access_token).catch(() => {});
    saveSession(null);
    setSession(null);
    setOwn(false);
    setError("");
  }
  if (session)
    return session.principal.role === "tutor" ? (
      <TutorFlow session={session} onLogout={logout} />
    ) : (
      <ClinicDashboard session={session} onLogout={logout} />
    );
  return (
    <main className="entry">
      <section className="entry-story">
        <Brand />
        <div className="entry-copy">
          <span className="eyebrow">Perto de você. Pelo seu animal.</span>
          <h1>
            O próximo passo,
            <br />
            <em>com mais clareza.</em>
          </h1>
          <p>
            Conte o que está acontecendo. Entenda a orientação inicial e
            encontre quem pode cuidar.
          </p>
          <div className="story-illustration" aria-hidden="true">
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <div className="illustration-paw">
              <Icon name="paw" size={90} />
            </div>
            <span className="floating-tag tag-one">
              <Icon name="chat" /> Espaço para ouvir
            </span>
            <span className="floating-tag tag-two">
              <Icon name="pin" /> Cuidado por perto
            </span>
          </div>
        </div>
        <p className="entry-foot">
          Pré-triagem de cães e gatos · Projeto acadêmico FEI
        </p>
      </section>
      <section className="entry-access">
        <div className="access-inner">
          <span className="eyebrow">Bem-vindo ao VetIA</span>
          <h2>{own ? "Seu espaço de cuidado" : "Como você quer entrar?"}</h2>
          <p className="muted">
            {own
              ? "Entre ou crie sua conta para guardar animais e conversas."
              : "Um lugar para tutores e para quem recebe o cuidado."}
          </p>
          <ErrorNotice message={error} />
          {own ? (
            <OwnAccount onSession={enter} onBack={() => setOwn(false)} />
          ) : (
            <>
              <div className="entry-options">
                <button
                  className="entry-option"
                  disabled={busy || !config?.quick_login_enabled}
                  onClick={() => quick("tutor-a")}
                >
                  <span className="option-icon">
                    <Icon name="paw" size={26} />
                  </span>
                  <span>
                    <strong>Entrar como tutor</strong>
                    <small>Conversar e encontrar atendimento</small>
                  </span>
                  <Icon name="arrow" />
                </button>
                <button
                  className="entry-option"
                  disabled={busy || !config?.quick_login_enabled}
                  onClick={() => quick("clinic-a")}
                >
                  <span className="option-icon">
                    <Icon name="clinic" size={26} />
                  </span>
                  <span>
                    <strong>Entrar como clínica</strong>
                    <small>Receber casos e falar com tutores</small>
                  </span>
                  <Icon name="arrow" />
                </button>
                <button
                  className="entry-option own"
                  onClick={() => setOwn(true)}
                >
                  <span className="option-icon">
                    <Icon name="shield" size={26} />
                  </span>
                  <span>
                    <strong>Entrar ou cadastrar uma conta própria</strong>
                    <small>Seu perfil, seus animais e seu histórico</small>
                  </span>
                  <Icon name="arrow" />
                </button>
              </div>
              <p className="access-note">
                Os dois acessos rápidos usam contas acadêmicas compartilhadas.
                Use dados de teste nessas contas.
              </p>
            </>
          )}
          <div className="entry-safety">
            <Icon name="phone" />
            <p>
              Em risco imediato, procure uma clínica. A orientação automática
              não substitui a avaliação veterinária.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
function OwnAccount({
  onSession,
  onBack,
}: {
  onSession: (s: Session) => void;
  onBack: () => void;
}) {
  const [signup, setSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<"tutor" | "clinic">("tutor");
  const [addPet, setAddPet] = useState(false);
  const [pet, setPet] = useState<Pet>(emptyPet);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  return (
    <form
      className="auth-form"
      onSubmit={async (e) => {
        e.preventDefault();
        setError("");
        setBusy(true);
        try {
          if (signup) {
            const result = await api.signup({
              email,
              password,
              display_name: name,
              role,
            });
            if (result.email_confirmation_required) {
              setNotice(
                "Confira seu e-mail para confirmar a conta antes de entrar.",
              );
              setSignup(false);
              return;
            }
          }
          const session = await api.login(email, password);
          if (signup && role === "tutor" && addPet) {
            try {
              await api.savePet(pet, session.access_token);
            } catch {
              sessionStorage.setItem(
                "vetai.notice",
                "Conta criada, mas o cadastro do animal falhou. Cadastre-o em Meus animais.",
              );
            }
          }
          onSession(session);
        } catch (e) {
          setError(errorText(e));
        } finally {
          setBusy(false);
        }
      }}
    >
      <div className="tabs">
        <button
          type="button"
          className={!signup ? "active" : ""}
          onClick={() => setSignup(false)}
        >
          Entrar
        </button>
        <button
          type="button"
          className={signup ? "active" : ""}
          onClick={() => setSignup(true)}
        >
          Criar conta
        </button>
      </div>
      <ErrorNotice message={error} />
      {notice && <p className="notice">{notice}</p>}
      {signup && (
        <>
          <label>
            Seu nome
            <input
              required
              value={name}
              minLength={2}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
            />
          </label>
          <label>
            Perfil
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as "tutor" | "clinic")}
            >
              <option value="tutor">Tutor</option>
              <option value="clinic">Clínica</option>
            </select>
          </label>
        </>
      )}
      <label>
        E-mail
        <input
          required
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
        />
      </label>
      <label>
        Senha
        <input
          required
          type="password"
          minLength={8}
          maxLength={200}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete={signup ? "new-password" : "current-password"}
        />
      </label>
      {signup && role === "tutor" && (
        <>
          <label className="check">
            <input
              type="checkbox"
              checked={addPet}
              onChange={(e) => setAddPet(e.target.checked)}
            />
            Cadastrar meu animal agora
          </label>
          {addPet && <PetFields value={pet} onChange={setPet} />}
        </>
      )}
      {signup && role === "clinic" && (
        <p className="notice">
          Após criar a conta, cadastre a unidade. O acesso a casos depende da
          verificação do responsável.
        </p>
      )}
      <button className="primary" disabled={busy}>
        {busy ? "Aguarde…" : signup ? "Criar minha conta" : "Entrar"}
        <Icon name="arrow" />
      </button>
      <button type="button" className="text-button" onClick={onBack}>
        Voltar aos acessos rápidos
      </button>
    </form>
  );
}
