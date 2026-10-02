# Rodada 25 — comparação SBERT e LangChain

Pedido: testar se adotar SBERT e/ou LangChain melhora o sistema atual.
Base: `454bdcf`, após comunicação VetIA. Experimento isolado, sem migração do
produto, sem alteração da coleção ativa e sem chamadas ao Gemini.

## Resultado principal

**Manter BGE-M3; não adotar LangChain apenas por desempenho.** MiniLM foi
7,43 vezes mais rápido na mediana da busca direta, mas o hit@3 caiu de
86,45% para 52,99%. LangChain preservou todos os ranks, notas e prompts nos
1.506 pares comparados, sem ganho de recuperação.

| Configuração | Hit@1 (251 casos) | Hit@3 | Mediana busca + prompt | p95 |
|---|---:|---:|---:|---:|
| BGE-M3 direto | 181/251 (72,11%) | 217/251 (86,45%) | 622,07 ms | 1.305,04 ms |
| BGE-M3 + LangChain | 181/251 (72,11%) | 217/251 (86,45%) | 632,80 ms | 1.337,04 ms |
| MiniLM direto | 82/251 (32,67%) | 133/251 (52,99%) | 83,67 ms | 162,94 ms |
| MiniLM + LangChain | 82/251 (32,67%) | 133/251 (52,99%) | 77,96 ms | 153,96 ms |

Tempos de 753 chamadas por linha, após aquecimento; qualidade conta cada caso
uma vez. Medianas agregadas não representam diferença pareada: a mediana da
diferença LangChain − direto foi +5,57 ms no BGE e −3,00 ms no MiniLM. Não há
evidência de ganho geral de velocidade do framework: a direção mudou entre
modelos e o caminho direto inclui collection.count(), enquanto o adaptador
LangChain conhece o k da coleção congelada. Além disso, o ambiente foi compartilhado.

| Conjunto | BGE hit@1 / hit@3 | MiniLM hit@1 / hit@3 | Perda de hit@3 |
|---|---:|---:|---:|
| Régua (66) | 58 / 65 | 26 / 39 | 39,39 p.p. |
| Dev (47) | 39 / 43 | 14 / 26 | 36,17 p.p. |
| Calibração com tópico (16) | 10 / 15 | 4 / 8 | 43,75 p.p. |
| Independentes (122) | 74 / 94 | 38 / 60 | 27,87 p.p. |

No pareamento por caso, MiniLM ganhou cinco casos no top 3 e perdeu 89; saldo
−84/251 (−33,47 p.p.). Nos independentes, BGE alcançou 77,05% contra 49,18%.
Hit@5 global: BGE 231/251; MiniLM 168/251. MRR nos primeiros 50: 0,80862 e
0,48093. Todas as ordenações permaneceram estáveis nas três repetições.
Detalhes nos [agregados](2026-10-02-sbert-langchain/summary.json) e na
[comparação por caso](2026-10-02-sbert-langchain/case-comparison.json).

## Recursos e comportamento observado

| Medida | BGE-M3 | MiniLM |
|---|---:|---:|
| Carga do modelo em cache | 3,68 s | 3,61 s |
| Indexação das 61 fichas | 186,93 s | 5,69 s |
| Pico RSS do processo | 2.193,02 MiB | 1.253,42 MiB |
| Dimensões | 1.024 | 384 |
| Payload float32 dos 61 vetores | 249.856 bytes | 93.696 bytes |
| Teto nativo de tokens | 8.192 | 128 |
| Fichas truncadas | 0/61 | 61/61 |
| Consultas truncadas | 0/251 | 0/251 |

As fichas têm 244–485 tokens no tokenizer; as consultas não excedem o teto dos
modelos. Esse diagnóstico posterior usa apenas tokenização, com resultados em
[token-lengths.json](2026-10-02-sbert-langchain/token-lengths.json).
O MiniLM economizou aproximadamente 940 MiB de pico RSS nesta execução, mas
esse pico inclui bibliotecas e índice, não apenas pesos, e não isola o custo de
LangChain. O payload vetorial é teórico; não é tamanho total do banco.

A indexação BGE foi particularmente cara nesta VM de 3,825 GiB. Inspeções no fim
da etapa e início das consultas encontraram 2.078.040 KiB de RSS no processo,
leitura acumulada de ~7,98 GB e
swap da VM quase cheio. Isso sugere pressão de memória/I/O, sem provar que ela
explique toda a demora. O custo não ocorre a cada mensagem: a aplicação reutiliza
o índice. São execuções únicas de carga/indexação, sem comparação estatística.

As medianas BGE direto por repetição foram 655,04 / 624,23 / 593,84 ms, indicando
variação temporal. Não comparar diretamente esses tempos com os 119 ms históricos
de outro ambiente. As 3.012 consultas medidas concluíram sem erro; quatro chamadas
de aquecimento ficaram fora das métricas. Não houve geração clínica remota.

## O que exatamente foi comparado

O backend **já usa Sentence Transformers**, biblioteca do ecossistema SBERT,
com BGE-M3. SBERT não é uma alternativa única a LangChain: um produz embeddings;
o outro organiza integrações e execução. Avaliamos uma alternativa concreta,
MiniLM multilíngue L12-v2, e uma integração LangChain equivalente à busca atual.

Quatro braços: BGE direto, BGE + LangChain, MiniLM direto e MiniLM + LangChain.
61 fichas idênticas; 251 relatos distintos por conjunto/ID; três repetições por
braço, total realizado 3.012 consultas medidas mais quatro aquecimentos. Os 251
relatos incluem régua 66, dev 47, calibração 16 e independentes 122. Excluímos
casos sem tópico e a prova reservada. Os conjuntos podem compartilhar temas;
não são uma nova amostra clínica certificada.

O [protocolo](2026-10-02-sbert-langchain/protocolo.md) foi escrito antes da
execução. [Insumos](2026-10-02-sbert-langchain/inputs.json), runner, metadados,
resultados individuais, comparação por caso e instruções de reprodução estão na
[pasta da rodada](2026-10-02-sbert-langchain/README.md).

## Relação com medições anteriores

- Em 24/09, o [experimento de embeddings do João](../joao/2026-09-24-17-busca-bge-m3-e-tres-fichas.md)
  já comparou seis modelos. MiniLM teve hit@3 de 45%/38%/41% em dev/calibração/régua,
  contra 96%/94%/91% do BGE. Eram fichas/execução daquela rodada, não um controle
  pareado com o ambiente atual; os tempos históricos de 14/119 ms não são SLA.
- Em 25/09, a [implementação por fichas](../joao/2026-09-25-25-busca-por-fichas-com-bge-m3.md)
  registrou top1/top3 de 107/129 e 123/129 em prova + régua; nos independentes,
  74/122 e 94/122. A [régua salva](../../data/retrieval/cited/20260925-031753_fichas_bge_m3_vector/metrics.json)
  registrou 58/66 no primeiro lugar e 65/66 nos cinco primeiros.
- Os 94,44% da [rodada 24](2026-10-02-24-nova-rodada-vetia.md) são **acerto clínico
  na calibração**, não acerto de recuperação. Esta rodada não reexecuta essa
  classificação nem substitui seu resultado. Também não reavalia as taxas
  clínicas históricas de 89,3%/96,3% em outros conjuntos.

## Limites de interpretação

Encontrar a ficha esperada não garante resposta clínica correta. LangChain não
troca o raciocínio do Gemini quando preservamos a mesma entrada. Não medir LLM
remoto nesta rodada evita misturar fila/retentativas do provedor com custo local,
mas impede afirmar uma nova acurácia clínica ou ganho ponta a ponta.

MiniLM e BGE diferem em arquitetura, pesos e teto de entrada. Todas as fichas
excedem os 128 tokens nativos do MiniLM: isso é um mecanismo plausível de perda,
não demonstração de que todo o efeito é causado pelo truncamento. Não testamos
chunking próprio, fine-tuning ou todos os modelos Sentence Transformers.

Para LangChain, o teste cobre Chroma + RunnableLambda, sem agentes, LangGraph,
tracing remoto, streaming ou persistência de workflows. Variações pequenas de
latência numa máquina compartilhada não estabelecem superioridade do framework.

## Decisões e próximos passos

1. **Manter BGE-M3 na receita atual.** MiniLM perdeu bem mais que os dois pontos
   percentuais permitidos no protocolo, em todos os conjuntos. A vantagem de
   custo não passou no requisito de qualidade. Isso não reprova a biblioteca
   SBERT/Sentence Transformers, que já usamos, nem todos os modelos menores.
2. **Não migrar para LangChain por promessa de desempenho ou acurácia.** A
   integração equivalente não acrescenta informação às fichas nem ao prompt.
   Ela pode justificar-se por uma necessidade concreta de integração, composição
   ou manutenção; essa avaliação de produtividade não foi medida neste benchmark.
3. **Priorizar os gargalos conhecidos do sistema.** A rodada 24 registrou 300 s
   de espera em retentativas após 503. Trocar o organizador do fluxo não resolve
   essa política. Medir limites de espera e comportamento de erro tem prioridade
   sobre uma migração de framework sem benefício demonstrado.
4. **Como próximo experimento de custo, otimizar o modelo atual mantendo a régua.**
   A documentação do Sentence Transformers oferece backends/quantização para
   avaliar; não há ganho garantido neste hardware e modelo. Testar uma opção por
   rodada e revalidar ranks e classificação antes de ativar. Ver
   [documentação oficial](https://www.sbert.net/docs/sentence_transformer/usage/efficiency.html).
5. **Investigar os erros restantes com validação clínica.** Preservar o desempenho
   histórico não elimina os relatos cuja ficha correta fica fora do top 3, nem
   resolve por si só o caso manual que só foi reconhecido após complemento.

Mudanças desta rodada: somente scripts, dados e documentação em `evidencias/vini`.
LangChain foi instalado em venv temporário, e o MiniLM foi baixado no cache de
modelos. Nenhuma dependência foi adicionada ao produto; nenhum índice ativo foi
substituído. Não foi necessário repetir testes de UI/backend sem alteração de
código de aplicação. A validação desta rodada verifica completude dos dados,
equivalência dos braços, estabilidade das repetições e reconstituição das métricas.
