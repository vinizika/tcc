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

**Etapa atual: 6 de 7.** O produto classifica de verdade, a régua existe e
recusa medir sobre a base errada. O Marco 1 está medido, e o
Chain-of-Thought foi medido e reprovado — um resultado negativo com
mecanismo identificado.

| # | Entrega | Situação | O que entregou / entrega |
|---|---|---|---|
| 0 | Estado inicial | ✅ 03/09 | Ponto de partida documentado, com o baseline e duas limitações do conjunto de avaliação |
| 1 | Higiene e ambiente | ✅ 03/09 | Arquivos gerados fora do Git; clone limpo sobe; modelo rodando na GPU |
| 2 | Configuração centralizada | ✅ 03/09 | Mesmo código em Docker e local; saída estruturada validada |
| 3 | Geração ancorada | ✅ 04/09 | **O mock morreu.** Classificação real com fontes citadas, etapas ligáveis por requisição, 43 testes |
| 4 | Runner de avaliação | ✅ 04/09 | A régua: rodadas versionadas com manifesto, métricas e teste estatístico. **Marco 1 medido** |
| 5a | Endurecimento do instrumento | ✅ 11/09 | Revisão das entregas dos outros trilhos; o runner recusa base errada ou vazia, o retrato identifica conteúdo e embedder, o `compare` avisa mudança de código. **Nenhuma métrica mudou** |
| 5 | **Chain-of-Thought** | ✅ 11/09, **resultado negativo** | Implementado e medido em cinco braços. Falsos não urgentes de 8 para 1, mas falsos urgentes de 4 para 16 e recall da classe leve a **zero**. Balanceada de 0,856 para 0,408. Não entra no sistema; fica desligado e medido para a ablação |
| 6 | **Self-Refine** | 🔜 **próxima**, com desenho revisto | A rodada 8 mostrou que este modelo aplica mal uma regra explícita. O que sobrevive do plano é a **trava de segurança** determinística, que não depende do julgamento do modelo |
| 7 | Driver de ablação | ⏳ | Cruza as chaves de todos os trilhos e gera as tabelas do artigo |

## Próxima entrega: Self-Refine, com o desenho revisto

**O que a rodada 8 mudou.** O plano original era o modelo revisar a própria
resposta e corrigi-la. O Chain-of-Thought acabou de mostrar que, quando este
modelo recebe uma regra explícita e a aplica, ele a aplica mal — não por
desobedecer, mas porque o julgamento clínico que a regra pressupõe não está
lá (marca claudicação como risco à vida em 20 de 25 vezes,
[B-41](../backlog.md#b-41)). Um Self-Refine que peça "revise sua decisão"
tende ao mesmo destino.

**O que sobrevive.** A **trava de segurança**: o código que compara a
revisão com o rascunho e só aceita rebaixar a urgência quando a justificativa
cita um trecho literal do relato ou dos documentos. Ela é determinística, não
depende do julgamento do modelo, e é a única parte do desenho que a rodada 8
não enfraqueceu. Também endereça o [B-14](../backlog.md#b-14), o detalhe
inventado na justificativa.

**Como será medido:** o mesmo braço com e sem a chave, com a trava registrando
quantas revisões foram recusadas e por quê. Uma revisão que nunca é aceita é
tão informativa quanto uma que sempre é.

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
| 9 | **O rótulo de título e seção vai embutido no texto do trecho.** Depois da reindexação, ele chega ao classificador como se fosse texto do protocolo | Trilho A | Rodada 7 (11/09) | Qualquer medição com RAG sobre a base nova mistura o efeito do rótulo com o da recuperação. Sem efeito hoje: a base não foi reindexada | [B-36](../backlog.md#b-36) |
| 10 | **A base de 18 trechos não pode mais ser gerada.** O algoritmo de chunking mudou em 07/09 e os manuais divergiam | Trilho A (data da virada) | Rodada 7 (11/09) | As rodadas citadas R3, R3c e R6 dependem dela. Um clone limpo não a reproduz; na virada, os braços com RAG precisam ser remedidos | [B-37](../backlog.md#b-37) |

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
