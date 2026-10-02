# Pré-triagem conversacional v1

A implementação usa o RAG existente e os clientes reais Gemini/Ollama.
O acompanhamento se aplica somente a `workspace/conversations`. Não há
respostas clínicas simuladas em produção. A classificação continua sendo
`EMERGENCIA`, `NAO_EMERGENCIA` ou `INCERTO`; o controle de interação é separado.

## Estados e decisão

| Estado | Comportamento |
|---|---|
| `completed` | Classificação suficiente; exibe resultado, orientação e fontes. Não abre questionário. |
| `asking` | INCERTO; exibe uma pergunta objetiva selecionada a partir do relato e fichas recuperadas. |
| `form` | INCERTO; oferece opções para uma informação faltante, incluindo desconhecimento e complemento livre. |
| `insufficient` | INCERTO após esgotar acompanhamento; explica a limitação, oferece clínica e aceita novas observações. |

Toda nova resposta passa primeiro pelo classificador, inclusive depois de
`insufficient`. Um sinal grave novo pode concluir imediatamente como emergência.
O formulário recebe uma resposta; se ela ainda não permite classificar, o
acompanhamento termina. Novas mensagens continuam podendo mudar a classificação,
mas não reabrem uma sequência infinita de perguntas.

O backend valida a saída `FollowupPlan` com Pydantic. Ela contém o estado da
informação respondida, uma evidência literal, indicador de informação nova,
chave semântica estável, informação faltante, uma pergunta, opções e um código
curto de seleção. Não contém pensamento bruto. As perguntas são geradas pelo
provedor, com as fichas efetivamente retornadas pelo pipeline. A UI não interpreta
texto livre para escolher perguntas ou opções.

A distinção da informação é `reported`, `explicit_negative`, `unknown` e
`unanswered`. As respostas originais são preservadas, mesmo se a avaliação do
modelo for inconsistente. Uma informação só conta como progresso se o modelo a
marcar como nova/relevante, sua evidência literal existir na resposta e não for
uma resposta desconhecida. “Não sei”, “Não sei dizer” e “Não observei” não viram
negativas. Chaves já respondidas não geram outra pergunta.

O formulário é acionado por qualquer um destes motivos persistidos:

- `no_progress`: duas respostas consecutivas sem informação útil (configurável);
- `repeated_question`: a chave semântica ou pergunta normalizada já apareceu;
- `attempt_limit`: o teto de perguntas foi alcançado, mesmo havendo progresso.

A repetição pode antecipar o formulário antes da segunda resposta inútil.
Informação nova zera a sequência de falta de progresso. O número de mensagens
sozinho não diagnostica falta de progresso. O teto de tentativas é uma proteção
separada, não uma regra clínica. A equivalência semântica das chaves depende da
LLM; a normalização textual é uma proteção adicional, não uma prova semântica.

## Configuração e compatibilidade

```dotenv
FOLLOWUP_NO_PROGRESS_LIMIT=2
FOLLOWUP_MAX_QUESTIONS=4
WORKSPACE_NUM_CTX=32768
```

O workspace fixa `v1_grounded`, desliga CoT e usa a janela local acima. Os
prompts científicos, datasets, rótulos, fichas e coleção ativa não mudaram.
`PipelineOptions.num_ctx` é opcional; sem override, os runners continuam usando
`LLM_NUM_CTX`, como antes. A versão conversacional fica gravada no estado.

O dataset1 tem cinco colunas de sintomas e o rótulo `Dangerous` usados na
pesquisa. O dataset2 participa da preparação de dados e vocabulário. Nenhum
impõe quantidade mínima de sintomas ao tutor. Um sinal grave basta; vários
sinais vagos não obrigam decisão binária.

No Ollama, o adaptador verifica um limite conservador com bytes UTF-8 do
prompt/schema e reserva de saída. Históricos excessivos geram erro recuperável,
sem cortar fatos silenciosamente. Pode-se escolher Gemini ou procurar uma
clínica. A janela 32768 exige memória adequada ao modelo local.

## API, persistência e concorrência

`POST /workspace/conversations/{id}/messages` mantém os campos anteriores.
Um formulário acrescenta:

```json
{
  "request_id": "uuid-do-envio",
  "content": "Não observei — Estava fora de casa",
  "origin": "form",
  "question_id": "id-da-pergunta-ativa",
  "selected_option": "Não observei"
}
```

O servidor valida pergunta ativa e opção, associa texto à pergunta respondida,
persiste antes de iniciar o trabalho e reanalisa o conjunto dos relatos.
Perguntas não são fatos positivos; conclusões anteriores não entram como fatos.
Cada mensagem do assistente guarda seu estado e a conversa guarda o estado
atual. Conversas antigas sem campos novos funcionam sem migração.

`accepted_requests` torna reenvios antigos idempotentes. Uma falha pode ser
retentada com o mesmo ID ou pelo botão existente, sem duplicar a resposta.
Atualizações condicionais e `processing_id` impedem que um worker antigo
sobrescreva uma retentativa. A lease de vinte minutos continua permitindo
recuperar trabalho interrompido. Isso não é uma fila durável: após queda, o tutor
precisa retentar. O estado de processamento não significa que um worker ainda
esteja vivo.

A triagem estruturada é salva em `latest_triage` antes da etapa de pergunta.
Falha do provedor de acompanhamento deixa a resposta salva e o turno em
`failed`. A UI mantém o botão de retentativa. Não compartilha resultado antigo
com a clínica enquanto o turno mais recente estiver pendente ou falho.
Encaminhamentos preservam consentimento, snapshot e `INCERTO`; perguntas entram
no texto do histórico autorizado, com origem e associação da resposta.

## Operação e reprodução

Na raiz, execute as suítes separadamente: seus `conftest.py` legados colidem
quando coletados no mesmo processo.

```sh
DEBUG=false .venv/bin/pytest backend/tests
DEBUG=false .venv/bin/pytest scripts/tests
cd frontend-react
npm run build
# Em outro terminal: npx vite preview --host localhost --port 5173
APP_URL=http://localhost:5173 npx playwright test tests/followup.spec.ts
```

Use Node 22.12+ e Chromium instalado. `followup.spec.ts` é um teste de contrato
visual com fixtures HTTP. `workspace.spec.ts` usa API/Mongo reais e cria dados
acadêmicos. Para incluir o fluxo de encaminhamento real, forneça uma conversa
concluída do tutor acadêmico:

```sh
APP_URL=http://localhost:5173 LIVE_RAG_CONVERSATION_ID=ID npx playwright test
```

Com Docker/API reais ativos e acesso rápido acadêmico habilitado:

```sh
.venv/bin/python scripts/smoke_workspace_followup.py \
  --provider gemini --output /tmp/pre-triagem-live.json
```

Esse comando cria três conversas sintéticas, chama o provedor de verdade e salva
as respostas efetivamente recebidas, sem credenciais. Não é um benchmark de
acurácia nem promete reproduzir exatamente a redação/decisão de outra execução.
A etapa de acompanhamento adiciona uma chamada ao provedor nos turnos INCERTO,
com custo, latência e possibilidade de cota/indisponibilidade.

## Para a URL interna da equipe

É preciso escolher/configurar host e HTTPS, servir o build React novo e a API,
manter Mongo persistente e a coleção Chroma existente acessível, configurar
credenciais/cota do Gemini ou recursos do Ollama, e ajustar `VITE_API_URL` e
`FRONTEND_ORIGINS` para a URL final. A imagem frontend já em execução não se
atualiza apenas alterando arquivos locais: precisa de rebuild/redeploy.

Testar acesso remoto com contas separadas e confirmar recuperação de mensagens
na URL escolhida continua pendente. As contas rápidas acadêmicas são
compartilhadas; isolamento individual exige contas próprias. Nenhuma base deve
ser promovida para habilitar este fluxo. Veja a evidência da rodada para
resultados locais, limitações e conversas completas.
