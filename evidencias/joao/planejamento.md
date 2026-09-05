# Planejamento do trilho B2 — Decisão

Roteiro do trilho: o que já foi entregue, o que vem a seguir e o que está
travando. Serve de controle para o time e para o orientador acompanharem sem
precisar ler o histórico de commits.

O registro detalhado de cada entrega — decisões, resultados medidos e
observações — está nas [rodadas](README.md). O escopo do trilho e as
fronteiras com os outros estão em
[`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md).

---

## Objetivo do trilho

Cuidar do caminho **da evidência recuperada até a resposta**: transformar os
trechos que a busca encontrou em uma decisão de triagem confiável, e ser a
**régua que mede o sistema inteiro**.

A régua é a parte que dá o número do TCC. Estado das medições em 04/09,
sobre os 98 relatos de cão e gato:

| Configuração | Acurácia balanceada | Falsos não urgentes |
|---|---|---|
| Medição de 04/05 (prompt antigo) | 0,532 | 4 de 71 |
| **Melhor atual**: prompt novo, sem RAG | **0,893** | 8 de 71 |
| Com RAG e a base de hoje | 0,763 | **30 de 71** |

A métrica principal é a **acurácia balanceada**, média do recall das duas
classes: como 71 das 98 linhas são emergência, um sistema que sempre responde
"emergência" acerta 72,4% na acurácia simples, e ela premiaria esse
comportamento. O detalhe de cada número está nas rodadas.

## Onde estou

**Etapa atual: 5 de 7.** O produto classifica de verdade e a régua existe.
O Marco 1 está medido.

| # | Entrega | Situação | O que entregou / entrega |
|---|---|---|---|
| 0 | Estado inicial | ✅ 03/09 | Ponto de partida documentado, com o baseline e duas limitações do conjunto de avaliação |
| 1 | Higiene e ambiente | ✅ 03/09 | Arquivos gerados fora do Git; clone limpo sobe; modelo rodando na GPU |
| 2 | Configuração centralizada | ✅ 03/09 | Mesmo código em Docker e local; saída estruturada validada |
| 3 | Geração ancorada | ✅ 04/09 | **O mock morreu.** Classificação real com fontes citadas, etapas ligáveis por requisição, 43 testes |
| 4 | Runner de avaliação | ✅ 04/09 | A régua: rodadas versionadas com manifesto, métricas e teste estatístico. **Marco 1 medido** |
| 5 | **Chain-of-Thought** | 🔜 **próxima** | Raciocínio em etapas antes da classificação, medido isoladamente |
| 6 | Self-Refine | ⏳ | Revisão da própria resposta, com trava de segurança |
| 7 | Driver de ablação | ⏳ | Cruza as chaves de todos os trilhos e gera as tabelas do artigo |

## Próxima entrega: Chain-of-Thought

**O problema que resolve.** O erro que mais importa hoje é o falso não
urgente: 8 em 71 no melhor braço, e 30 em 71 quando o RAG entra. A hipótese
é que pedir ao modelo para percorrer os sinais um a um, antes de concluir,
reduza a chance de ele rebaixar um caso grave por comparação com o contexto
— que foi exatamente o mecanismo observado na
[rodada 4](2026-09-04-05-runner-de-avaliacao.md).

**O que vai fazer:** a chave `cot_enabled`, que hoje é recusada com erro 400
de propósito, passa a funcionar. O modelo escreve o raciocínio antes da
classificação, e a ordem importa: o campo do raciocínio precisa vir primeiro
no formato de saída, ou a conclusão sai antes do que a justifica.

**Como será medido:** o mesmo braço com e sem a chave, sobre o conjunto
inteiro, comparados com o teste pareado. Também o custo em tokens e em
tempo, porque o artigo trata latência como requisito.

Depois dela vêm o Self-Refine e o driver que cruza as chaves de todos os
trilhos para gerar as tabelas do artigo.

## Marcos

| Quando | Marco |
|---|---|
| 8–19 set | **Marco 1** — primeira triagem RAG medida sobre os 98 relatos, comparada ao baseline |
| Outubro | **Marco 2** — matriz de ablação completa; sai da geladeira o que foi adiado (frontend, RAGAs, geolocalização, deploy) |
| Novembro | **Marco 3** — números congelados, escrita final |

## O que está travando

Esta seção **só cresce**. Um bloqueio entra com a data em que foi visto e de
onde veio, e permanece até o trilho responsável resolvê-lo — só então vai
para "Resolvidos", com a data. Nada é apagado ou substituído: é a lista que
diz aos outros desenvolvedores o que fazer para ajudar, e a trilha de como
cada problema apareceu é parte do valor.

Aqui fica só o resumo. O detalhe de cada item — o que foi observado, com os
dados, o que resolveria e o status — mora no
[backlog do projeto](../backlog.md), no ID indicado.

### Aberto

| # | Bloqueio | De quem depende | Visto em | Efeito medido | Detalhe |
|---|---|---|---|---|---|
| 1 | **Com a base atual, ligar o RAG degrada o sistema.** Enquanto a busca não separar assunto, o contexto irrelevante recalibra o julgamento do modelo para cima e ele rebaixa emergências | Trilho A | Rodada 4 (04/09) | **−20,4 pontos de acurácia** (IC 95% de −29,6 a −11,2; p = 0,0001) e **+22 falsos não urgentes**. Em 100% das linhas nenhum trecho passou do limiar de relevância; score máximo médio de 0,574 | [B-01](../backlog.md#b-01) |
| 2 | **Ordenação da busca não separa assunto.** Para um relato de espirro, o protocolo de obstrução urinária apareceu em primeiro com 0,8183 | Trilho A | Rodada 3 (04/09) | É a causa provável do bloqueio 1 | [B-02](../backlog.md#b-02) |
| 3 | **Base de conhecimento sintética.** Os 7 protocolos são de teste e todos tratam de emergência, o que enviesa qualquer recuperação | Trilho A + especialista | Rodada 3 (04/09) | O artigo promete base curada; curadoria depende de gente, não de código | [B-03](../backlog.md#b-03) |
| 4 | **Temperatura e seed não fixadas na etapa de consulta.** As três chamadas usam o padrão do Ollama | Trilho B1 | Rodada 3 (04/09) | Nenhuma rodada com o pipeline completo é reproduzível. São três linhas de correção, com o que já existe em `core/ollama.py`. **Atualização 05/09 (rodada 6):** o B1 corrigiu em `b907d6e` e a instabilidade caiu de 33 para 6 linhas em 98 — 82% do problema. O resto é ruído numérico de GPU, que seed não controla; o bloqueio permanece aberto porque o critério pede zero, e rever esse critério virou [B-24](../backlog.md#b-24) | [B-04](../backlog.md#b-04) |
| 5 | **O conjunto de avaliação é trivialmente separável.** A classe não emergência usa 5 termos de sintoma contra 192 da outra, e tem 3 ou 4 sintomas contra sempre 5 | Time + especialista | Rodada 4 (04/09) | A regra "só sintomas leves" acerta **98 de 98** sem modelo nenhum. O conjunto mede se o sistema parou de exagerar cinco sinais leves, não a capacidade geral de triagem | [B-05](../backlog.md#b-05) |
| 6 | **A etapa de consulta custa 63% do tempo de resposta.** Três chamadas sequenciais ao modelo antes de qualquer busca | Trilho B1 | Rodada 3 (04/09) | Relevante para o requisito de latência do artigo. As chamadas são independentes e poderiam ser paralelas ou fundidas | [B-07](../backlog.md#b-07) |
| 7 | **`RERANK_TOP_K` e `CONTEXT_TOP_K` se sobrepõem.** A primeira é do trilho A e hoje não é usada | Trilho A + B2 | Rodada 3 (04/09) | Quando o re-ranking real cortar em 3, pedir 5 trechos devolverá 3 em silêncio | [B-17](../backlog.md#b-17) |
| 8 | **O critério de aceitação do B-04 precisa de decisão do time.** Ele pede zero linhas instáveis, mas 6 sobram por ruído numérico de GPU, que nenhuma configuração controla | Time (decisão de método) | Rodada 6 (05/09) | Enquanto não se decide, o B-04 fica aberto sem que ninguém possa fechá-lo, e a matriz de ablação de outubro não tem regra definida para comparar braços que usam a etapa de consulta | [B-24](../backlog.md#b-24) |

### Resolvidos

*(nenhum ainda)*

Nenhum destes impediu o runner de ser construído. Eles limitam o
**resultado** que ele mede — e é por isso que cada linha de cada rodada
registra o score da recuperação: para separar "a decisão errou" de "a busca
não trouxe o que era preciso".

## Fora do escopo deste trilho

Chunking, ingestão, embeddings e re-ranking são do trilho A. Reescrita de
consulta, multi-query, HyDE e Whisper são do B1. Frontend novo, RAGAs,
geolocalização, resumo MIST e deploy estão adiados para outubro por decisão
do time.
