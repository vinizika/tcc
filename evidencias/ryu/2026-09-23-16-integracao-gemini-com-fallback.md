# Gemini em produção, com fallback para Ollama, e HyDE de volta

**Data:** 23/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 16 · **Commit:** este

## O que foi feito

Depois das rodadas 14-15 mostrarem, em 25 casos, que o Ollama comete erros
factuais claros na reescrita, no Multi-Query e no HyDE (5 casos) e o
Gemini não repetiu nenhum, decidi (dono do trilho B1) integrar o Gemini na
etapa de consulta de produção, com Ollama como plano B automático:

1. [`HybridQueryClient`](../../backend/app/clients/hybrid_query_client.py) —
   tenta o Gemini primeiro; se falhar (sem chave, limite atingido, erro de
   rede), cai para o Ollama na reescrita e no Multi-Query. **No HyDE, não
   cai para o Ollama** — se o Gemini falhar, a consulta segue sem
   documento hipotético, porque o HyDE do Ollama já tinha sido desligado
   por um motivo (B-09) que continua valendo se ele voltar pela porta dos
   fundos do fallback.
2. `ChatPipeline` passou a usar `HybridQueryClient` por padrão em vez do
   `QueryClient` puro.
3. `HYDE_ENABLED` voltou a `True` por padrão — agora ele roda no Gemini,
   que não alucinou nenhuma vez em 25 casos revisados.

## Por quê

O usuário (dono do trilho) decidiu, depois de ver os dados das rodadas
14-15, que a etapa de consulta deveria usar o modelo mais confiável
disponível, sem correr o risco de travar o app quando esse modelo externo
tiver algum problema — daí o fallback ser automático e não uma escolha
manual.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Fallback por técnica (rewrite, multi-query, hyde cada um decide sozinho), não por request inteira | Uma falha pontual do Gemini numa chamada não deveria jogar fora o que as outras duas já conseguiram — maximiza a chance de usar Gemini no que der certo |
| 2 | HyDE não cai para Ollama | É a única técnica que o Ollama reprovou por qualidade, não só por estar disponível — cair para ele reintroduziria em silêncio o B-09 |
| 3 | Nenhuma flag nova de configuração — a ausência de `GEMINI_API_KEY` já é o interruptor | Quem não configurar a chave continua exatamente como antes (100% Ollama), sem precisar saber que o `HybridQueryClient` existe |
| 4 | `google-genai` movido de instalação ephemeral para a imagem de verdade (`docker compose build`) | Isso deixou de ser só um experimento — é o que roda em produção agora, precisa sobreviver a um `docker compose up` normal |

## Resultado esperado

_Escrito antes de testar ao vivo._ Esperava que uma chamada real ao
`/chat/` usasse o Gemini nas três técnicas, terminasse a etapa de consulta
bem mais rápido que o Ollama (que levava dezenas de segundos nesta
máquina), e não quebrasse nada que já funcionava.

## Resultado obtido

**Funcionou de ponta a ponta, e o ganho de latência foi maior que o
esperado.** Uma chamada real, ao vivo, contra `POST /chat/`:

```
02:26:09 — reescrita iniciada (Gemini)
02:26:11 — reescrita concluída
02:26:11 — Multi-Query e HyDE disparados em paralelo (Gemini)
02:26:12 — os dois concluídos
```

**A etapa de consulta inteira levou 3,3 segundos** — contra os 20 a 100+
segundos que o mesmo trio de chamadas levava no Ollama nesta máquina (sem
GPU, ver rodada 9). Não era o objetivo desta rodada medir latência, mas é
um efeito colateral grande demais para não registrar.

O documento HyDE gerado citou corretamente "metilxantinas (teobromina e
cafeína)", o mecanismo fisiológico certo (antagonismo de receptores de
adenosina) e a conduta real (carvão ativado, fluidoterapia, benzodiazepínicos
para tremor/convulsão, monitoramento eletrocardiográfico) — sem nenhuma
invenção, no primeiro caso de uso real do sistema integrado.

**Um obstáculo sério no meio do caminho, resolvido:** ao reiniciar o
container para carregar as novas variáveis de ambiente, usei
`docker compose up -d --force-recreate`, que recriou o container a partir
de uma imagem `tcc-backend:latest` **desatualizada** (de 07/09, sem
`pymongo` — o backend caiu num loop de erro, "unhealthy"). A imagem
correta só existia porque o container antigo tinha sido construído em
algum momento posterior sem que a tag `latest` fosse atualizada. Corrigido
com `docker compose build backend` (reconstrução completa, ~7 minutos) e
depois `docker compose up -d backend` a partir da imagem nova — o serviço
voltou saudável, com `pymongo`, `google-genai` e o `pydantic` atualizado
todos presentes.

**Verificação de que nada quebrou:** suíte completa do backend na imagem
nova, **242 passed** (235 + 7 novos: 5 do `HybridQueryClient`, mais os que
já existiam do `GeminiQueryClient` recontados na imagem correta).

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/clients/hybrid_query_client.py` | **novo** — Gemini com fallback para Ollama (exceto HyDE) |
| `backend/app/pipeline/chat_pipeline.py` | `ChatPipeline` usa `HybridQueryClient` por padrão |
| `backend/app/core/config.py` | `HYDE_ENABLED` volta a `True`, comentário atualizado |
| `.env.example` | `HYDE_ENABLED=True`, comentário atualizado |
| `backend/tests/test_hybrid_query_client.py` | **novo** — 5 testes (Gemini ok, fallback em cada técnica, HyDE não cai para Ollama) |

## Observações

**A base vetorial continua vazia no sistema ao vivo.** A chamada real
confirmou "A coleção do ChromaDB está vazia" — nada mudou aqui hoje, é o
mesmo estado desde sempre (B-57 ainda aberto). Perguntei ao usuário se
deveria conectar com a base real do Vinicius agora; ele decidiu **falar
com o Vinicius antes**, porque a evidência do próprio Vinicius registra
várias vezes que aquela base específica não deveria ser ativada sem antes
validar dois arquivos novos pela ASAVET, melhorar a régua de recuperação e
definir critérios de promoção. Não mexi no ponteiro ativo nem no
`CHROMA_PATH`.

**A imagem desatualizada que causou a queda não tem relação com o meu
trabalho de hoje** — é uma dívida de infraestrutura pré-existente (a tag
`latest` ficou para trás de builds anteriores). Vale registrar no backlog
para o trilho A/time saber que `docker compose restart` sozinho não é
suficiente depois de mudar dependências, e que a tag `latest` local pode
estar desatualizada em relação ao que rodava de fato.

## Deixado para depois

**Registrar a dívida da imagem desatualizada no backlog**, para ninguém
mais tomar o mesmo susto.

**Conectar com a base real do Vinicius** — bloqueado, aguardando conversa
com ele (ver acima).

**Medir a latência da etapa de consulta formalmente** (B-07) agora com o
Gemini — o ganho observado ao vivo (3,3s vs. dezenas de segundos) é
grande demais para não formalizar com o instrumento que já existe
(`measure_query_latency.py`).

## Próximo passo

Registrar a dívida da imagem no backlog, e retomar a conversa sobre a
base real do Vinicius quando ele estiver disponível.
