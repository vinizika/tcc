# Régua de recuperação — 20260911-202505_linha_de_base

**Quando:** 2026-09-11T20:25:05.973047-03:00 · **commit:** `74c6dfa`

Mede se a busca traz o protocolo certo, por **posição**. Não mede classificação — para isso é o runner de `data/evaluation/`.

## Resultado

| Métrica | Valor |
|---|---|
| **Protocolo certo em 1º** (Precision@1) | 0.556 (9 casos com protocolo na base) |
| Posição média invertida (MRR) | 0.698 |
| Protocolo certo entre os 5 (Recall@5) | 1.000 |
| Casos com algum trecho acima de 0.70 | 0.000 |
| Nota máxima média | 0.5036 |

### Quando a resposta certa é não trazer nada

| Natureza | Casos | Busca ficou quieta |
|---|---|---|
| Caso leve | 5 | 1.000 |
| Sem cobertura na base | 4 | 1.000 |

### O número é bom? Comparado com o quê

| Estratégia | Protocolo certo em 1º |
|---|---|
| Escolher um documento ao acaso | 0.143 |
| Responder sempre o mesmo documento | 0.222 |
| **A busca** | **0.556** |

> **Cuidado ao ler o Recall.** A busca mostra em média 4.4 documentos distintos por caso, e a base tem 7 documentos no total. Com um acervo pequeno, "o certo está entre os primeiros" é quase geométrico — a métrica só passa a informar quando a base crescer.

> **Atenção: a busca não passou do corte em nenhum caso.** O silêncio acima não é mérito — ela está sempre quieta, e "acerta" os casos leves por acidente. Enquanto este número for zero, as taxas de silêncio não medem discernimento.

### Concentração no primeiro lugar

O protocolo **trauma_and_bleeding** aparece em 1º lugar em **9 de 18** casos (0.500). Um documento que atrai consultas de assuntos que não são dele é o mecanismo do [B-02](../../evidencias/backlog.md#b-02).

| Protocolo em 1º | Casos |
|---|---|
| trauma_and_bleeding | 9 |
| urethral_obstruction | 4 |
| vomiting_and_diarrhea | 3 |
| respiratory_distress | 1 |
| allium_toxicosis | 1 |

## Caso a caso

| Caso | Natureza | Esperado | 1º lugar | Posição | Nota máx. |
|---|---|---|---|---|---|
| b01 | com protocolo | chocolate_toxicosis | vomiting_and_diarrhea | 5 | 0.441 |
| b02 | com protocolo | urethral_obstruction | urethral_obstruction | 1 | 0.533 |
| b03 | com protocolo | respiratory_distress | respiratory_distress | 1 | 0.516 |
| b04 | com protocolo | seizures | trauma_and_bleeding | 4 | 0.559 |
| b05 | caso leve | — | urethral_obstruction | — | 0.504 |
| b06 | com protocolo | trauma_and_bleeding | trauma_and_bleeding | 1 | 0.563 |
| b07 | com protocolo | vomiting_and_diarrhea | vomiting_and_diarrhea | 1 | 0.556 |
| b08 | com protocolo | allium_toxicosis | vomiting_and_diarrhea | 2 | 0.442 |
| b09 | caso leve | — | trauma_and_bleeding | — | 0.518 |
| b10 | caso leve | — | trauma_and_bleeding | — | 0.514 |
| b11 | caso leve | — | urethral_obstruction | — | 0.460 |
| b12 | sem cobertura | — | trauma_and_bleeding | — | 0.562 |
| b13 | com protocolo | trauma_and_bleeding | trauma_and_bleeding | 1 | 0.429 |
| b14 | sem cobertura | — | allium_toxicosis | — | 0.376 |
| b15 | sem cobertura | — | trauma_and_bleeding | — | 0.600 |
| b16 | com protocolo | respiratory_distress | trauma_and_bleeding | 3 | 0.458 |
| b17 | sem cobertura | — | trauma_and_bleeding | — | 0.546 |
| b18 | caso leve | — | urethral_obstruction | — | 0.489 |

---

Gabarito marcado pelo trilho B2, **provisório**, aguardando validação do trilho A. Ver `data/retrieval/README.md`.
