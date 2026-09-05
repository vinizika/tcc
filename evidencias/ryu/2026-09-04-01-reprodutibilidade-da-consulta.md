# Reprodutibilidade das chamadas de consulta (B-04)

**Data:** 04/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 1

## O que foi feito

As três chamadas ao modelo em `backend/app/clients/query_client.py`
(`rewrite`, `generate_queries`, `generate_hypothetical_document`) passaram a
enviar `options=default_options()` ao Ollama, importado de
`app.core.ollama` — a mesma função que o trilho B2 já usa na etapa de
classificação. Adicionado `backend/tests/test_query_client.py` com um teste
por método, verificando que a chamada real ao cliente recebe exatamente
essas opções.

## Por quê

O João (B2) identificou em [B-04](../backlog.md#b-04) que, sem `options`, as
três chamadas usam a temperatura padrão do Ollama (0,8) com seed aleatória.
Com o pipeline completo, 33 das 98 linhas da avaliação mudavam de
classificação entre execuções idênticas (concordância de 0,663) — nenhuma
rodada com o pipeline completo é reproduzível, e o estudo de ablação do
artigo depende disso. Era o item de prioridade Alta mais isolado do meu
trilho: três chamadas, um arquivo, sem depender de decisão de ninguém.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Reusar `default_options()` de `app.core.ollama`, sem parâmetros | É a mesma fonte de verdade que a etapa de decisão já usa (`temperature=0`, `seed=42`, `num_ctx`, `num_predict` das settings); duas fontes de configuração de temperatura/seed seriam a próxima causa de inconsistência |
| Testar com um dublê do cliente Ollama, não com o servidor real | Segue o padrão do `conftest.py` do time (dublês para `RetrievalClient`, `LLMClient`); testes de reprodutibilidade fim a fim continuam dependendo de Ollama de pé e ficam para a régua de avaliação, não para o pytest |

## Resultado esperado

As três chamadas passam a receber a mesma configuração determinística da
etapa de decisão. Não estimo aqui uma redução exata na taxa de instabilidade
(os 0,663 de concordância citados por João foram medidos com o pipeline
completo, não isolando a etapa de consulta) — o critério do backlog é
**o preset `rag_query` com `--repeat 2` chegando a zero linhas instáveis**,
o que só se confirma rodando o runner com Ollama ativo.

## Resultado obtido

**Nível de unidade, confirmado.** Os três testes novos passam e comprovam
que `options=default_options()` chega ao cliente em cada uma das três
chamadas — o mecanismo do bug (ausência de `options`) está corrigido.

**Nível de sistema, pendente.** Este ambiente não tem um servidor Ollama
acessível (`localhost:11434` não responde), então não rodei o critério de
aceitação do backlog (`--set` do preset `rag_query` com `--repeat 2` contra
o runner). Fica como o primeiro passo de quem pegar esta rodada em uma
máquina com Ollama disponível — comando abaixo.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/clients/query_client.py` | import de `default_options`; `options=default_options()` nas três chamadas (`rewrite`, `generate_queries`, `generate_hypothetical_document`) |
| `backend/tests/test_query_client.py` | **novo** — três testes garantindo que cada chamada recebe as opções padrão |

## Observações

Os outros itens de B1 no backlog (B-07 latência, B-08 julgamento clínico na
reescrita, B-09 HyDE não medido, B-10 fusão reescrita+variações, B-13
Whisper) continuam abertos. B-09 em particular está bloqueado por fora do
trilho: a régua de recuperação do trilho A (Precision@1/MRR) ainda não
existe, então "ligado vs. desligado" para HyDE/multi-query/rewriting não tem
onde ser medido ainda.

## Deixado para depois

Rodar o preset `rag_query --repeat 2` contra o runner do B2 para confirmar
o critério de aceitação numérico do B-04 — depende de Ollama rodando
localmente, que este ambiente não tem.

## Próximo passo

Com B-04 fechado no nível de unidade, o próximo item natural do trilho é
**B-10** (decisão de fundir `[reescrita] + variações` sem duplicatas em
`_build_queries`) — é uma decisão que só o dono do trilho pode tomar, está
bem delimitada em `docs/CONTRATOS.md` e não depende da régua do trilho A.
