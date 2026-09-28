# Lote `teste` da prova oficial + verificador de sobreposição (entrega 5, parte 2)

**Data:** 22/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 12 · **Commit:** este

## O que foi feito

Duas peças que fecham a entrega 5:

1. **O lote `teste`**: 100 casos novos em `data/prova/casos_oficiais.csv`
   (`split=teste`), completando os ~150 do plano junto com o lote `dev`
   (rodada 11). Cobrem os 14 tópicos que o `dev` ainda não tinha tocado e
   repetem boa parte dos outros com espécie, idade ou apresentação
   diferente — inclusive casos de segunda profundidade que testam nuance
   fina (duração de crise convulsiva num cão já epiléptico; apetite
   reduzido bem na fronteira das 24h que o próprio mapa usa como corte para
   gato adulto).
2. **O verificador automático da regra 4 da muralha**:
   [`backend/app/database/check_prova_overlap.py`](../../backend/app/database/check_prova_overlap.py),
   que compara os casos da prova contra os chunks reais da base por
   sobreposição de sequências de palavras — a peça que faltava desde a
   rodada 11.

## Por quê

A entrega 5 pedia ~150 casos, dev+teste, com o passo de sobreposição
rodado antes de considerar o lote pronto para congelar. A rodada 11
entregou só a metade e deixou o verificador como pendência explícita.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Verificador compara contra os **chunks já extraídos na coleção do ChromaDB**, não reabre os PDF/TXT originais | Reaproveita a extração e limpeza que o ingestor do trilho A já fez (remoção de cabeçalho, rodapé, seções inúteis); reimplementar extração de PDF só para este checker duplicaria trabalho e poderia divergir do que o sistema realmente indexa |
| 2 | Comparação por n-grama de 6 palavras, não por frase inteira nem por palavra isolada | Frase inteira é frágil a qualquer diferença de pontuação; palavra isolada gera falso positivo o tempo todo (qualquer termo clínico comum apareceria). Seis palavras seguidas em comum entre um relato de tutor e um artigo científico não acontece por acaso |
| 3 | Alguns pares de confusão do lote `teste` apontam para casos do lote `dev` (ex.: `p77` ↔ `p47`) | O mapa de assuntos não faz distinção entre lotes ao definir pares — usar um caso já escrito é mais honesto que forçar uma repetição só para manter os dois lados no mesmo split |
| 4 | Registrar o achado de separabilidade parcial (`"agora"`/`"repente"` só em emergência, `"comendo"` só em não emergência) em vez de reescrever os casos para escondê-lo | Reescrever agora seria decidir no escuro, sem o baseline formal medido; o registro serve de aviso para quando os baselines triviais (seção 5.4 do plano) forem construídos |

## Resultado esperado

_Escrito antes de rodar as verificações._ Esperava fechar 150 casos com
cobertura total do mapa (61/61), balanço próximo de 50/50, e zero problemas de
sobreposição contra a base — mas sem expectativa de que o baseline informal
de separabilidade desse "limpo" feito à mão numa segunda passada, já que a
amostra maior (150 vs. 50) dá mais chance de um tique de escrita se repetir
o suficiente para aparecer.

## Resultado obtido

**Balanço final (150 casos):** 77 EMERGENCIA / 70 NAO_EMERGENCIA / 3
INCERTO — 51%/47%/2%.

**Cobertura: 61 de 61 tópicos do mapa**, todos com pelo menos um caso.

**23 pares de confusão**, todos reciprocamente consistentes (verificado por
script: se `A` aponta para `B`, `B` aponta de volta para `A`).

**Zero problemas em todas as checagens automáticas:** nenhum id duplicado,
nenhum par quebrado, nenhum texto duplicado (nem entre lotes, nem contra a
calibração), todo tópico existe no mapa, toda combinação
classe/urgência/espécie bate exatamente com o mapa. Duas divergências foram
encontradas e corrigidas no processo (`p83` usava gato para um tópico que o
mapa restringe a cão; `p142` tinha a urgência esperada errada) — é
exatamente o tipo de erro que a checagem automática existe para pegar antes
de alguém confiar no gabarito.

**Verificador de sobreposição:** `nenhum dos 150 casos compartilha 6-grama
com a base (3.481 chunks)` — regra 4 da muralha cumprida.

**Achado honesto de separabilidade parcial:** `"agora"` e `"repente"`
aparecem em 25 e 10 casos de emergência e nunca num caso leve;
`"comendo"` aparece em 13 casos leves e nunca numa emergência. Duas dessas
palavras têm justificativa clínica real (início súbito é discriminador do
MSD; "comendo normal" é a frase padrão de tranquilidade), mas um baseline de
saco de palavras vai conseguir usar isso como atalho. Não reescrevi os casos
para esconder o padrão — o critério que decide se isso é problema é o do
B-05 (baseline abaixo de 0,90), que só pode ser medido depois que os
baselines novos existirem.

**Fumaça contra a API** (3 primeiros casos do split `teste`, `--mode
no_rag`): confirma que o filtro `--split teste` funciona e le os casos
certos — não é medição.

**Testes:** 3 novos (`test_check_prova_overlap.py`, lógica pura de
normalização e n-grama). Suíte do backend: 226 → **229**.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/prova/casos_oficiais.csv` | +100 casos (`split=teste`); 2 correções de rótulo nos casos já existentes |
| `backend/app/database/check_prova_overlap.py` | **novo** — verificador de sobreposição de texto (regra 4 da muralha) |
| `backend/tests/test_check_prova_overlap.py` | **novo** — 3 testes da lógica pura |
| `data/prova/README.md` | Nova seção documentando o lote `teste`, o verificador, e o achado de separabilidade |
| `data/evaluation/prova_runs/` | Rodada de fumaça do split `teste` |

## Observações

**Os dois scripts que geraram os CSVs foram descartados depois de rodar**,
mesmo padrão da rodada 11 — o raciocínio de cada caso está na coluna `note`,
que fica versionada.

**Não abri nenhuma fonte nem documento da base para escrever os 100 casos
novos** — só o mapa de assuntos, mantendo a muralha da rodada 11.

**A prova ainda não está congelada por hash.** As checagens automáticas
estão limpas, mas falta uma decisão explícita de congelar — depois disso,
nenhuma linha do `teste` pode ser reescrita mesmo que o sistema erre nela
(é a proteção contra "mover a trave depois do chute" que o plano descreve).

## Deixado para depois

**Congelar o `teste` por hash** — decisão pendente, não bloqueada
tecnicamente.

**Baselines triviais novos** (saco de palavras com validação cruzada,
palavra de alarme, comprimento) — agora há amostra suficiente (150 casos).
É o item que vai dizer se `"agora"`/`"comendo"` são só uma curiosidade ou um
problema de verdade.

**Rodar o lote completo contra a API com RAG ligado**, quando a coleção do
trilho A for ativada — hoje qualquer rodada contra a API real usa a coleção
legada vazia.

## Próximo passo

Com a entrega 5 substancialmente completa, meus itens abertos voltam a ser
o benchmark de WER com áudio real (B-13, item 11 do planejamento) e a
decisão de congelamento do `teste`.
