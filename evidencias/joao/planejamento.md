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
| 6 | **Entrega a decidir** | ⏸️ aguardando as três correções ([adendo da rodada 9](2026-09-12-09-autopsia-do-cot.md#adendo-de-1209--as-três-correções-em-linguagem-simples-e-uma-hipótese-em-espera)) | O Self-Refine como planejado ficou enfraquecido: o que o modelo escreve sobre a própria decisão é racionalização. Uma camada de decisão determinística foi avistada e está **em stand-by**, por decisão do João — volta só se as correções não bastarem ou como braço a mais da ablação. Qualquer alternativa depende do corte, da base e da prova para ser **avaliada** sem circularidade |
| 7 | Driver de ablação | ⏳ | Cruza as chaves de todos os trilhos e gera as tabelas do artigo |

## Próxima entrega: a decidir, depois das três correções

A [rodada 9](2026-09-12-09-autopsia-do-cot.md) e a conversa que a seguiu
levaram a uma conclusão sobre **ordem**, registrada no adendo dela: antes de
qualquer técnica nova na etapa de decisão, três coisas precisam acontecer, e
duas delas não são do meu trilho.

1. **O corte de relevância** deixa de ser zero — meia parte minha, meia do
   trilho A, decisão do time ([B-11](../backlog.md#b-11)). É a mais barata e
   a mais urgente: enquanto ele for zero, toda medição com RAG mede ruído.
2. **A base** passa a cobrir os assuntos do conjunto, com quadros leves,
   validada ([B-03](../backlog.md#b-03)). Trilho A e especialista.
3. **A prova** deixa de ser separável por vocabulário e ganha um conjunto de
   desenvolvimento ([B-05](../backlog.md#b-05), [B-45](../backlog.md#b-45)).
   Time e especialista.

Do meu lado, o que anda enquanto isso: o teste limpo da ordem
([B-46](../backlog.md#b-46)), o item do modelo maior para o time
([B-42](../backlog.md#b-42)), e o driver de ablação (entrega 7), que não
depende do resultado de nenhum braço.

**O Self-Refine** como planejado perdeu força com a autópsia: o que o modelo
escreve sobre a própria decisão é racionalização, não julgamento. A trava de
segurança, que é código, continua valendo.

**Uma camada de decisão determinística** — o modelo extrai os sinais, uma
tabela validada pela especialista decide — foi avistada e descrita no adendo
da rodada 9. Está **em stand-by** por decisão do João: cedo para decidir. Não
é candidata em disputa; é uma saída registrada para não se perder.

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
| 11 | **A base não cobre os assuntos do conjunto de avaliação, e nenhum protocolo fala de quadros leves.** O desenho de Chain-of-Thought do artigo pressupõe evidência recuperada para o modelo não julgar sozinho | Trilho A + especialista | Rodada 9 (12/09) | O CoT como o artigo o desenhou **nunca foi testado**: o passo "correlacionar com as evidências recuperadas" não teve evidência | [B-03](../backlog.md#b-03) |
| 12 | **O corte de relevância da busca é zero.** Nas 98 linhas, nenhum trecho passou do limiar de 0,70, e três entraram em todos os prompts assim mesmo | Trilho A | Rodada 9 (12/09) | Os braços com recuperação mediram **injeção de ruído**, não conhecimento. Com o corte aplicado, `naive_rag` seria idêntico a `llm_only` | [B-11](../backlog.md#b-11) |
| 13 | **Os relatos de avaliação não têm gravidade nem duração.** São listas de sintomas | Time + especialista | Rodada 9 (12/09) | É a causa raiz do fracasso do CoT: a rubrica por sinal pergunta o que o dado não permite responder. Em 21 das 23 abstenções o modelo contrariou a regra para seguir "sem informação suficiente, responda INCERTO" | [B-05](../backlog.md#b-05) |

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
