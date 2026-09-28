# Lote `dev` da prova oficial — 50 casos (entrega 5, parte 1)

**Data:** 21/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 11 · **Commit:** este

## O que foi feito

Escrevi os primeiros 50 casos do lote oficial da prova nova, em
[`data/prova/casos_oficiais.csv`](../../data/prova/casos_oficiais.csv)
(`split=dev`), seguindo o desenho da [seção 5.3 do plano](../../docs/plano-base-e-prova.md#53-o-que-o-time-aprendeu-e-suspeita)
e o mesmo formato do lote de calibração (rodada 4). Usei o mapa de assuntos
completo (61 quadros, hoje todos com fonte aprovada ou encontrada) para
desenhar cobertura e pares de confusão a partir do cenário clínico, nunca da
coluna `sinais_que_o_tutor_relata`.

## Por quê

É a entrega 5 do meu planejamento, e a que o Vinicius pediu explicitamente
no repasse de 20/09 ("priorizar a prova oficial independente"). O lote de
calibração provou o formato em 18 casos; faltava escalar para o tamanho que
o plano pede (~150, aqui a primeira metade).

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Um arquivo só (`casos_oficiais.csv`), com `split` distinguindo `dev`/`teste` | O runner já lê `split` como filtro (rodada 10); um arquivo por split duplicaria a manutenção sem ganhar nada |
| 2 | Cada tópico aparece no máximo uma vez no lote `dev` | Com 61 tópicos e 50 casos, repetir tópico aqui custaria cobertura; o lote `teste` (2x maior) é o lugar de repetir tópico com apresentação diferente |
| 3 | Reaproveitar tópico já usado na calibração, mas nunca o mesmo texto ou a mesma combinação espécie+apresentação | Ex.: `urethral_obstruction` na calibração foi gato; aqui é cão — testa de propósito o gap que a régua achou (b15, cão macho sem documento) |
| 4 | `fora_da_base` do lote de calibração virou `fora_do_mapa` aqui, com critério mais estrito (fora dos 61 quadros, não só sem documento hoje) | O caso "fora da base" da calibração (acidente ofídico) já ganhou fonte aprovada em 20/09 — a `seção 5.3` do plano já avisava que isso aconteceria. `fora_do_mapa` não envelhece: nutrição e calendário vacinal nunca vão virar um dos 61 quadros |
| 5 | Verificação automática de consistência antes de considerar o lote pronto | Script (descartado depois de rodar) conferiu: nenhum id duplicado, todo `confusion_pair_id` existe e é recíproco, nenhum texto duplicado (nem contra a calibração), todo `topic` existe no mapa, e `expected_class`/`expected_urgency`/`species` batem exatamente com `classe`/`urgencia`/`especie` do mapa |

## Resultado esperado

_Escrito antes de rodar qualquer coisa contra a API._ Esperava fechar 50
casos com balanço próximo de 50/50, cobertura de pelo menos 40 dos 61
tópicos, e nenhuma inconsistência nas checagens automáticas.

## Resultado obtido

**Balanço:** 25 EMERGENCIA / 24 NAO_EMERGENCIA / 1 INCERTO — o mais próximo
de 50/50 que o projeto já teve (a prova antiga: 72/28).

**Cobertura:** 47 de 61 tópicos (77%), cada um em exatamente um caso, mais
16 pares de confusão (o dobro dos 7 da calibração) e 3 casos fora do mapa.

**Checagens automáticas:** zero inconsistências — nenhum id duplicado,
todos os pares recíprocos, zero sobreposição de texto (dentro do lote e
contra a calibração), todos os tópicos válidos, zero divergência de
classe/urgência/espécie contra o mapa.

**Verificação informal de separabilidade** (mesma checagem manual da
calibração, agora automatizada): nenhuma palavra de conteúdo aparece
concentrada numa classe só — as únicas palavras que aparecem nos dois lados
em quantidade são preposições e outras palavras funcionais do português, o
esperado.

**Fumaça contra a API real** (5 primeiros casos, `--mode no_rag`, coleção
ativa vazia — só valida o encanamento, não é medição): 3 de 5 corretos. Os
dois erros (`p20`, intoxicação por cebola com gengiva pálida → classificado
NAO_EMERGENCIA; `p22`, primeira convulsão → classificado NAO_EMERGENCIA) são
achados genuínos do LLM puro sem RAG, não bugs do lote — mas a amostra é
pequena demais (5 casos, sem nenhum caso leve) para significar qualquer
coisa. Registro aqui só para não perder o dado; a leitura de verdade espera
o lote completo.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/prova/casos_oficiais.csv` | **novo** — 50 casos, `split=dev` |
| `data/prova/README.md` | Reestruturado para descrever os dois arquivos (`casos_calibracao.csv` e `casos_oficiais.csv`); nova seção documentando o lote `dev`; `fora_da_base` documentado como substituído por `fora_do_mapa` |
| `data/evaluation/prova_runs/20260921-210543_smoke_prova_dev/` | Rodada de fumaça, 5 casos |
| `evidencias/ryu/planejamento.md` | Entrega 5 marcada "em andamento" |

## Observações

**O script que gerou o CSV foi descartado depois de rodar** (era só uma
forma segura de escrever texto em português com vírgulas/acentos num CSV
sem erro de escaping manual) — o raciocínio de cada caso já está na coluna
`note`, que é o que fica versionado.

**Não fiz o passo automático de sobreposição de texto contra
`backend/data/documents/`** (regra 4 da muralha) — ainda não escrevi esse
verificador, e ele importa mais quando o lote `teste` for congelado do que
agora, no `dev`, que por definição não congela. Fica registrado como
pendência real antes de fechar o `teste`.

**Reli o mapa de assuntos inteiro para desenhar este lote — não abri
nenhuma fonte (`data/curadoria/fontes/`) nem documento
(`backend/data/documents/`)**, mantendo a mesma muralha da calibração.

## Deixado para depois

**O verificador de sobreposição de texto contra a base** — precisa existir
antes do lote `teste` congelar.

**O lote `teste`** (~100 casos) — cobre os 14 tópicos que o `dev` não
tocou (inclui `pyometra`, deslocado de propósito para cá desde a calibração
já ter esse par) e repete tópicos já vistos com apresentação e espécie
diferentes.

**Baselines triviais novos** (saco de palavras, palavra de alarme,
comprimento) — esperam o lote completo (~150) para terem amostra suficiente.

## Próximo passo

Escrever o lote `teste`.
