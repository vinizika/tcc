# Prova 2: divisão, conferência e congelamento

**Data:** 05/10/2026 · **Trilho:** B1 (Consulta, frente prova) · **Rodada:** 17 · **Commit:** este

## O que foi feito

O [B-63](../backlog.md#b-63) estava sem dono desde 25/09. A frente prova é do
B1 desde 12/09 ([`docs/plano-base-e-prova.md`](../../docs/plano-base-e-prova.md)),
e o Ryu decidiu assumir o que faltava, seguindo **exatamente** a especificação
escrita pelo João na [rodada 20](../joao/2026-09-24-21-prova-2-desenho-e-piloto.md),
sem redesenhar nada:

1. **Divisão por assunto** (decisão 4 da rodada 20): um relato de cada um dos
   61 quadros vai para a calibração e os outros quatro para o teste; dos 25
   especiais, 5 vão para a calibração, na proporção de cada tipo. Total: 66 de
   calibração, 264 de teste.
2. **Conferência do vazamento**, antes de congelar: as medidas de superfície
   que a rodada 20 fez na prova 1 e no piloto, agora na prova 2.
3. **Congelamento por hash** dos dois lotes, com o `prova_freeze.py`.

## Por quê

A prova 2 é de onde sai o número final do TCC (bloqueio 16 do planejamento do
João). Os rótulos já foram validados pela ASAVET (26/09), mas sem a divisão e o
lacre ela não pode ser usada: qualquer medição antes disso arrisca ajustar o
sistema às perguntas da prova. A autópsia 3 (05/10) registrou que "nada andou"
no B-63 desde 26/09.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Qual dos 5 relatos de cada quadro vai para a calibração é decidido por **sorteio determinístico**: ordena os relatos do quadro pelo sha256 de `semente:id` e pega o primeiro. A semente (`prova2-divisao-2026-10-05`) foi fixada **antes** de olhar qualquer resultado | Sorteio reproduzível por qualquer um, sem escolha manual que pudesse favorecer o sistema |
| 2 | Especiais na calibração: 2 de informação insuficiente (de 10), 2 de quadro fora do mapa (de 8), 1 não clínico (de 7) | Os 5 que a especificação pede, divididos na proporção de cada tipo (10:8:7) |
| 3 | A divisão mora no `prova2_montar.py`, e não numa edição à mão do `casos.csv` | O `--check` do montador continua valendo: o arquivo é sempre regenerável a partir dos pedidos, dos relatos e da regra de divisão |
| 4 | Congelar **os dois lotes**, calibração e teste | A calibração é para usar à vontade, mas as linhas dela também não devem mudar sem registro; o runner recusa rodar se o hash mudar |
| 5 | Nenhuma medição de sistema roda no lote teste nesta rodada. As conferências de superfície usam só o texto, a classe e o assunto, como na rodada 20 | O teste roda uma vez, pela configuração final |
| 6 | O "mesmo autor" no top 3 **não** é medido de novo aqui | Já foi medido na prova 2 inteira na rodada 30 do João (ficha certa entre as 3 em 79%, contra 77% dos relatos independentes); refazer agora seria usar o teste à toa |

## Resultado esperado

_Escrito antes de rodar._

**Divisão.** 66 / 264 linhas; cada um dos 61 quadros com exatamente 1 relato na
calibração; especiais 2 / 2 / 1; nenhum id nos dois lotes; a regra
reproduz o mesmo resultado em duas execuções.

**Vazamento** (Naive Bayes só com palavras, nos casos binários; referências da
rodada 20):

| Medida | Referência | Critério para congelar |
|---|---|---|
| (a) Naive Bayes, validação cruzada **por assunto** (nenhum assunto em comum entre treino e teste) | prova 1: 0,79 | **≤ 0,79** — a prova 2 não pode ser mais fácil de adivinhar pelas palavras que a prova 1 |
| (b) Naive Bayes treinado na prova 1 (150 + calibração 18) e aplicado à prova 2 | piloto 0,775; independentes 0,775 | **≤ 0,80** — perto dos relatos de quem não viu o mapa |
| (c) Regra "tem 'mas' ⇒ não emergência" | prova 1: 0,77; piloto: 0,675 | **perto do chute da classe mais comum** (≈ 0,61 = 194/320) — os pedidos controlaram o "mas" em 40% das duas classes |
| (d) Naive Bayes treinado na calibração e aplicado ao teste | — | só registro: a calibração tem ~64 casos binários, pouco para treinar |
| (e) Naive Bayes, validação cruzada aleatória (assunto pode repetir) | prova 1: 0,91 | só registro, para dimensionar quanto vem de assunto repetido |

Se (a), (b) ou (c) falhar, a prova **não** é congelada nesta rodada e o achado
vai ao time.

## Resultado obtido

### Divisão: como especificada

| Lote | Linhas | EMERGENCIA | NAO_EMERGENCIA | INCERTO |
|---|---|---|---|---|
| `calibracao` | 66 | 40 | 24 | 2 |
| `teste` | 264 | 154 | 102 | 8 |

Cada um dos 61 quadros com exatamente 1 relato na calibração; especiais 2 / 2 / 1;
nenhum id nos dois lotes; a mesma divisão em execuções repetidas (teste
automatizado). **Os rótulos não mudaram**: comparando com o arquivo exato que a
ASAVET validou (o `81231b9`, cujo sha256 é o do `validacao.json`), só mudaram as
colunas `marked_by` (rodada 30 do João) e `split` (esta rodada), nas mesmas 330
linhas, na mesma ordem.

### Vazamento: os três critérios passam

Medido com `python scripts/prova2_conferir.py` (Naive Bayes, validação cruzada
5 × 20, nos 320 casos binários; dados em
[`dados/2026-10-05-prova2-conferencia-vazamento.json`](dados/2026-10-05-prova2-conferencia-vazamento.json)):

| Medida | Prova 2 | Critério | Passa? |
|---|---|---|---|
| (a) por assunto | **0,769** (0,747 a 0,794) | ≤ 0,79 | ✅ |
| (b) treinado na prova 1 → prova 2 | **0,781** | ≤ 0,80 | ✅ |
| (c) regra do "mas" | **0,519** (chute: 0,606) | perto do chute | ✅ abaixo do chute |
| (d) treinado na calibração → teste | 0,797 | só registro | — |
| (e) aleatória | 0,867 (0,838 a 0,888) | só registro | — |

**A ressalva, por honestidade.** O critério (a) foi escrito contra o 0,79 que a
rodada 20 mediu na prova 1 com o executor do João. Com o **meu** instrumento,
a prova 1 dá 0,744 (0,695 a 0,781) por assunto: nessa comparação de mesmo
instrumento, a prova 2 fica **2,5 pontos acima** da prova 1, com faixas que se
sobrepõem. Mas as duas provas têm balanços diferentes: chutar a classe mais
comum já acerta 0,606 na prova 2 e 0,524 na prova 1. **Descontado o chute, as
palavras ganham 16 pontos na prova 2 e 22 na prova 1.** Leio isso como a rodada
20 leu o piloto: o que sobra é, em boa parte, vocabulário clínico legítimo
("convulsão", "não consegue respirar"), que **deve** carregar a classe. A pista
de estilo que a rodada 20 achou, o "mas", sumiu: de 0,768 na prova 1 para 0,519
na prova 2, abaixo do chute. E o acerto que vinha de assunto repetido caiu
(aleatória: 0,904 na prova 1, 0,867 na prova 2).

### Congelamento

| Lote | sha256 | Manifesto |
|---|---|---|
| `teste` | `b21b4648c9205dac8df9b29a58bcdd2b2c2fad1faed71533fb79c92da08c5e93` | [`casos.teste.freeze.json`](../../data/prova2/casos.teste.freeze.json) |
| `calibracao` | `44fa0edd515afdbaae4c73149c1b0fdf32c7a106f326de3ea411f3bad5cfd0f8` | [`casos.calibracao.freeze.json`](../../data/prova2/casos.calibracao.freeze.json) |

Conferência logo depois: os dois lotes batem. Contador de uso do `teste`: 0
(no [README da prova 2](../../data/prova2/README.md)).

**Testes:** scripts 198 → 204 passando (6 novos: 3 da divisão, 3 das medidas de
vazamento). As 26 falhas restantes da suíte de scripts nesta máquina são todas
do `test_capturar_fonte.py` e vêm de a biblioteca `trafilatura` não estar
instalada fora do CI; não têm relação com esta rodada.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/prova2_montar.py` | a divisão (`dividir`, `SEMENTE_DIVISAO`) e a contagem por lote na conferência |
| `data/prova2/casos.csv` | coluna `split` preenchida (regerado pelo montador; `--check` limpo) |
| `data/prova2/casos.teste.freeze.json`, `casos.calibracao.freeze.json` | **novos** — os lacres |
| `data/prova2/README.md` | a seção do congelamento, com o contador de uso |
| `scripts/prova_baselines.py` | Naive Bayes por validação repetida (aleatória e por assunto), treino × teste e a regra do "mas" |
| `scripts/prova2_conferir.py` | **novo** — a conferência de vazamento |
| `scripts/prova_freeze.py` | o manifesto grava o caminho com barra normal e o arquivo com LF no Windows ([B-71](../backlog.md#b-71)), como o João teve que corrigir à mão em 25/09 |
| `scripts/tests/test_prova2_montar.py` (novo), `test_prova_baselines.py` | 6 testes |
| `evidencias/ryu/dados/2026-10-05-prova2-conferencia-vazamento.json` | **novo** — os números da conferência |

## Observações

**O caso das passas.** A autópsia 3 apontou que o i58 dos relatos
**independentes** ("pão com passas") está rotulado leve, e passas são tóxicas
para cães. Esse relato não é da prova 2, mas o mesmo quadro ("comeu fora da
dieta") existe nela, e os 5 rótulos dele foram validados pela ASAVET. Não mexi
em nada: mudar rótulo depois do congelamento é decisão explícita do time, com
recongelamento registrado.

**Nenhuma medição de sistema rodou nesta rodada.** O ambiente local (imagem do
backend de 12 dias atrás e um `.env` com os padrões antigos do time, como o
llama e o tradutor ligado) precisa ser atualizado antes; a atualização do
`.env` fica com o Ryu, porque o arquivo guarda as chaves.

## Deixado para depois

- **Medir o lote de calibração** (66) com a configuração de produção (Gemini
  com fichas), o Gemini sem busca (`llm_only`) e, se houver tempo de CPU, o
  `local_qwen`, assim que o ambiente estiver atualizado. É a medição que diz
  se o projeto está andando bem sem tocar no teste.
- **Protocolo da medição final** ([B-77](../backlog.md#b-77)): repetição em
  dias diferentes e um conjunto-sentinela; a tolerância a E→N e E→I decidida
  com os especialistas antes de olhar o resultado (B-63).

## Próximo passo

Atualizar o ambiente e rodar a calibração, com o resultado esperado escrito
antes.
