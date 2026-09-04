# Evidências — João Pedro Peterutto · Trilho B2 (Decisão)

Trilho responsável pelo caminho **da evidência recuperada até a resposta**:
geração ancorada nos documentos, classificação estruturada, Chain-of-Thought e
Self-Refine, e a régua de avaliação do sistema (runner de métricas).

Escopo, fronteiras e contratos com os outros trilhos estão em
[`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md).
O padrão destes registros está em [`../README.md`](../README.md).

## Rodadas

| # | Data | Rodada | Resultado |
|---|---|---|---|
| 0 | 03/09 | [Estado inicial](2026-09-03-01-estado-inicial.md) | Marco zero: geração é mock, régua quebrada, baseline de 70,41% não reproduzível |
| 1 | 03/09 | [Higiene do repositório e ambiente](2026-09-03-02-higiene-e-ambiente.md) | 41 arquivos gerados fora do Git; clone limpo sobe; modelo 100% na GPU |
| 2 | 03/09 | [Configuração centralizada](2026-09-03-03-configuracao-centralizada.md) | Mesmo código roda em Docker e local; saída por schema com campos exatos em 8s |
| 3 | 04/09 | [Geração ancorada nos documentos](2026-09-04-04-geracao-ancorada.md) | Mock morto: classificação real com fontes citadas, 43 testes. RAG muda a decisão em 1 dos 3 casos, mas a etapa de consulta erra 1 em 4 execuções |

## Estado atual do trilho

**Funcionando:** ambiente reproduzível em Docker com GPU; configuração
centralizada; triagem real ancorada nos documentos, com fontes citadas e
etapas ligáveis por requisição; 43 testes automatizados.

**Ainda pendente (em ordem):**

1. **Reconstruir a régua** — runner de métricas apontando para o endpoint novo,
   com resultados versionados e manifesto por rodada.
2. **Rodadas de medição** — reproduzir o baseline antigo, fixar a linha de base
   determinística e medir a primeira triagem com RAG ponta a ponta (Marco 1).
3. **Chain-of-Thought e Self-Refine** medidos separadamente.
4. **Driver de ablação** cruzando as chaves de todos os trilhos.

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
