# Remove o cadastro antigo de tutor e pet no Supabase

**Data:** 06/10/2026 · **Trilho:** B1 · **Rodada:** 25 · **Commit:** este

## O que foi feito

Saíram as rotas `/tutors` e `/pets`, que gravavam tutor e pet no Supabase
(construídas na [rodada 5 do Ryu](2026-09-13-05-cadastro-de-tutor-pet-e-historico.md)),
e tudo o que só existia para elas:

- **Backend:** as rotas, os serviços, os schemas e as exceções de tutor e pet;
  os campos `tutor_id` e `pet_id` do `POST /chat/` (quem ainda os mandar recebe a
  triagem normalmente, e os campos são ignorados); o dublê de Supabase dos
  testes, que só elas usavam.
- **Tela antiga (Streamlit, `--profile legacy`):** o formulário de cadastro de
  tutor e pet da barra lateral.
- **Esquema do Supabase** (`supabase_schema.sql`): deixa de criar as tabelas
  `tutors` e `pets`. Não as apaga: num projeto que já as tenha, apagar é decisão
  de quem administra.
- **Documentação:** README, `docs/CONTRATOS.md`, `docs/poc-utilizavel.md`,
  `docs/segunda-etapa.md`, `.env.example` e o comentário das settings.

**O que fica:**

- o **Supabase como login do modo real** (`profiles`, `AUTH_PROVIDER=supabase`),
  do Vinicius — intocado;
- o **histórico de conversa da API antiga** (`/conversations`, MongoDB). Ele
  começava quando o `/chat/` recebia `tutor_id` ou `pet_id`; agora começa com
  um campo explícito, `save_history`, que a tela antiga passou a enviar. Sem
  dono desde a remoção, fora do modo `demo` a conversa antiga fica
  inacessível — que era o comportamento de antes para conversas sem tutor.

## Por quê

Melhoria 4 da lista aprovada pelo Ryu em 06/10. A análise de 06/10 mostrou dois
cadastros de pet no código: o antigo, no Supabase, que o app novo não usa, e o
do app (workspace), no MongoDB, que o tutor de fato preenche. Eles não
conversavam: um pet salvo num não aparecia no outro. O Ryu decidiu "seguir com o
que o Vinicius montou". O cadastro antigo era do trilho B1, então a remoção
também.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Manter o histórico antigo, trocando o gatilho por `save_history` | A tela antiga ainda existe como opção (`--profile legacy`) e perderia a continuidade da conversa |
| 2 | `tutor_id`/`pet_id` ignorados, não recusados | Um cliente antigo continua recebendo a triagem; não há motivo para quebrá-lo com erro 422 |
| 3 | O esquema do Supabase não apaga as tabelas antigas | Apagar dados num banco de outra pessoa não cabe num script de criação |
| 4 | O [B-56](../backlog.md#b-56) (cadastro sem autenticação) fecha como obsoleto | O cadastro que ele descrevia não existe mais |

## Resultado esperado

_Escrito antes de testar._ O app novo não muda nada (ele nunca chamou essas
rotas); a suíte do backend passa sem os testes do cadastro antigo; `/tutors`
passa a responder 404; a tela antiga ainda compila.

## Resultado obtido

**Como esperado.** Backend: **313 testes passando** (eram 346; saíram 33: os
dos cinco arquivos de teste do cadastro antigo, o do histórico que guardava
`tutor_id` e os do `/chat/` que usavam `pet_id`, num arquivo reescrito para
`save_history`). Scripts: 204
passando, iguais. Ao vivo, `GET /tutors/x` responde **404**. A tela antiga
(`frontend/`) compila (`py_compile` nos três arquivos mexidos). O app novo
(`frontend-react`) não chamava nenhuma das rotas removidas — conferido no
`api.ts`.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/api/{tutors,pets}.py`, `services/{tutor,pet}_service.py`, `schemas/{tutor,pet}.py`, `exceptions/{tutor,pet}_exception.py` | **removidos** |
| `backend/tests/test_api_{tutors,pets}.py`, `test_{tutor,pet}_service.py`, `test_pet_schema.py` | **removidos** |
| `backend/app/main.py` | sem as duas rotas |
| `backend/app/schemas/chat.py`, `api/chat.py`, `services/chat_service.py` | `save_history` no lugar de `tutor_id`/`pet_id` |
| `backend/app/services/conversation_service.py`, `schemas/conversation.py` | histórico sem `tutor_id`/`pet_id` |
| `backend/tests/conftest.py` | sem o dublê de Supabase |
| `backend/tests/test_api_chat_persistence.py`, `test_api_conversations.py`, `test_conversation_service.py`, `test_workflow_api.py`, `test_workspace.py` | ajustados |
| `frontend/app/components/pet_form.py` | **removido** |
| `frontend/app/components/{chat,sidebar}.py`, `frontend/services/api.py` | sem o cadastro; histórico por `save_history` |
| `backend/supabase_schema.sql` | só os perfis do modo real |
| `README.md`, `docs/CONTRATOS.md`, `docs/poc-utilizavel.md`, `docs/segunda-etapa.md`, `.env.example`, `backend/app/core/config.py` | a documentação acompanha |

## Observações

**Mexe em arquivos do Vinicius** (a tela antiga e três documentos dele). As
mudanças só tiram o que dependia do cadastro antigo; vale avisá-lo antes do PR.

## Próximo passo

Avisar o Vinicius. Em 07/10, medir a melhoria 2 (rodada 23) com a cota nova do
Gemini.
