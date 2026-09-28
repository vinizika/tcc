# Comparando Gemini e Ollama na etapa de consulta

**Data:** 22/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 14 · **Commit:** este

## O que foi feito

Construí um espelho experimental do `QueryClient` — `GeminiQueryClient`
([`backend/app/clients/gemini_query_client.py`](../../backend/app/clients/gemini_query_client.py))
— usando a API do Gemini em vez do Ollama local, com os **mesmos três
prompts** (extraídos como constantes em `query_client.py` para garantir que
os dois usam texto idêntico) e a mesma interface. Um script comparador
([`backend/app/database/compare_query_providers.py`](../../backend/app/database/compare_query_providers.py))
roda os dois lado a lado contra a mesma coleção candidata (3.481 chunks) e
grava os dois resultados.

Rodei contra 9 casos da régua de recuperação (b01-b09), respeitando o
limite gratuito do Gemini com um teto de chamadas e uma pausa de 7s entre
cada uma.

Isolado da produção de propósito: `ChatPipeline` continua usando só o
`QueryClient` (Ollama).

## Por quê

O grupo pediu para testar se um modelo maior (Gemini) melhora a etapa de
consulta o suficiente para justificar a complexidade de depender de uma API
externa — sem travar o app real caso o limite gratuito seja atingido no
meio de uma pergunta de tutor. A resposta a essa segunda parte foi rodar
como experimento isolado, nunca no caminho de produção; a resposta à
primeira parte é o que esta rodada mede.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Extrair os três prompts do `QueryClient` como constantes reaproveitadas pelo `GeminiQueryClient` | Garante que a única variável do experimento é o modelo — se os textos divergissem, uma diferença de resultado poderia vir do prompt, não do provedor |
| 2 | Nada em produção chama `GeminiQueryClient` | O grupo foi explícito: não travar o sistema real por causa de um limite de API externa. A resposta mais simples é não integrar até decidir que vale a pena |
| 3 | Teto de chamadas + pausa de 7s, não só tratamento de erro | Um erro 429 tratado sozinho ainda deixaria a rodada gastar toda a cota do dia sem querer; o teto para a execução antes disso |
| 4 | Erro do Gemini vira `LLMException` e o caso é marcado com o erro, sem derrubar a rodada inteira | Perder o restante da amostra por causa de uma falha pontual (limite, rede) desperdiçaria as chamadas já gastas |

## Resultado esperado

_Escrito antes de rodar._ Não tinha uma expectativa forte sobre
Precision@1/MRR — 9 casos é pouco para qualquer conclusão estatística.
Tinha uma hipótese qualitativa: um modelo maior deveria alucinar menos na
reescrita e no HyDE, que é o problema histórico documentado desde o B-09
("Síndrome de Sífilo da Cadeia de Reações Imunes", um diagnóstico
inventado pelo `llama3.2:3b`).

## Resultado obtido

### Quantitativo — inconclusivo, como esperado com 9 casos

| | Ollama | Gemini |
|---|---:|---:|
| Precision@1 | 3/9 (0,333) | 3/9 (0,333) |
| MRR | 0,436 | 0,455 |

Empate técnico. E não é o mesmo empate: Gemini acertou `b08` (intoxicação
por cebola/alho) onde o Ollama errou feio (recuperou
`grape_xylitol_toxicosis`); Ollama acertou `b09` (dermatite por pulga) onde
o Gemini errou (`airway_foreign_body_choking`). Nenhum dos dois domina o
outro na recuperação, nesta amostra.

### Qualitativo — diferença real e visível

Reli as reescritas, variações e documentos HyDE dos 9 casos. Dois exemplos
concretos, lado a lado:

**Caso b04 (convulsão) — HyDE:**

> **Ollama:** "...pode ser relacionada a condições neurológicas, como
> encefalite viral, encefalite subviral, lesões cerebrais, toxinas,
> metabolismo, doenças hereditárias ou **degenerativas, como a doença de
> Huntington**, entre outras."

Doença de Huntington é uma doença genética **humana**. O modelo local
inventou um diferencial que não existe em medicina veterinária — o mesmo
tipo de alucinação que motivou o B-09 originalmente.

> **Gemini:** "...etiologia diferencial inclui epilepsia idiopática,
> encefalopatias metabólicas, intoxicações exógenas ou processos
> inflamatórios/neoplásicos intracranianos; a conduta imediata requer
> avaliação neurológica e cardiorrespiratória, instituição de terapia
> anticonvulsivante de emergência (como benzodiazepínicos)..."

Diferenciais reais, terminologia correta, conduta clinicamente defensável.

**Caso b08 (intoxicação por cebola/alho) — HyDE:**

> **Ollama:** "...caracterizada por **hipotirese**, evidenciada por uma cor
> pálida e clara da pele..."

"Hipotirese" não é um termo médico — nem humano, nem veterinário. É uma
palavra inventada.

> **Gemini:** "...anemia hemolítica oxidativa com **formação de corpúsculos
> de Heinz**; a conduta clínica imediata compreende a indução de êmese (se
> recente ingestão), administração de carvão ativado, fluidoterapia
> intravenosa agressiva, monitoramento hematológico seriado e, em casos de
> anemia grave, suporte transfusional..."

Corpúsculos de Heinz é exatamente o mecanismo correto e específico da
intoxicação por *Allium* em cães — o tipo de precisão que um profissional
esperaria de um texto de referência.

Em nenhum dos 9 casos encontrei o Gemini inventando um termo ou diagnóstico
que não existe; encontrei pelo menos dois no Ollama só nestes dois casos
revisados em detalhe.

### Um obstáculo no caminho: nome do modelo mudou

`gemini-2.5-flash-lite` (o modelo que configurei inicialmente, com base na
pesquisa de preços/limites da conversa anterior) **não existe mais para
contas novas** — a própria API respondeu com o nome certo no erro 404:
`gemini-3.5-flash-lite`. Modelos desta família parecem ter vida curta;
qualquer reprodução futura deste experimento deve conferir o nome atual
antes de gastar cota.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/clients/query_client.py` | Prompts extraídos como constantes (`REWRITE_SYSTEM_PROMPT`, `MULTI_QUERY_SYSTEM_PROMPT`, `HYDE_SYSTEM_PROMPT`) — comportamento idêntico, só reorganizado |
| `backend/app/clients/gemini_query_client.py` | **novo** — espelho do QueryClient usando Gemini |
| `backend/app/database/compare_query_providers.py` | **novo** — script de comparação, com teto de chamadas e pausa |
| `backend/tests/test_gemini_query_client.py` | **novo** — 6 testes, com dublê do cliente Gemini (não precisam de rede nem de chave real) |
| `backend/app/core/config.py` | `GEMINI_API_KEY`, `GEMINI_MODEL` — nenhuma etapa de produção lê estas duas |
| `.env.example` | Campos vazios/documentados para as duas configs novas |
| `backend/requirements.txt` | `google-genai==2.24.0`; `pydantic` subiu de 2.11.7 para 2.13.5 (piso exigido pelo `google-genai`, testado sem quebrar nada) |
| `evidencias/ryu/dados/2026-09-22-comparacao-gemini-ollama.json` | Resultado bruto da rodada (9 casos, os dois provedores) |

**Verificações:** suíte do backend, 229 → **235** (6 testes novos). Sem
regressão depois da atualização do `pydantic`.

## Observações

**Um incidente de segurança no meio do caminho, corrigido na hora.** O
usuário colou a chave real do Gemini em `.env.example` (rastreado e
público) em vez de `.env`. Identifiquei antes de qualquer commit — a chave
nunca chegou a ficar no histórico do Git nem foi enviada ao GitHub. Movi a
chave para `.env` e limpei o `.env.example` na mesma hora. Recomendei ao
usuário gerar uma chave nova por precaução, já que esta também ficou
registrada na conversa.

**A amostra de 9 casos não decide nada sozinha** — nem a favor, nem contra.
O que decide é o padrão qualitativo: se ele se repetir numa amostra maior
(a régua inteira tem mais casos, e a prova nova tem 150), aí sim vira
evidência de que vale a pena pagar a complexidade de uma API externa para
pelo menos a etapa de HyDE, que é justamente a que mais alucina.

**Custo desta rodada:** 27 chamadas ao Gemini, dentro do limite diário
gratuito por uma folga enorme (o limite é da ordem de centenas por dia).

## Deixado para depois

**Rodar contra uma amostra maior** (a régua inteira, ou uma fatia da prova
nova de 150 casos) para ver se o padrão qualitativo se sustenta com número,
não só com leitura manual de 2 casos.

**Se o padrão se sustentar, decidir isoladamente por técnica**: talvez só
o HyDE precise de um modelo maior (é o que mais alucina), enquanto reescrita
e multi-query já funcionam bem o suficiente no Ollama — o que reduziria a
dependência da API externa ao mínimo necessário.

**Só depois disso** desenhar a integração real com fallback para Ollama —
não antes de saber se há algo que valha a complexidade.

## Próximo passo

Reportar ao grupo o achado qualitativo (alucinação vs. precisão clínica) e
perguntar se vale escalar a amostra antes de qualquer decisão de adoção.
