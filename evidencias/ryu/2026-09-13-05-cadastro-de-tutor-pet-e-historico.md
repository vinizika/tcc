# Cadastro de tutor/pet e histórico de conversa

**Data:** 13/09/2026 · **Trilho:** B1 · **Rodada:** 5 · **Commit:** este

> Frente independente das outras duas ("prova nova" e o backlog de consulta):
> o TCC1 já previa "bancos relacionais e não relacionais para dados
> estruturados e históricos conversacionais" e "formulários estruturados"
> (seção K), e nada disso depende da base ou da prova de outro trilho — por
> isso entrou agora, em paralelo.

## O que foi feito

Persistência que não existia antes: até esta rodada, o histórico de
conversa vivia só em `st.session_state` do Streamlit (some ao fechar a
aba), e não havia conceito de tutor ou pet em lugar nenhum do backend.

| Peça | Onde | O que é |
|---|---|---|
| Tutores e pets | Supabase (Postgres) | Dado estruturado, relacional — `backend/supabase_schema.sql` |
| Histórico de conversa | MongoDB | Formato variável por turno; sobe local no compose |
| Integração com a triagem | `backend/app/prompts/triage.py`, `chat_pipeline.py`, `chat_service.py` | `pet_id` em `POST /chat/` injeta o cadastro do animal no prompt |
| Rotas novas | `app/api/tutors.py`, `pets.py`, `conversations.py` | CRUD de tutor/pet, leitura de conversa |

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **Sem autenticação real por enquanto** — `id` é a única credencial | Decisão do usuário: fase de desenvolvimento, autenticação de verdade fica para depois. Registrado como dívida no [B-56](../backlog.md#b-56), não escondido |
| 2 | **Supabase para tutor/pet, Mongo para histórico** | O primeiro é dado estruturado com relação clara (1 tutor → N pets); o segundo varia de formato por turno (texto/voz, com ou sem triagem) e cresce sem limite — não vale forçar schema relacional nele |
| 3 | **Degradação graciosa**: sem Supabase/Mongo configurados, `/chat/` continua funcionando | Nenhum dos dois projetos foi criado ainda. `pet_id` devolve 503 se pedido explicitamente sem Supabase; sem `tutor_id`/`pet_id`/`conversation_id`, nada do código novo roda — `/chat/` fica bit a bit igual a antes desta rodada |
| 4 | **`animal_context` nunca entra no `v0_legacy`** | Aquele prompt reproduz a medição de 04/05 ao pé da letra; mudar o que ele recebe invalidaria a comparabilidade histórica |
| 5 | **Falha de Mongo é engolida; falha de pet lookup não é** | Histórico é acessório à triagem — perder um turno não pode derrubar a resposta. Um `pet_id` que o tutor mandou e não existe é erro do cliente, e merece 404 explícito, não um silêncio que esconderia o cadastro faltando |
| 6 | **RLS ligado no Supabase, mas com política aberta** (`using (true)`) | É o padrão seguro por default do Supabase (ligar é a parte fácil); apertar a política exige login, que não existe ainda. Registrado como dívida explícita, não como esquecimento |
| 7 | **Campos do pet só os que mudam decisão clínica**, cruzados com o mapa de assuntos do B2 | Espécie, idade, sexo/castração e vacinação aparecem em discriminadores reais (`data/curadoria/mapa-de-assuntos.csv`) — obstrução uretral por espécie, piometra por sexo, convulsão por vacinação. Não é ficha de cadastro por completude |
| 8 | **MongoDB sobe local no compose**; Supabase fica externo | Mongo não tem custo de operar localmente. Supabase é o ponto — Postgres gerenciado com auth pronto para quando for hora de apertar o B-56 |

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/core/config.py` | `SUPABASE_URL`, `SUPABASE_KEY`, `MONGODB_URI`, `MONGODB_DB_NAME` |
| `backend/app/clients/supabase_client.py`, `mongo_client.py` | **novos** — clientes lazy, erro claro sem configuração |
| `backend/app/exceptions/persistence_exception.py`, `tutor_exception.py`, `pet_exception.py`, `conversation_exception.py` | **novos** |
| `backend/app/schemas/tutor.py`, `pet.py`, `conversation.py` | **novos** — `PetResponse.to_triage_context()` é a peça central |
| `backend/app/services/tutor_service.py`, `pet_service.py`, `conversation_service.py` | **novos** |
| `backend/app/api/tutors.py`, `pets.py`, `conversations.py` | **novos**, registrados em `main.py` |
| `backend/app/schemas/chat.py`, `services/chat_service.py`, `pipeline/chat_pipeline.py`, `prompts/triage.py` | `tutor_id`/`pet_id`/`conversation_id` opcionais em `ChatRequest`; `animal_context` atravessa o pipeline até o prompt; `conversation_id` na resposta |
| `backend/requirements.txt` | `supabase==2.15.0`, `pymongo==4.15.3` |
| `docker-compose.yml` | serviço `mongo` local; `MONGODB_URI` injetado no backend |
| `backend/supabase_schema.sql` | **novo** — DDL de `tutors`/`pets`, com RLS aberta e aviso |
| `.env.example`, `README.md`, `docs/CONTRATOS.md` | documentação de setup e das rotas novas |
| `evidencias/backlog.md` | [B-56](../backlog.md#b-56) registrado |
| testes | backend 134 → **181** (47 novos: schema do pet, serviços com dublês de Supabase/Mongo em `conftest.py`, rotas, e a integração com `/chat/`) |

## Verificação

`docker run ... tcc-backend:latest sh -c "pip install supabase pymongo && pytest -q"`
→ **181 passaram**. Ainda não testado contra Supabase/Mongo reais — nenhum
projeto foi criado. `docker compose config` valida a sintaxe do compose com
o serviço `mongo` novo.

## Observações

**1. Nenhum teste depende de rede.** Os dublês de Supabase (`conftest.py`,
`SupabaseClientFalso`) e Mongo (`MongoDatabaseFalso`) guardam tudo em
memória e imitam só o que os serviços usam — mesmo padrão dos dublês de
`RetrievalClient`/`LLMClient` já existentes.

**2. O ponto de integração é pequeno de propósito.** `animal_context` é uma
string opcional passada por três funções (`execute` → `_classify` →
`build_triage_messages`); não existe acoplamento novo entre o pipeline e o
Supabase — quem resolve `pet_id` em `animal_context` é o `ChatService`, uma
camada acima.

**3. Ainda não testado com API real.** Sem Supabase/Mongo criados, tudo
aqui é validado por dublê. O primeiro teste de fogo é criar os projetos e
rodar o exemplo do README ponta a ponta.

## Deixado para depois

**Autenticação de tutor** ([B-56](../backlog.md#b-56)) — Supabase Auth já
vem pronto no projeto, só falta ligar.

**O formulário do pet no frontend.** Esta rodada fez a API; a tela do
Streamlit para o tutor preencher o cadastro é a próxima peça óbvia.

**Testar contra Supabase/Mongo reais** assim que os projetos existirem —
criar o schema, rodar o exemplo do README, e conferir que `pet_id` de fato
muda a resposta do modelo (hoje só testado com o `LLMClientFalso`).

## Próximo passo

Criar os projetos (Supabase e, se quiser, um Atlas para produção — o Mongo
local do compose já resolve para desenvolvimento), rodar
`backend/supabase_schema.sql`, e testar o fluxo completo do README. Depois:
o formulário do pet no frontend.

---

## Adendo de 15–16/09 — teste contra o Supabase real

O projeto foi criado em 15/09 e o schema, rodado pelo próprio usuário no SQL
Editor. Dois problemas apareceram ao testar de ponta a ponta, nenhum deles
prova de que o código estava errado — os dois eram do ambiente.

**1. `supabase==2.15.0` não reconhece o formato novo de chave.** O projeto
criado já usa `sb_secret_...`/`sb_publishable_...` em vez do JWT antigo
(`eyJ...`); a versão fixada rejeitava com `SupabaseException("Invalid API
key")`. Corrigido para `2.31.0` — os 201 testes do backend continuam
passando (dublês não tocam a biblioteca de verdade).

**2. Disco do host quase cheio (2,1 GB livres de 223 GB) travou o
container.** Coincidiu com o merge do PR do Vinicius
(`codex/harden-vector-ingestion`), que fixou versões de várias dependências
— qualquer recriação de container agora baixa o modelo de embeddings do
zero (ele mora no cache da camada do container, não no bind mount), e com o
disco cheio a escrita simplesmente trava sem erro explícito. Resolvido
limpando o disco (o usuário liberou espaço no C:, e `docker builder prune`
tirou mais 15,6 GB de cache de build). Fica registrado porque é o mesmo
modo de falha que já tinha corrompido o Docker Desktop do Vinicius em
07/09 — vale todo mundo ficar de olho no disco antes de recriar containers.

**Teste de ponta a ponta, com os dois corrigidos:** tutor e pet criados no
Supabase real; `POST /chat/` com `pet_id` classificou corretamente
("vomitou uma vez, comendo normal" → `NAO_EMERGENCIA`) e devolveu
`conversation_id`; `GET /conversations/{id}` trouxe o turno completo,
incluindo a triagem embutida. A cadeia inteira (Supabase → prompt → Mongo)
funciona com infraestrutura real, não só dublês.

**O que ficou para depois:** o registro de teste ("Teste Ryu" / "Bidu")
continua no Supabase — não há rota de exclusão ainda (`POST`/`GET`/`PATCH`
existem, `DELETE` não foi implementado). E a chave usada é a `secret`
(equivalente a service role, ignora RLS por completo) — funciona porque a
política hoje é aberta mesmo, mas quando o B-56 for resolvido (autenticação
real), o app deve passar a usar a `publishable`/`anon` key, reservando a
`secret` para tarefas administrativas.
