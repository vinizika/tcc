# Baselines triviais e o congelamento do lote teste

**Data:** 22/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 13 · **Commit:** este

## O que foi feito

Duas peças pedidas pelo usuário nesta rodada ("passo 1 e 2"):

1. **Congelamento por hash** — construí
   [`scripts/prova_freeze.py`](../../scripts/prova_freeze.py), que calcula um
   hash do split `teste` (todas as colunas, ordenado por `id`) e grava um
   manifesto. `scripts/run_map_triage_eval.py` passou a checar esse
   manifesto automaticamente sempre que `--split teste` é usado — sem
   depender de alguém lembrar de passar uma flag (é a lição do
   [B-39](../backlog.md#b-39), que já registrava esse risco).
2. **Baselines triviais** — construí
   [`scripts/prova_baselines.py`](../../scripts/prova_baselines.py) com os
   três substitutos que a seção 5.4 do plano previa (palavra de alarme,
   comprimento por validação cruzada, saco de palavras Naive Bayes por
   validação cruzada) e rodei contra os 150 casos.

## Por quê

O usuário pediu para seguir com os dois passos, deixando o terceiro (WER
com áudio real) para depois. Os dois fazem sentido nessa ordem: não faz
sentido congelar sem medir primeiro se o conteúdo resiste ao próprio
critério que motivou reescrever a prova (B-05).

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | O hash do congelamento cobre a linha inteira, não só `text`/`expected_class` | Editar até a coluna `note` sem recongelar de propósito já é o tipo de deriva silenciosa que o instrumento existe para impedir |
| 2 | A checagem do runner é automática (sem flag), não opcional | O [B-39](../backlog.md#b-39) já registrava que uma flag opcional "depende de disciplina"; fail-stop automático não depende de ninguém lembrar |
| 3 | Naive Bayes multinomial implementado à mão, sem `scikit-learn` | Mantém a filosofia do projeto de scripts em Python puro (mesmo raciocínio do `capturar_fonte.py`), e evita adicionar uma dependência nova só para um baseline de checagem |
| 4 | Lista de palavras de alarme escolhida por conhecimento geral, antes de rodar qualquer coisa | Se a lista fosse ajustada depois de ver o resultado, a checagem perderia o sentido — mesma disciplina de "resultado esperado antes de medir" |
| 5 | Ao achar duas palavras 100% concentradas numa classe (`agora`, `comendo`), reescrevi o **texto** de 20 casos sem tocar rótulo, espécie ou tópico | É correção de estilo de escrita, não ajuste da chave de resposta — a diferença entre consertar um tique de redação e "decidir no escuro" olhando o resultado |
| 6 | Não continuei reescrevendo palavra por palavra depois da segunda medição | O sinal restante está espalhado por dezenas de palavras funcionais (conectivos, pronomes), não concentrado em alvos fáceis — mais edição viraria otimização contra o próprio baseline, arriscando deixar os textos artificiais |

## Resultado esperado

_Escrito antes de rodar._ Esperava que os dois baselines mais fracos
(palavra de alarme, comprimento) ficassem bem abaixo de 0,90 — são regras
propositalmente simples. Não tinha uma expectativa forte sobre o saco de
palavras: podia ir de qualquer jeito, dependendo de quanto meu próprio
estilo de escrita vazasse entre as classes.

## Resultado obtido

**Antes de qualquer correção, nos 150 casos:**

| Baseline | Acurácia |
|---|---:|
| Palavra de alarme | 0,571 |
| Comprimento do relato | 0,667 |
| Saco de palavras (Naive Bayes) | **0,925** |

O saco de palavras passou do critério do B-05 (abaixo de 0,90). Investigando
por que: duas palavras de conteúdo apareciam 100% concentradas numa classe
só — `"agora"` em 25 casos de emergência (nunca num leve) e `"comendo"` em
13 casos leves (nunca numa emergência). Reescrevi o texto de 20 casos (13
tirando "agora", 7 trocando a frase de tranquilização que usava "comendo"),
sem mudar rótulo, espécie ou tópico de nenhum.

**Depois da correção:**

| Baseline | 150 casos | só `dev` (50) | só `teste` (100) |
|---|---:|---:|---:|
| Palavra de alarme | 0,571 | 0,633 | 0,541 |
| Comprimento do relato | 0,592 | 0,673 | 0,582 |
| Saco de palavras | **0,912** | 0,673 | 0,847 |

Melhora real (0,925 → 0,912), mas **ainda acima de 0,90** no conjunto
combinado — mesmo os dois lotes ficando abaixo quando medidos separados.
Investiguei de novo: as palavras com maior peso agora (`mas`, `se`,
`continua`, `sempre`, `vez`, `pela`, `isso`) são majoritariamente conectivos
e pronomes — sinal de estilo de um autor único, espalhado, não concentrado
em dois ou três alvos como antes. Parei de editar palavra por palavra neste
ponto: a partir daqui, cada correção vira otimização contra o meu próprio
instrumento de medição, o oposto do que ele deveria fazer.

**O que isso significa de verdade.** A prova nova passou de "98 de 98 sem
nenhum modelo" (a antiga) para "precisa de um classificador estatístico
inteiro para chegar em 91%, e mesmo assim não entende nada de veterinária,
só aprendeu o jeito de um autor escrever" — é uma melhora enorme, mas não é
"resolvido". O jeito de resolver de verdade é diversificar quem escreve os
casos, não caçar mais palavras.

**Congelamento:** construí a ferramenta e ela está pronta e testada, mas
**não rodei `--freeze` no split `teste` ainda** — ver "Deixado para depois".

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/prova_baselines.py` | **novo** — os três baselines, módulo puro |
| `scripts/run_prova_baselines.py` | **novo** — CLI que roda os baselines e aplica o critério do B-05 |
| `scripts/prova_freeze.py` | **novo** — calcula/confere o hash de congelamento de um split |
| `scripts/run_map_triage_eval.py` | Checa automaticamente o congelamento quando `--split teste` é usado |
| `scripts/tests/test_prova_baselines.py` | **novo** — 5 testes |
| `scripts/tests/test_prova_freeze.py` | **novo** — 5 testes |
| `data/prova/casos_oficiais.csv` | 20 textos reescritos (sem mudar rótulo/espécie/tópico) |
| `evidencias/backlog.md` | B-05 atualizado com a medição e a recomendação real (diversificar autoria) |

**Verificações:** `scripts/tests` — 171 passaram (as 26 falhas de
`test_capturar_fonte.py` continuam pré-existentes, sem relação com esta
rodada — `trafilatura` ausente no ambiente host). Reconferi duplicidade de
id, reciprocidade de pares, ausência de texto duplicado e consistência de
rótulo contra o mapa depois das reescritas: tudo limpo. Reconferi a
sobreposição contra a base depois das reescritas: continua zero.

## Observações

**Não é um resultado "ruim" — é o resultado certo de ter construído o
instrumento certo.** A prova antiga nunca teve esse tipo de checagem, e
ninguém soube por meses que ela era 98/98 trivial. Descobrir agora, antes de
congelar e antes de gastar a matriz de ablação de outubro nela, é
exatamente para isso que a seção 5.4 do plano pediu este passo.

**O achado é sobre autoria, não sobre os casos em si.** Reli as notas
clínicas de todos os 150 casos e nenhuma delas está clinicamente errada por
causa disso — o problema é de superfície textual (como as frases são
montadas), não de conteúdo (o que elas descrevem).

## Deixado para depois

**A decisão de congelar o `teste` agora, com esta ressalva registrada, ou
esperar uma rodada de diversificação de autoria antes de congelar** — não é
uma decisão técnica, é uma decisão de prioridade do projeto (congelar cedo e
seguir para a matriz de ablação vs. atrasar para fortalecer o instrumento
primeiro). Não congelei sozinho porque essa troca pertence ao time.

**Diversificar autoria dos casos** — pedir para o João, o Vinicius ou um
especialista escreverem uma fração do lote `teste` (ou revisões de
fraseado, mantendo o rótulo) é o que resolveria de verdade, ao contrário de
mais edição palavra por palavra.

## Próximo passo

Depende da decisão acima. Se a decisão for congelar mesmo com a ressalva:
rodar `python scripts/prova_freeze.py --cases data/prova/casos_oficiais.csv
--split teste --freeze` registra o estado atual. Se for diversificar
primeiro: escrever um pedido claro de quantos casos e que critério cada
novo autor deveria seguir (mesma disciplina da muralha).
