# Rodada — pré-triagem conversacional para INCERTO

Base efetiva inspecionada: branch `codex/integrate-joao-react`, commit `6737665`
(working tree inicialmente limpo). Ela já contém `origin/main` local em
`e365f3e`, mais os commits de preservação/integração do React. A referência
`main` local ainda estava em `f2b8311`. Mantive a base integrada presente para
preservar React e tutor/clínica, em vez de voltar à referência local antiga.
Não houve fetch nesta rodada; a posição remota foi identificada pela referência
local disponível.
Implementação local em 28/09/2026. Não foi feito commit, push ou implantação em
uma URL remota. A API Docker local usa o código por volume/reload; o frontend
novo foi validado via preview do build, sem substituir o container frontend.

## Entrega

- Orquestração `conversational_v1` independente dos runners científicos.
- Schema validado de pergunta/opções/evidência; cliente Gemini/Ollama real.
- Estados persistidos `asking`, `form`, `completed`, `insufficient`.
- Distinção entre fato, negativa explícita, desconhecimento e não perguntado.
- Regra configurável de falta de progresso, prevenção de repetição e limite.
- Formulário integrado ao chat, complemento opcional e confirmação no histórico.
- Idempotência histórica, retentativa sem mensagem duplicada e identificação
  de cada processamento para rejeitar resultados de workers antigos.
- Histórico completo de relatos associado às perguntas, sem usar conclusões
  anteriores como fatos. Proteção de contexto para o Ollama.
- Encaminhamento da última resposta concluída; bloqueio durante falha/pendência.
- Documentação operacional em `docs/pre-triagem-conversacional.md`.

A coleção permaneceu `veterinary_documents__20260925T061349534255Z__280baf13`.
Nenhuma ficha, dataset, prova, rótulo, ponteiro ou base documental foi alterado.
O classificador científico mantém seus defaults; foi acrescentado apenas o
parâmetro opcional `num_ctx`, usado explicitamente pelo workspace.

## Resultados executados

| Verificação | Resultado |
|---|---|
| Backend, pytest (Mongo/LLM externos isolados pelos testes) | 330 testes passaram |
| Scripts, pytest | 217 testes passaram |
| TypeScript + build Vite | Passou |
| Playwright — novo formulário com fixtures HTTP | 2 passaram |
| Playwright — aplicação/API/Mongo reais, inclusive clínica | 5 passaram |
| Smoke API/RAG/Mongo/Gemini reais | 3 conversas concluídas; JSON ao lado desta evidência |
| `git diff --check` | Passou |

Comandos na raiz (executar suítes separadamente):

```sh
DEBUG=false .venv/bin/pytest backend/tests
DEBUG=false .venv/bin/pytest scripts/tests
cd frontend-react
npm run build
# Outro terminal: npx vite preview --host localhost --port 5173 --strictPort
APP_URL=http://localhost:5173 \
LIVE_RAG_CONVERSATION_ID=c1b10f5a-80d9-48d8-9691-43525ac8ee99 \
npx playwright test
```

O ID acima pertence ao smoke desta máquina; em outra instalação, use o ID de
uma nova conversa real do tutor acadêmico. Para repetir o smoke:

```sh
.venv/bin/python scripts/smoke_workspace_followup.py \
  --provider gemini --output /tmp/pre-triagem-live.json
```

O Node padrão era 18.18.2. O build funcionou com aviso, mas Playwright recusou
Node 18. Foi usado Node 22.23.3 já instalado em
`~/.npm/_npx/52027bd8fc0022aa/node_modules/node/bin/node` para o navegador. A verificação final TypeScript/Vite também passou com Node 22.23.3.
Chromium e os servidores locais precisaram executar fora do sandbox.

Tentativas iniciais registradas: `DEBUG=release` herdado do ambiente impediu a
coleta; o comando explicitamente usa `DEBUG=false`. Coletar backend e scripts
juntos causou colisão de seus módulos `conftest`; separadamente passaram. O
preview em `127.0.0.1:3000` não estava na lista CORS da API, então os testes reais
falharam nessa origem. A repetição em `localhost:5173`, origem já permitida,
passou nos sete testes. Nenhum relaxamento de CORS foi necessário.

## Conversas reais completas

As transcrições abaixo foram recebidas do Gemini `gemini-3.5-flash-lite`, sem
fallback. São relatos sintéticos de teste, não atendimento a animais reais.
Classificação, fontes, tempos, configuração, perguntas/opções e estados estão em
[2026-09-28-pre-triagem-live.json](2026-09-28-pre-triagem-live.json).

### 1. Emergência imediata

**Tutor**:

> Meu gato está respirando com a boca aberta e faz muita força para respirar mesmo parado.

**Assistente**:

> O gato apresenta dificuldade respiratoria grave com esforco e boca aberta, indicando risco imediato.
> Procure um veterinário agora, sem esperar.

Classificação: `EMERGENCIA`; estado: `completed`.


### 2. Incerteza resolvida por pergunta

**Tutor**:

> Meu gato está estranho, entra na caixa de areia muitas vezes. Não vi o que acontece lá.

**Assistente**:

> O relato não traz informação suficiente para decidir sobre a urgência.
> Procure atendimento veterinário na dúvida.
> Quando ele entra na caixa de areia, você percebe se ele consegue urinar ou se sai apenas algumas gotas ou nada?

Classificação: `INCERTO`; estado: `asking`.

**Tutor**:

> Ele tenta fazer xixi várias vezes e não sai nenhuma gota de urina.

**Assistente**:

> A incapacidade de urinar indica obstrução urinária, que é uma urgência veterinária grave.
> Procure atendimento veterinário imediatamente sem esperar.

Classificação: `EMERGENCIA`; estado: `completed`.


### 3. Incerteza com formulário e encerramento

**Tutor**:

> Meu gato está diferente hoje. Não consigo explicar o que mudou.

**Assistente**:

> O relato não traz informações suficientes sobre os sintomas do animal para permitir uma decisão segura.
> Procure atendimento veterinário na dúvida.
> O seu gato comeu a racao normalmente hoje?

Classificação: `INCERTO`; estado: `asking`.

**Tutor**:

> Não sei dizer

**Assistente**:

> O relato não traz informações suficientes sobre os sintomas do animal para definir a gravidade do caso.
> Na dúvida, procure atendimento veterinário para uma avaliação completa do seu pet.
> O seu gato comeu alguma quantidade de comida hoje?

Classificação: `INCERTO`; estado: `form`.

Opções: Sim, comeu normalmente; Comeu menos do que o habitual; Recusou completamente a comida; Não observei; Não sei dizer.

**Tutor** (formulário):

> Não observei

**Assistente**:

> O relato não traz informações suficientes sobre os sintomas do animal para decidir a gravidade.
> Procure atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

Classificação: `INCERTO`; estado: `insufficient`.

## Limites e pendências

Os testes determinísticos verificam a orquestração e falhas com dublês; não
medem acurácia clínica. Os três exemplos reais são smoke tests, não validação
clínica nem substituição da avaliação científica. A formulação do modelo ainda
pode ser excessivamente conclusiva (por exemplo, mencionar obstrução urinária
na justificativa); requer revisão da equipe antes de uso além da POC.

A terceira conversa acionou formulário após uma resposta desconhecida porque
o modelo propôs a mesma chave semântica; o motivo persistido foi
`repeated_question`. O caso de duas respostas consecutivas sem progresso está
coberto no teste determinístico. Desconhecimento permaneceu INCERTO.

Não executado: conversa completa com Ollama real nesta rodada, falha real de
quota Gemini, interrupção real do processo em plena análise, restauração de
backup Mongo e teste em URL remota. Falhas, lease e worker antigo foram
verificados em testes determinísticos. Não houve novas avaliações científicas
nem alteração da coleção para facilitar resultados.

Para testar em URL interna ainda faltam host/domínio/HTTPS definidos pela
equipe, build/deploy do frontend novo junto da API, configuração de origem/API,
segredos e persistência no host escolhido, e um smoke remoto com contas próprias.
Os serviços locais já permitiram testar o fluxo completo. As contas rápidas
continuam compartilhadas; contas próprias oferecem isolamento entre pessoas.

Não há fila externa durável: uma interrupção exige retentativa após a lease.
A seleção semântica depende do modelo, com validação estrutural/evidência e
limites determinísticos no backend. O acompanhamento faz uma chamada adicional
por INCERTO e depende da disponibilidade/cota do provedor. Dados de teste
criados no Mongo acadêmico foram mantidos para reprodução.
