# Paralelizando Multi-Query e HyDE (B-07)

**Data:** 17/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 8 · **Commit:** este

## O que foi feito

`_build_queries` chamava `generate_queries` e `generate_hypothetical_document`
em sequência, mesmo as duas dependendo só da consulta reescrita — nunca uma
da outra. Extraí a lógica para `_generate_variations_and_hyde`, que roda as
duas em `ThreadPoolExecutor(max_workers=2)` quando Multi-Query e HyDE estão
ligados ao mesmo tempo, preservando a ordem final da lista de consultas
(reescrita, variações, documento hipotético) independente de qual chamada
termina primeiro.

## Por quê

B-07 registra que a etapa de consulta custa ~60% da latência do pipeline
completo (3,5s de 5,7s), com as três chamadas ao modelo em sequência. A
reescrita não pode ser paralelizada — as outras duas dependem do seu
resultado —, mas Multi-Query e HyDE são independentes entre si: ambas
recebem a mesma `rewritten` e não trocam informação. São chamadas de rede
(HTTP ao Ollama), presas em I/O, então threads bastam — não é preciso
`asyncio` nem reescrever o cliente do Ollama.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | `ThreadPoolExecutor`, não `asyncio` | O resto do pipeline é síncrono (`ChatPipeline.execute` não é uma corrotina); introduzir `asyncio` aqui exigiria mudar a assinatura de toda a cadeia de chamada. Threads resolvem o problema real (I/O concorrente) sem essa mudança |
| 2 | Só paraleliza quando as duas flags estão ligadas | Com uma só ligada, não há nada para paralelizar — chamar teria o mesmo custo de uma chamada direta, só com a complexidade extra do executor |
| 3 | Resultado final preserva a ordem de sempre (reescrita, variações, HyDE) | O contrato do B-10 (fusão sem duplicatas) e os testes existentes assumem essa ordem; um teste novo (`test_multi_query_e_hyde_juntos_preservam_a_ordem_apesar_do_paralelismo`) trava isso explicitamente |

## Resultado esperado

_Escrito antes de medir._ Esperava que o tempo da etapa de consulta com
Multi-Query e HyDE ligados caísse de "soma das duas chamadas" para
"a mais lenta das duas", e que nenhum teste existente quebrasse.

## Resultado obtido

**Qualitativo, confirmado pelos logs.** Numa chamada real a `/chat/` com as
duas flags ligadas, os logs mostram as duas chamadas submetidas com 14ms de
diferença (`01:11:25,209` e `01:11:25,223`) e suas janelas de execução se
sobrepondo no tempo: HyDE terminou em `01:12:00` (~35s de duração) e
Multi-Query em `01:12:14` (~49s de duração) — se fossem sequenciais, o
Multi-Query só teria começado a rodar depois dos 35s do HyDE, terminando por
volta de `01:12:35` em vez de `01:12:14`. A sobreposição confirma que o
Ollama desta máquina processa as duas chamadas de fato em paralelo, não só
que o cliente as submete em paralelo.

**Não há número limpo para o critério do item ainda.** A mesma chamada caiu
num cold-start do Ollama — a reescrita sozinha (uma frase curta) levou 70s,
o que não reflete o custo em regime normal (medido em rodadas anteriores em
frações de segundo). O critério do B-07 (`query_s` mediano abaixo de 1,5s)
pede uma medição limpa, com modelo já carregado e repetição — exatamente o
que o preset `rag_query --repeat` do runner do B2 já faz. Não rodei isso
nesta sessão porque o runner mede contra a API completa, e a coleção ativa
está vazia neste ambiente (seria medir latência de busca vazia, não de
consulta).

**Verificação de correção:** suíte completa do backend, 207 → **208**
(1 teste novo trava a ordem preservada sob paralelismo).

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/pipeline/chat_pipeline.py` | novo método `_generate_variations_and_hyde`; Multi-Query e HyDE rodam em `ThreadPoolExecutor` quando ambos ligados |
| `backend/tests/test_chat_pipeline.py` | 1 teste novo (ordem preservada com paralelismo) |
| `evidencias/backlog.md` | B-07 passa de Aberto para Em andamento |

## Observações

**A reescrita continua sendo a única chamada que não pode ser paralelizada**
— é uma dependência real (as outras duas leem o texto que ela produz), não
uma limitação da implementação. O ganho máximo teórico desta mudança é
eliminar uma das três chamadas sequenciais quando o pipeline completo está
ligado; com `HYDE_ENABLED=False` por padrão (B-09), a configuração padrão de
produção não passa por este caminho — o ganho vale para quem ligar HyDE
manualmente (via preset ou por requisição) e ainda quiser Multi-Query junto.

## Deixado para depois

**Medir `query_s` mediano com o runner, modelo aquecido, contra uma coleção
com conteúdo** — é o critério numérico do próprio item, e exige um ambiente
sem os dois fatores de ruído desta rodada (cold-start e coleção ativa vazia).
Não fechar o B-07 como "Resolvido" até essa medição existir.

## Próximo passo

O item B-56 (autenticação) foi conscientemente adiado para quando a API for
exposta publicamente — decisão confirmada com o usuário nesta rodada. Os
itens abertos do meu trilho voltam a ser a prova oficial (~150 casos, já era
a entrega prioritária do time) e o benchmark de WER com áudio real.
