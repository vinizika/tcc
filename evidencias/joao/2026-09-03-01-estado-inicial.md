# Diário do Trilho B2 — Decisão

Trilho responsável pelo caminho **da evidência recuperada até a resposta**: geração
ancorada, classificação estruturada, CoT e Self-Refine, e a régua de avaliação do
sistema (runner de métricas). Responsável: João Pedro Peterutto.

Escopo e fronteiras estão em [`divisao-de-trabalho.md`](divisao-de-trabalho.md).

## Como registrar uma rodada

Toda rodada de implementação entra aqui, **acrescentando no fim**, neste formato:

```
## [data] · o que mudou
- Intenção: por que fizemos isso
- Resultado esperado: o que achávamos que ia acontecer
- Resultado medido: números da régua compartilhada (antes → depois)
- Leitura: o que aprendemos com a diferença
- Próximo passo: o que isso puxa
```

Três regras para o registro valer:

1. **Número da régua compartilhada, sempre** — sem número, é opinião.
2. **Uma mudança por rodada**, ou o resultado não diz qual mudança causou o quê.
3. **Revisão cruzada na sync semanal** — cada um lê os registros dos outros.

Este diário conta a história das decisões. Ele **complementa** o estudo de ablação
do artigo (a matriz sistemática de componentes ligados/desligados, prevista para
outubro), não o substitui.

---

## 03/09/2026 · Entrada 0 — estado inicial do trilho

Registro do ponto de partida, antes de qualquer mudança de código do B2.

### O que existe hoje

- **A geração é um mock.** `LLMClient.generate` devolve um template fixo com os
  documentos recuperados colados dentro; `LLMClient.self_correct` devolve a
  entrada sem alteração. O `/chat/` responde, mas nada ali é classificação.
- **A classificação real está desligada.** `backend/app/llm.py` tem o prompt que
  produziu os números de 04/05 (JSON com `classificacao`, `justificativa`,
  `sinais_de_alerta`, `recomendacao`), mas o endpoint `/triagem` está comentado
  no `main.py` e esse código nunca usou documentos recuperados — era LLM puro.
- **A régua está quebrada.** `scripts/evaluate_accuracy.py` aponta para
  `POST /triagem`, que não existe mais. Ou seja: os números abaixo não são
  reproduzíveis contra o backend atual.

### Baseline herdado (04/05/2026, LLM puro, sem RAG)

| Métrica | Valor |
|---|---|
| Total avaliado | 98 (Dog/Cat) |
| Acurácia | 70,41% |
| Baseline ingênuo (sempre EMERGENCIA) | 72% |
| Recall EMERGENCIA | 91,55% (65/71) |
| Recall NAO_EMERGENCIA | 14,81% (4/27) |
| Falsos não urgentes | 4 |
| Falsos urgentes | 19 |
| Casos INCERTO | 6 |
| JSON inválido | 0 (depois de `format: json`) |

Ressalva importante: essa rodada usou a temperatura padrão do Ollama (0.8), então
não é determinística — reproduzir vai dar "~70% com ruído", não o número exato.
As rodadas do B2 daqui em diante fixam `temperature=0` e `seed`, registrados no
manifesto de cada rodada.

### Limitação conhecida do conjunto de avaliação

Nas 98 linhas Dog/Cat, a origem do dado separa perfeitamente o rótulo:

| | `original` | `llm_data_augmentation` |
|---|---|---|
| `Dangerous = Yes` (EMERGENCIA) | 71 | 0 |
| `Dangerous = No` (NAO_EMERGENCIA) | 0 | 27 |

Como as 27 não-emergências são exatamente as linhas sintéticas construídas a
partir de 5 sintomas leves (Eye Discharge, Nasal Discharge, Skin Lesions,
Sneezing, Lameness), o recall de NAO_EMERGENCIA mede, na prática, "o modelo
reconhece esse vocabulário de sintomas leves" — e não "o modelo distingue
gravidade em casos variados". **Isso não invalida a métrica**, mas precisa estar
escrito no artigo, e as rodadas do B2 vão reportar as métricas separadas por
`Source` para deixar o efeito visível.

Corrigir isso (ampliar o vocabulário permitido, rotular casos originais como
não urgentes) é decisão do time com a especialista, não do B2 sozinho.

### Outra limitação: base × conjunto de avaliação

A base vetorial tem 7 protocolos sintéticos **em português**; os relatos gerados
para avaliação são listas de sintomas **em inglês** ("Animal: Dog. Sintomas
observados: Fever, Vomiting..."). É provável que, no primeiro teste ponta a
ponta, o RAG mova pouco o número — não por falha da geração, mas porque a
recuperação tem pouco a recuperar. Por isso o runner vai registrar, em cada
linha, o score máximo da recuperação e se algo passou do limiar: assim a
conclusão vira um achado de curadoria para o trilho A, com evidência.

### Próximo passo

E0 (higiene do repositório e ambiente) e E1 (configuração centralizada), para
então matar o mock (E2) e reconstruir a régua (E3). Plano completo do trilho em
`divisao-de-trabalho.md` e no plano de execução do B2.
