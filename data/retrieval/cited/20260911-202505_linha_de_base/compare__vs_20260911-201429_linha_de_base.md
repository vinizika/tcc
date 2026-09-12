# Comparação da régua — 20260911-202505_linha_de_base

**Antes (A):** `20260911-201429_linha_de_base` · 2026-09-11T20:14:29.827464-03:00 · commit `74c6dfa`

**Depois (B):** `20260911-202505_linha_de_base` · 2026-09-11T20:25:05.973047-03:00 · commit `74c6dfa`

Corte de relevância: 0.7 · 18 casos em comum

## O que mudou na base

| | Antes | Depois |
|---|---|---|
| Trechos indexados | 18 | 18 |
| Recorte (`chunk_ids_sha256`) | `eeba9f51d239` | `eeba9f51d239` |
| Conteúdo (`content_sha256`) | `89a215ac3c7c` | `89a215ac3c7c` |

> **Nenhum documento entrou entre as duas rodadas.** O recorte da base é o mesmo, então esta comparação mede o **instrumento**, não uma mudança de curadoria: tudo abaixo deve dar zero. A régua é determinística, e qualquer diferença aqui seria defeito do compare ou da rodada.

## 1. Cobertura — quais quadros têm documento encontrável

**Encontrável** quer dizer que o assunto apareceu entre os cinco trechos devolvidos em algum caso. Um documento indexado que nunca aparece é cobertura no papel: entrou na base e não muda a resposta de ninguém.

| | Antes | Depois |
|---|---|---|
| Quadros encontráveis (de 61) | 7 | 7 |
| Na etapa 1 (de 31) | 7 | 7 |

Nenhum quadro mudou de estado.

> **Espécie divergente entre a ficha e o mapa** — é o que o caso b15 da régua ensinou a olhar (protocolo de gato, caso de cão):

> - `chocolate_toxicosis`: o mapa diz *cao*, a ficha diz *ambos*

## 2. Ordenação — onde cada caso foi parar

| Métrica | Antes | Depois | Δ |
|---|---|---|---|
| Protocolo certo em 1º | 0.556 | 0.556 | +0.0000 |
| Posição média invertida (MRR) | 0.698 | 0.698 | +0.0000 |
| Certo entre os cinco | 1.000 | 1.000 | +0.0000 |

**0 melhoraram · 0 pioraram · 9 iguais**

Nenhum caso mudou de posição.

## 3. Ruído — o que a base nova empurrou para dentro

| | Antes | Depois | Δ |
|---|---|---|---|
| Protocolo-ímã | trauma_and_bleeding (0.500) | trauma_and_bleeding (0.500) | +0.0000 |
| Casos acima do corte | 0.000 | 0.000 | +0.0000 |

### Casos leves — a nota máxima subiu?

| Caso | Antes | Depois | 1º lugar agora | |
|---|---|---|---|---|
| b05 | 0.504 | 0.504 | urethral_obstruction |  |
| b09 | 0.518 | 0.518 | trauma_and_bleeding |  |
| b10 | 0.514 | 0.514 | trauma_and_bleeding |  |
| b11 | 0.460 | 0.460 | urethral_obstruction |  |
| b18 | 0.489 | 0.489 | urethral_obstruction |  |

### Casos sem cobertura na base — a nota máxima subiu?

| Caso | Antes | Depois | 1º lugar agora | |
|---|---|---|---|---|
| b12 | 0.562 | 0.562 | trauma_and_bleeding |  |
| b14 | 0.376 | 0.376 | allium_toxicosis |  |
| b15 | 0.600 | 0.600 | trauma_and_bleeding |  |
| b17 | 0.546 | 0.546 | trauma_and_bleeding |  |

> **Nenhum caso leve recebeu trecho acima do corte — mas nenhum caso recebeu.** Enquanto a busca não passar do corte em caso nenhum, este silêncio é acidente, não discernimento. É a mesma ressalva que o `report.md` da régua emite sozinho.

## 4. Gabarito a atualizar

Nenhum caso precisa de revisão de gabarito.

## 5. A porta de decisão

Os critérios de `data/curadoria/README.md` que saem deste arquivo:

| Eixo | Valor | Limite | |
|---|---|---|---|
| Ordenação | 0 pioraram, 0 melhoraram | pioraram ≤ melhoraram | passa |
| Ímã | trauma_and_bleeding em 50% dos casos | nenhum documento em 1º em mais de 1/3 | **não passa** |
| Ruído nos leves | 0 caso(s) leve(s) acima do corte | nenhum | passa |
| Cobertura real | nenhum assunto novo nesta comparação | ≥ 70% dos quadros novos | passa |

Os outros dois critérios não vêm daqui: **velocidade** sai da coluna `cobertura` do mapa de assuntos, e **classificação** sai de uma rodada do runner de `data/evaluation/`.

---

### Como ler este arquivo

- **A régua é determinística.** Duas rodadas sobre a mesma base devolvem posições e notas idênticas, então aqui diferença é sinal — não ruído de sessão, ao contrário do runner de classificação.
- **Um caso vale 0.111 da Precision@1.** Com poucos casos com protocolo, uma linha move muito: leia a tabela pareada antes da média.
- **A comparação é sobre os casos em comum**, não sobre o arquivo inteiro. Cada lote de fontes traz relatos novos, e travar por hash do `cases.csv` abortaria sempre; o que aborta é um caso em comum ter mudado de texto ou de gabarito.
- **A espécie vem das fichas de hoje**, não das de cada rodada: `backend/data/documents/*.json` é lido no momento da comparação.
- **Espécies normalizadas** (as fichas usam mais de uma grafia, B-53): cats → gato; dog → cao; dogs_and_cats → ambos.
