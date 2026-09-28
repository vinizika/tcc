# Segunda etapa: encaminhamento entre tutor e clínica

> Atualização: o workspace persistente, o provedor local de identidade, voz no
> React e a configuração independente do Google estão no guia
> [POC utilizável](poc-utilizavel.md). Em caso de diferença, use o guia novo.

## Arquitetura escolhida

O frontend principal é React + TypeScript (`frontend-react/`). O Streamlit
permanece disponível no perfil `legacy` enquanto voz e cadastros antigos são
migrados. React foi escolhido porque esta etapa reúne mapa interativo, estado
recuperável, áreas distintas, formulários de revisão, dashboard e polling; no
Streamlit essas interações dependiam de estado de sessão e o protótipo em
`mock/` não chamava o backend real.

FastAPI continua sendo a fronteira de regras e dados. A interface consome
`triage`, nunca interpreta o texto de `answer`, e cria um snapshot
`triage_snapshot.v1` no encaminhamento. Assim, trocar RAG, prompt ou modelo não
reescreve um caso já compartilhado.

| Responsabilidade | Tecnologia | Observação |
|---|---|---|
| identidade e perfis reais | Supabase Auth/Postgres | RLS por `auth.uid()`; clínica nasce pendente |
| encaminhamentos, eventos e mensagens | MongoDB já presente | documento agregado, histórico e polling |
| pré-triagem | pipeline FastAPI existente | permanece isolado dos módulos novos |
| descoberta pública | Google Places sob demanda | resposta não vira catálogo persistente |
| demonstração | identidades e clínicas fictícias | ativada somente por `WORKFLOW_MODE=demo` |

## Modos de execução

### Demonstração local, sem cobrança

```bash
cp .env.example .env
# mantenha WORKFLOW_MODE=demo e as chaves Google vazias
docker compose up -d
```

Abra <http://localhost:3000>. As contas, clínicas, notas, horários, telefones,
localizações e distâncias trazem a palavra “demo” ou “fictício”. Nenhuma ação
contata uma unidade externa. O MongoDB mantém caso e chat após recarregar a
página e enquanto o volume existir.

O Streamlit anterior continua disponível, sem virar o frontend principal:

```bash
docker compose --profile legacy up -d frontend-legacy
```

Ele abre em <http://localhost:8501>.

### Modo real

1. Configure um projeto Supabase e execute `backend/supabase_schema.sql`.
2. Use uma chave de servidor no backend; não coloque `sb_secret_*` no bundle.
3. Defina `WORKFLOW_MODE=real`, `SUPABASE_URL` e `SUPABASE_KEY`.
4. Ative Maps JavaScript API, Places API (New) e Geocoding API no Google Cloud.
5. Crie duas chaves: web restrita por domínio/API e servidor restrita por
   IP/API. Preencha `GOOGLE_MAPS_WEB_KEY`, `GOOGLE_MAPS_SERVER_KEY` e um Map ID.
6. Reconstrua o frontend, pois a chave web é argumento de build.

O modo real falha com mensagem explícita quando Google ou Supabase não estão
configurados. Ele nunca exibe as clínicas fictícias como fallback.

## Google Maps: campos, custos e limites

A busca usa Nearby Search (New), raio máximo de 50 km e `FieldMask` explícita.
São pedidos somente: id, nome, endereço, coordenadas, telefone, horários,
estado de abertura, nota, quantidade de avaliações e URI do Maps. O Google
cobra a requisição conforme o campo de SKU mais alto presente; por isso ampliar
a máscara muda custo e precisa de revisão. Preço, franquia mensal e cotas são
configuração externa e devem ser conferidos antes do deploy na
[tabela oficial de preços](https://developers.google.com/maps/billing-and-pricing/pricing)
e na [documentação de uso e cobrança do Places](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing).

Defina alertas de orçamento e uma cota por minuto no projeto. Não use `*` na
máscara em produção. A aplicação não persiste nome, nota, horário ou telefone
de resultados públicos; somente o `place_id` pode vincular, após verificação
manual, uma unidade participante. Isso reduz dados desatualizados e respeita
as restrições de armazenamento/exibição. Resultados Google são exibidos com
mapa Google e atribuição; o modo demo não usa tiles do Google.

Distância é calculada em linha reta e rotulada assim. A aplicação não chama
Routes API nem promete tempo de trajeto. Rota abre no Google Maps; caso uma
estimativa interna seja desejada depois, a equipe deve habilitar e orçar Routes
separadamente.

## Identidade, dados antigos e verificação de clínicas

IDs de tutor antigos não autenticam ninguém. A migração adiciona `user_id`
anulável a `tutors`; registros anteriores ficam preservados, mas inacessíveis
por RLS até associação manual após verificação de identidade. Nunca se associa
conta antiga somente por nome ou e-mail semelhante.

As rotas anteriores de tutor, pet e conversa continuam sem sessão apenas em
`WORKFLOW_MODE=demo`, para preservar o runner e a demonstração. Em `real`, elas
exigem Bearer de tutor e consultam o recurso junto com `user_id`; um ID conhecido
não concede acesso. A pré-triagem continua pública quando não recebe IDs
pessoais. Se `tutor_id`, `pet_id` ou `conversation_id` for enviado, a sessão e
a titularidade passam a ser obrigatórias.

No cadastro de clínica, CNPJ/documento, responsável, endereço e eventual
`google_place_id` criam uma unidade `pending_manual_verification`. Selecionar
um resultado do Maps não concede posse. O procedimento administrativo é:

1. conferir documento da empresa e identidade/autorização do responsável;
2. confirmar o telefone/endereço por canal independente;
3. confrontar o `place_id` sem tratá-lo como prova de titularidade;
4. atualizar no Mongo `verified=true`, `enabled=true` e status; atualizar no
   Supabase `profiles.clinic_id` e `clinic_verified=true` com chave de serviço;
5. registrar operador, data e evidências fora do repositório público.

Até os passos terminarem, a conta não abre dashboard nem lê casos. O schema
modela um perfil por usuário e `clinic_id`, permitindo vários responsáveis na
mesma unidade futuramente sem mudar os encaminhamentos.

## Estados do encaminhamento

```text
delivered → viewed → acknowledged → accepted → on_the_way → arrived → completed
                  └──────────────→ refused
delivered/viewed/acknowledged/accepted/on_the_way → cancelled
```

`submitted` é um evento: o sistema gravou após consentimento. `delivered`
significa que ficou disponível no painel. `viewed`, `acknowledged`, `accepted`,
`on_the_way` e `arrived` exigem ações distintas. Nenhum desses estados equivale
a vaga garantida. Toda transição guarda ator e horário, e transições fora da
máquina recebem HTTP 409.

Indicadores do dashboard:

- **A caminho confirmados:** status `on_the_way`, após ação do tutor;
- **Aguardando análise:** `delivered`, `viewed` ou `acknowledged`;
- **Chegadas em 24 h:** evento `arrived` nas últimas 24 horas;
- **Total recebido:** todo encaminhamento destinado à unidade.

Dashboard e chat usam polling de 8 segundos (`WORKFLOW_POLL_INTERVAL_S`). Isso
funciona após recarga, mas não é push e pode atrasar a visualização até um
intervalo; WebSocket/notificações ficam como evolução.

## Decisões de IHC aproveitadas

- início sem cadastro, uma ação principal e relato preservado: P01/H08;
- linguagem cotidiana, resultado com limite e próximo passo: P01, P02/H02,
  H06 e H11;
- mapa sincronizado com lista, telefone e rota, sem inferir capacidade: H10;
- resumo revisável com origem “tutor” e “automático”: R05/H03;
- consentimento explícito e confirmação por eventos: P03/H05;
- alvos amplos, responsividade e informação além de cor: P01/P02.

H03, H05 e H08–H11 continuam hipóteses do estudo de IHC, não resultados de
pesquisa. A interface materializa decisões para avaliação posterior; não as
apresenta como necessidades já validadas.

## Limites reais

- o modo real depende de credenciais, cobrança/cotas do Google e Supabase;
- verificação institucional é manual;
- disponibilidade/capacidade clínica não vem de avaliação ou horário Google;
- não há notificação push, SLA de resposta nem escalonamento automático;
- a entrada de voz continua no Streamlit legado até a migração React;
- a triagem continua sujeita às limitações clínicas e de recuperação já
  registradas nas evidências do projeto.
