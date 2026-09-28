# POC utilizável: conversa, identidade e localização real

## O que será feito

Evoluir a segunda etapa para chat persistente por animal, contas próprias e
acessos acadêmicos controlados no servidor, descoberta Google real, revisão de
consentimento por tipo de dado e deslocamento opcional. Criar e aplicar um
brand book apoiado na análise de referências e no repositório IHC (somente leitura).

## Por quê

A interface anterior ainda era um formulário de triagem, não uma conversa;
o modo demo também forçava clínicas fictícias. Faltavam histórico navegável,
animais persistidos nas contas de avaliação e consentimento para conversa completa.

## Decisões previstas

- Separar provedor de identidade, acesso acadêmico e provedor de mapas.
- Reaproveitar pipeline e taxonomia sem mudar prompts científicos.
- Executar triagem como tarefa persistida consultável, evitando HTTP de longa duração.
- Mongo para contas locais da POC, seus animais e conversas; Supabase continua
  disponível como provedor de identidade e preserva os registros legados.
- Google Places New sem avaliações/fotos; Geocoding v4 e Routes quando disponíveis.
- Clínica acadêmica explicitamente separada das unidades reais do Google.

## Resultado esperado

Login → chat → pet opcional → resultado real → busca Google → consentimento →
painel → mensagens e estados sobrevivem à recarga. Acesso entre titulares é
recusado; localização e conversa completa só aparecem após autorização específica.

## Resultado obtido

Concluído em 25/09 UTC (24/09 à noite em São Paulo). Aplicação local na porta
3000; sem publicação externa ou aprovação de clínica real.

### Implementação

- Três ações de entrada, contas próprias, sessões opacas/revogáveis, scrypt.
- Animais opcionais, edição, histórico privado e chat persistente com resposta
  202; geração não depende mais de uma requisição HTTP longa.
- Brand book aplicado: VetAI, DM Sans/Manrope locais com licenças, superfícies
  claras, transições curtas, foco visível e movimento reduzido.
- Google real por Places New/Maps JS, texto/CEP/referência e localização.
  Clínicas acadêmicas separadas; erro Google nunca vira fixture silenciosamente.
- Resumo revisado, opt-in de conversa completa e localização; conteúdo automático
  obtido do servidor, não confiado ao navegador. Posição desatualizada é ocultada
  e removida nas leituras do repositório.
- Dashboard paginado, indicadores, estados, conversa autorizada, chat humano e
  proteção contra perda de atualizações concorrentes.
- Cadastro institucional pendente e comando de verificação manual auditável.
- [Brand book](../../docs/brand-book.md) e [operação](../../docs/poc-utilizavel.md).
  IHC consultado somente para leitura; nenhuma validação com participantes presumida.

### Verificações concluídas

| Verificação | Resultado |
| --- | --- |
| Backend completo, `docker compose exec -T backend python -m pytest` | **254 passaram**, 62 avisos de depreciação, 4,49 s |
| TypeScript/Vite no Node 22 Docker | Build aprovado; JS ~244 kB / 76 kB gzip |
| Playwright/Chromium com backend local real | **5 passaram**, 57,9 s |
| `compileall -q app` | Passou |
| `pip check` | Nenhuma dependência quebrada |
| `git diff --check` | Sem erros |
| Credencial | Somente no `.env` ignorado; sem cópia para fontes/docs/evidências |

Os testes de navegador não interceptaram API nem inventaram saídas do modelo:

1. Login acadêmico, rascunho após recarga, cadastro/edição de pet e associação.
2. Conta própria com pet opcional no cadastro e login posterior.
3. Viewport de 390 px sem overflow, busca Google e mapa real.
4. RAG previamente concluído → consentimento → unidade acadêmica → aceite →
   deslocamento → geolocalização emulada autorizada/revogada → mensagens nos dois
   sentidos → chegada → conclusão.
5. Clínica própria fictícia cadastrada, permanecendo pendente após recarga.

Screenshots locais em `frontend-react/test-results/`, ignorados pelo Git.
Os testes criaram registros “Teste UI” e contas `@example.org`, sem dados pessoais.

### RAG real: duas execuções, não benchmark clínico

Coleção: `veterinary_documents__20260920T160842289762Z__388f518d`, em
`/app/chroma_db`; integridade verificada pelo adaptador isolado. Nenhum ponteiro
foi ativado. Corpus continua experimental e corte 0,72 foi mantido.

| Relato fictício | Estado final | Trechos usados | Fontes citadas | Pipeline |
| --- | --- | ---: | ---: | ---: |
| Gato tentando urinar, gotas e vômito | idle / EMERGENCIA | 0 | 0 | 197,237 s |
| Caso b01 existente: cão/chocolate/tremor/vômito | idle / EMERGENCIA | 2 | 1 | 200,804 s |

Parede, incluindo inicialização/polling: aproximadamente 222 s e 227 s. Sem 504.
A primeira informa ausência de referência elegível. A segunda cita “Chocolate
Toxicity in Dogs and Cats”; também incluiu trecho de diarreia não citado.
Pipeline operacional não implica relevância perfeita ou segurança clínica.

IDs locais:
`6408f3b0-1830-44c0-a4d2-a8e071dce346` e
`7cec3b32-0385-487e-b27a-1e58a3505d3f`.

### Google real

Text Search resolveu “Avenida Paulista, São Paulo”; Nearby retornou 20 locais.
Maps JS foi confirmado no Chromium. Routes entre dois pontos públicos retornou
2.339 m / 520 s, DRIVE sem trânsito ao vivo; não se trata de ETA de paciente.
Unidade acadêmica mantém ETA indisponível por definição.

### Limites e correções durante a validação

- Primeira regressão: 15 falhas porque testes legados herdavam modo/provedor do
  `.env` real. Configuração dos testes foi isolada, com testes novos explicitamente
  exercitando autorização no modo POC.
- Primeiro navegador: seletor de espécie incorreto e logout mantendo formulário
  próprio em vez dos três acessos. Corrigidos; edição de animal passou a enviar
  somente campos permitidos, sem metadados internos.
- Node 18 local incompatível: build em Node 22 Docker e navegador com Node 22
  temporário. Requisito agora explícito no package.json.
- Demo Key possui cotas e não serve como credencial de produção; não foram
  pedidos avaliações/fotos. Chave de servidor não é argumento do build.
- CPU ainda lenta. BackgroundTasks não é fila durável; texto persiste, mas
  geração interrompida exige tentativa após expiração da tarefa em 20 min.
- Supabase continua alternativa, não testada aqui com credenciais reais.
- Voz ligada ao endpoint existente com revisão de transcrição, sem teste de
  microfone/transcrição real nesta rodada.
- Publicação requer infraestrutura/TLS, identidade endurecida, retenção/backups,
  avaliação clínica e teste IHC com pessoas. Não foi feita automaticamente.
