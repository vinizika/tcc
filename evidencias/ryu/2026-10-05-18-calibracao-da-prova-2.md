# Prova 2: primeira medição, no lote de calibração

**Data:** 05/10/2026 · **Trilho:** B1 (Consulta, frente prova) · **Rodada:** 18 · **Commit:** este

## O que foi feito

Primeira medição do sistema na prova 2, **só no lote `calibracao`** (66
relatos: 40 emergências, 24 não emergências, 2 incertos), congelado na
[rodada 17](2026-10-05-17-prova-2-divisao-e-congelamento.md). O lote `teste`
não é tocado. Os braços:

| Braço | Preset | O que mostra |
|---|---|---|
| Produção | `producao` | o sistema como está: relato cru, bge-m3 nas 61 fichas, 3 fichas sem porta, Gemini decide |
| Gemini sem busca | `llm_only` | se as fichas ajudam o Gemini |
| Atendente antigo | `local_llama` | referência do llama3.2:3b (o atendente até 24/09) com a base nova |
| Modelo local | `local_qwen` | a alternativa local, se o `qwen3:8b` estiver baixado |

## Por quê

O Ryu pediu, depois de congelar a prova, "as medidas necessárias para ver se o
projeto está andando bem". O lote de calibração existe para isso: dá para
medir quantas vezes for preciso sem gastar o teste, que roda uma vez, pela
configuração final.

## Resultado esperado

_Escrito antes de rodar._ As referências são os relatos independentes (122,
autores que não viram o mapa) da [rodada 26 do João](../joao/2026-09-25-27-atendente-gemini-e-replica.md)
e da autópsia 3: Gemini em produção 6 de 76 emergências perdidas e 3 de 38
falsos alarmes; Gemini sem busca 5 e 10; llama perde 40 de 76. A prova 2 deve
ser mais difícil que os independentes (76 das 194 emergências contadas com
calma; ficha certa em 1º lugar em 54% contra 61%, rodada 30 do João).

Semântica da autópsia: **emergência perdida** = EMERGENCIA prevista como
NAO_EMERGENCIA **ou** INCERTO; **falso alarme** = NAO_EMERGENCIA prevista
como EMERGENCIA.

| Braço | Emergências perdidas (de 40) | Falsos alarmes (de 24) |
|---|---|---|
| Produção | ≤ 4 | ≤ 3 |
| Gemini sem busca | parecido com a produção | **mais** que a produção (≈ 6) |
| llama | muitas (≈ 20) | — |

**Critério de "o projeto está andando bem":** a produção perde **no máximo 4
das 40 emergências** (10%), **não perde mais** que o Gemini sem busca, e dá
**menos falsos alarmes** que ele. Ressalva escrita antes: com 40 emergências,
cada caso vale 2,5 pontos; isto é uma checagem de rumo, não o número do TCC.

## Resultado obtido

O `qwen3:8b` não está baixado nesta máquina (sem placa de vídeo, ~34 s por
caso): o braço local ficou de fora. Os outros três rodaram inteiros, 66/66
linhas com status `ok`, contra a API reconstruída da `main` de 05/10
(`698da6a` + as mudanças da rodada 17), com a mesma identidade de versão da
autópsia 3 (coleção `…280baf13`, bge-m3, `vector`, corte 0, Gemini sem troca,
tradutor desligado).

| Braço | Emergências perdidas (de 40) | Falsos alarmes (de 24) | Leve → INCERTO | INCERTO certos (de 2) | Mediana / p95 por caso |
|---|---|---|---|---|---|
| **Produção** (Gemini + fichas) | **0** | **1** (q118) | 1 (q186) | 2 | 4,1 s / 15,0 s |
| Gemini sem busca | **0** | **0** | 0 | 2 | 4,0 s / 5,4 s |
| llama + fichas | 3 | **9** | 0 | 0 | 33,4 s / 106,1 s |

Busca (produção e llama, mesma busca): ficha certa em 1º lugar em **37 de 61**
relatos com quadro do mapa (61%) e entre as 3 em **50 de 61** (82%), perto do que
a rodada 30 do João mediu na prova 2 inteira (54% · 79%).

Rodadas citadas:
[`20261005-224021_r18_gemini_calib`](../../data/evaluation/cited/20261005-224021_r18_gemini_calib/report.md) ·
[`20261005-224914_r18_gemini_sem_busca_calib`](../../data/evaluation/cited/20261005-224914_r18_gemini_sem_busca_calib/report.md) ·
[`20261005-225812_r18_llama_calib`](../../data/evaluation/cited/20261005-225812_r18_llama_calib/report.md).
Comando: `python scripts/run_evaluation.py --api-url http://127.0.0.1:8000 --cases data/prova2/casos.csv --split calibracao --preset <producao|llm_only|local_llama>`.

### Contra o critério escrito antes

| Parte do critério | Resultado | |
|---|---|---|
| Produção perde no máximo 4 das 40 emergências | 0 | ✅ |
| Produção não perde mais que o Gemini sem busca | 0 contra 0 | ✅ |
| Produção dá menos falsos alarmes que o Gemini sem busca | 1 contra 0 | ❌ |

**O critério não passa inteiro**, e o resultado esperado para o Gemini sem
busca estava errado: eu esperava uns 6 falsos alarmes (pela proporção dos
relatos independentes) e ele não errou nenhum dos 66. A diferença entre
produção e sem busca são **2 casos em 66** (q118 e q186), pouco para
afirmar qualquer coisa (McNemar com 2 casos discordantes: p = 0,5). O que a
medição mostra é que **na calibração as fichas não ajudam o Gemini**, e não que
atrapalham.

### Os dois erros da produção

- **q118 — leve virou EMERGENCIA, com a ficha certa em 1º.** Cachorro brigou com
  gambá, "furinho" na orelha que parou de sangrar, comendo e brincando, vacina
  vencida. O Gemini leu a ficha de raiva e subiu a urgência. É o mesmo padrão do
  i40 ("morcego", leve → EMERGENCIA) que a autópsia 3 registrou: vale olhar o
  texto de leitura da ficha de raiva na rodada 32 do João ([B-61](../backlog.md#b-61)).
- **q186 — leve virou INCERTO, com as 3 fichas erradas.** Cadela de 8 meses no
  primeiro cio, tutora aflita ("sangue", "inchada"). A busca trouxe ferida leve,
  trauma e sangramento, e obstrução uretral; a ficha do cio não veio. Sem busca, o
  Gemini acertou. É exatamente o erro que o [B-70](../backlog.md#b-70) descreve
  (ficha de outro assunto ⇒ INCERTO), e o argumento a favor de um Self-Refine que
  confira se a ficha é do assunto do relato.

### O llama mostra que a prova não é fácil para qualquer um

O llama erra 12 de 64 casos binários, e erra pelo **tom**: 6 dos 8 relatos leves
contados com aflição viraram EMERGENCIA, e 2 das 3 emergências perdidas eram
contadas com calma. É a armadilha que a prova 2 foi desenhada para armar
(rodada 20 do João), e ela funciona. O que o Gemini acerta não vem de a prova
ser trivial.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/evaluation/cited/20261005-*_r18_*` | **novas** — as três rodadas citadas (conferido: a chave do Gemini não aparece em nenhum arquivo) |
| esta evidência | — |

## Observações

**1. A calibração é fácil para o Gemini, e isso tem consequência.** Com 0
emergências perdidas nos dois braços do Gemini, a calibração não tem poder para
separar "com fichas" de "sem fichas". O lote `teste` (264, 154 emergências)
tem quatro vezes mais casos, mas, se a taxa de erro for parecida, ainda pode ficar
perto do chão. A comparação final entre braços bons precisa de McNemar pareado e
intervalo de confiança declarados antes, como o B-66 já pede, e de repetição em
dias diferentes (B-77).

**2. Os relatos independentes contavam outra história.** Lá, as fichas cortaram
os falsos alarmes do Gemini de 10 para 3. Aqui, sem busca ele já dá 0. Duas
leituras possíveis, que esta rodada não separa: o Gemini mudou entre 25/09 e
hoje (o B-77 mostrou que ele muda), ou a prova 2 está mais "limpa" que os
independentes para um modelo grande. Separar as duas pede rodar os
independentes sem busca de novo, no mesmo dia. Fica registrado, não feito.

**3. Efeito colateral conhecido ([B-73](../backlog.md#b-73)).** Abrir a base
alterou os arquivos versionados de `backend/chroma_db/`; desfeito com
`git checkout` depois das rodadas, com o backend parado.

**4. Ambiente.** Antes desta rodada o backend local rodava uma imagem de 12 dias
atrás e um `.env` com os padrões antigos; o Ryu trocou o `.env` pelo
`.env.example` e as imagens foram reconstruídas. O primeiro `/chat/` levou 3
minutos (carga do bge-m3), e o container precisou ser recriado uma vez para ler a
chave do Gemini.

## Deixado para depois

- **Braço local (`local_qwen`)**: o `qwen3:8b` foi baixado em 06/10 (digest
  `500a1f06`, o mesmo da rodada 25 do João), mas **não roda nesta máquina**: o
  Ollama morreu por falta de memória já no aquecimento ("llama-server process
  has terminated: signal: killed"). A máquina tem 7,7 GB de RAM e o Docker
  recebe 3,7 GB; o qwen sozinho pede ~5,5 GB, além do bge-m3 no backend (~2 GB).
  Fica para quem tem placa de vídeo (o João mediu o qwen numa).
- **Repetir os dois braços do Gemini em outro dia**, no mesmo lote, como pede o
  [B-77](../backlog.md#b-77): mede quanto ele varia aqui.
- **Os independentes sem busca, hoje** (observação 2).

## Próximo passo

Levar ao time: a calibração passou na segurança (zero emergências perdidas), mas
mostrou que, para o Gemini, as fichas não fazem diferença nestes 66 casos. Isso
pesa na decisão sobre o Self-Refine (q186) e na rodada 32 do João (q118).
