# Evidências — João Pedro Peterutto · Trilho B2 (Decisão)

Trilho responsável pelo caminho **da evidência recuperada até a resposta**:
geração ancorada nos documentos, classificação estruturada, Chain-of-Thought e
Self-Refine, e a régua de avaliação do sistema (runner de métricas).

- **[planejamento.md](planejamento.md)** — o que já foi feito, o que vem a
  seguir e o que está travando.
- [`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md) — escopo
  e fronteiras entre os trilhos.
- [`../README.md`](../README.md) — o padrão destes registros.

## Rodadas

| # | Data | Rodada | Resultado |
|---|---|---|---|
| 0 | 03/09 | [Estado inicial](2026-09-03-01-estado-inicial.md) | Marco zero: geração é mock, régua quebrada, baseline de 70,41% não reproduzível |
| 1 | 03/09 | [Higiene do repositório e ambiente](2026-09-03-02-higiene-e-ambiente.md) | 41 arquivos gerados fora do Git; clone limpo sobe; modelo 100% na GPU |
| 2 | 03/09 | [Configuração centralizada](2026-09-03-03-configuracao-centralizada.md) | Mesmo código roda em Docker e local; saída por schema com campos exatos em 8s |
| 3 | 04/09 | [Geração ancorada nos documentos](2026-09-04-04-geracao-ancorada.md) | Mock morto: classificação real com fontes citadas, 43 testes. RAG muda a decisão em 1 dos 3 casos, mas a etapa de consulta erra 1 em 4 execuções |

## Estado atual

**Etapa 4 de 7.** O produto já classifica de verdade: triagem ancorada nos
documentos, com fontes citadas e etapas ligáveis por requisição, sobre 43
testes automatizados. Falta a régua que transforma isso em número — o runner
de avaliação é a próxima entrega.

O roteiro completo, com marcos e bloqueios, está em
**[planejamento.md](planejamento.md)**.

## Números de referência

Baseline de 04/05/2026, LLM puro, 98 relatos Dog/Cat:

| Métrica | Valor |
|---|---|
| Acurácia | 70,41% |
| Baseline ingênuo (sempre EMERGENCIA) | 72% |
| Recall EMERGENCIA | 91,55% |
| Recall NAO_EMERGENCIA | 14,81% |
| Falsos não urgentes | 4 |

Mover esses números com o RAG é o resultado central do trilho. Duas ressalvas
que acompanham qualquer leitura deles estão registradas no
[estado inicial](2026-09-03-01-estado-inicial.md): a rodada antiga não era
determinística, e no conjunto de avaliação a origem do dado separa
perfeitamente o rótulo.
