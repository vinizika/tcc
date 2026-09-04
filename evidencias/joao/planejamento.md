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

A régua é a parte que dá o número do TCC. O baseline a ser superado está
medido: **70,41% de acurácia**, contra 72% de um modelo que sempre responde
"emergência", com recall de não emergência em apenas 14,81%.

## Onde estou

**Etapa atual: 4 de 7.** O produto classifica de verdade; falta a régua que
transforma isso em número.

| # | Entrega | Situação | O que entregou / entrega |
|---|---|---|---|
| 0 | Estado inicial | ✅ 03/09 | Ponto de partida documentado, com o baseline e duas limitações do conjunto de avaliação |
| 1 | Higiene e ambiente | ✅ 03/09 | Arquivos gerados fora do Git; clone limpo sobe; modelo rodando na GPU |
| 2 | Configuração centralizada | ✅ 03/09 | Mesmo código em Docker e local; saída estruturada validada |
| 3 | Geração ancorada | ✅ 04/09 | **O mock morreu.** Classificação real com fontes citadas, etapas ligáveis por requisição, 43 testes |
| 4 | **Runner de avaliação** | 🔜 **próxima** | Transforma casos isolados em número sobre os 98 relatos |
| 5 | Chain-of-Thought | ⏳ | Raciocínio em etapas antes da classificação, medido isoladamente |
| 6 | Self-Refine | ⏳ | Revisão da própria resposta, com trava de segurança |
| 7 | Driver de ablação | ⏳ | Cruza as chaves de todos os trilhos e gera as tabelas do artigo |

## Próxima entrega: o runner de avaliação

**O problema que resolve.** Hoje o script de métricas do projeto aponta para
um endpoint que não existe mais, então os 70,41% não são reproduzíveis. E a
[rodada 3](2026-09-04-04-geracao-ancorada.md) mostrou por que casos isolados
não bastam: o mesmo relato deu acerto em três execuções e erro grave numa
quarta. Sem medir sobre o conjunto inteiro, qualquer conclusão é anedota.

**O que vai fazer:** rodar os 98 relatos contra a API, calcular acurácia,
recall por classe, F1 e tempo de resposta, e salvar cada rodada com um
manifesto do que foi executado — quais etapas estavam ligadas, qual modelo,
qual configuração. Duas rodadas passam a ser comparáveis porque o manifesto
diz o que mudou entre elas.

**Três medições logo depois:**

1. **Reproduzir o baseline antigo**, para provar que a régua mede a mesma
   coisa que a medição de 04/05.
2. **Fixar uma linha de base determinística**, com temperatura zero.
3. **Marco 1: a primeira triagem com RAG medida ponta a ponta**, comparada
   com a linha de base. É o número central do artigo.

## Marcos

| Quando | Marco |
|---|---|
| 8–19 set | **Marco 1** — primeira triagem RAG medida sobre os 98 relatos, comparada ao baseline |
| Outubro | **Marco 2** — matriz de ablação completa; sai da geladeira o que foi adiado (frontend, RAGAs, geolocalização, deploy) |
| Novembro | **Marco 3** — números congelados, escrita final |

## O que está travando

| Bloqueio | De quem depende | Efeito |
|---|---|---|
| **Temperatura e seed na etapa de consulta** | Trilho B1 | Sem isso as consultas mudam a cada execução, e **nenhuma rodada com RAG é reproduzível**. Medido: 1 erro em 4 execuções do mesmo relato. É a pendência mais urgente do projeto hoje |
| Ordenação da busca | Trilho A | O documento certo nem sempre aparece entre os primeiros. Limita o ganho que o RAG pode mostrar nas medições |
| Base de conhecimento sintética | Trilho A + especialista | Os 7 protocolos são de teste. O artigo promete base curada, e curadoria depende de gente, não de código |

Nenhum deles impede o runner de ser construído. Eles limitam o **resultado**
que ele vai medir — e é justamente por isso que o runner registra o score da
recuperação em cada linha: para separar "a decisão errou" de "a busca não
trouxe o que era preciso".

## Fora do escopo deste trilho

Chunking, ingestão, embeddings e re-ranking são do trilho A. Reescrita de
consulta, multi-query, HyDE e Whisper são do B1. Frontend novo, RAGAs,
geolocalização, resumo MIST e deploy estão adiados para outubro por decisão
do time.
