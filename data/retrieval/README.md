# Régua de recuperação

Mede uma coisa só: **a busca traz o protocolo certo?**

É a régua do trilho A, e o irmão do runner de `data/evaluation/`. Os dois
medem pedaços diferentes do sistema, e confundi-los leva a conclusões
erradas:

| | `data/evaluation/` | esta pasta |
|---|---|---|
| Testa | O sistema inteiro, do relato à decisão | Só a busca |
| Pergunta | O caso foi classificado certo? | O protocolo certo veio em primeiro? |
| Nota | Acurácia balanceada | Posição: Precision@1, MRR, Recall@5 |
| Casos | 98 listas de sintomas em inglês | 18 relatos de tutor em português |

Sem esta régua, quando a classificação erra com RAG ligado não dá para
saber se a busca trouxe o documento errado ou se o modelo leu mal o
documento certo.

## Como rodar

A API precisa estar de pé com a base indexada:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
python scripts/run_retrieval_eval.py --name minha_rodada \
    --expect-base-hash $(curl -s localhost:8000/health/fingerprint | \
    python -c "import json,sys; print(json.load(sys.stdin)['vector_store']['chunk_ids_sha256'])")
```

Leva segundos: a busca não chama o modelo de linguagem.

| Opção | O que faz |
|---|---|
| `--name` | Sufixo do diretório da rodada |
| `--limiar` | Nota mínima para contar como "trouxe algo relevante". Padrão 0,70, **provisório** — é esta régua que deve dizer o valor certo |
| `--expect-base-hash` | Aborta se a base não for a esperada. **Use em toda rodada que for citada** |

Rodadas vão para `runs/` (fora do Git). As citadas por alguma evidência são
copiadas para `cited/`, como no runner de avaliação.

## Os casos

`cases.csv`, 18 relatos de tutor em português. São os mesmos que o trilho B1
escreveu para medir a transcrição de voz — assim a mesma frase é testada na
voz e na busca.

Cada caso tem uma de três naturezas, e elas **não** se misturam nas contas:

| Natureza | Quantos | O que mede |
|---|---|---|
| **com protocolo** | 9 | A base tem o documento certo. São os que contam para Precision@1, MRR e Recall@5 |
| **caso leve** | 5 | A resposta certa é não trazer protocolo de emergência |
| **sem cobertura** | 4 | É emergência, mas **nenhum protocolo da base trata do assunto** |

A terceira categoria não estava no plano original e existe porque misturá-la
com a segunda confundiria dois diagnósticos: "a busca acertou ao ficar
quieta" e "a base não tem o que buscar". O segundo é dado de curadoria, não
nota da busca. Os quatro casos sem cobertura são, hoje, a lista dos
protocolos que faltam:

| Caso | Quadro | O que faltaria |
|---|---|---|
| b12 | barriga inchada e dura, vômito improdutivo | dilatação-torção gástrica |
| b14 | filhote molinho, não mama, boca fria | hipoglicemia e hipotermia neonatal |
| b15 | cão **macho** urinando gotinhas com dor | obstrução uretral em cães (o protocolo da base é de gatos) |
| b17 | cadela idosa sem levantar as pernas de trás | emergência neurológica |

## O gabarito é provisório

A coluna `marked_by` diz: **marcado pelo trilho B2, aguardando validação do
trilho A**. A régua foi construída pelo B2 porque estava bloqueando dois
trilhos, mas quem decide qual protocolo é o certo para cada relato é quem
cuida da base, com a especialista.

A coluna `note` registra o motivo clínico de cada marcação, para o trilho A
poder discordar de uma linha específica sem refazer o trabalho todo.

Três marcações merecem atenção na validação:

1. **b12 e b15**, marcados como "sem cobertura". No primeiro rascunho eu os
   havia apontado para vômito/diarreia e obstrução urinária. Os dois
   estavam errados, por motivos diferentes: b12 é outro quadro, b15 é a
   espécie errada.
2. **b16** (picada de abelha com edema de face) aponta para dificuldade
   respiratória, por risco de via aérea — e **não** para trauma, porque é
   reação alérgica.
3. **b10** ("manca de leve depois de correr") está como caso leve.

## Como ler o resultado

**Precision@1 é o número principal.** Ele responde: em que fração dos casos
o protocolo certo veio em primeiro lugar? Medir por posição, e não por nota
de semelhança, foi decisão do trilho A e é a certa — a nota deste modelo de
embedding não separa relevância ([B-11](../../evidencias/backlog.md#b-11)).

**"Casos acima do limiar" decide se o resto vale.** Se for zero, a busca não
trouxe nada que ela mesma considere relevante em nenhum caso — e as taxas de
silêncio dos casos leves não medem discernimento, medem acidente. O
relatório avisa isso sozinho.

**A concentração no primeiro lugar** mostra se existe um "protocolo-ímã": um
documento que aparece em primeiro para assuntos que não são dele. Nenhuma
das três métricas clássicas pega isso, porque todas olham o caso e não o
conjunto.

**Compare com o trivial antes de comemorar.** O relatório traz duas
estratégias que não usam busca nenhuma: escolher um documento ao acaso e
responder sempre o mesmo documento. Se a busca não ganhar das duas com
folga, o número não é resultado — é o tamanho da base aparecendo. Na linha
de base: acaso 0,143, sempre o mesmo 0,222, a busca **0,556**.

## O que esta régua ainda não mede bem

A régua está pronta, mas três dos seus números ainda não sustentam
conclusão forte, e é sempre pela mesma razão: **a base tem 7 documentos e o
conjunto tem 18 casos, dos quais 9 entram na conta principal**. Está
registrado como [B-49](../../evidencias/backlog.md#b-49).

| Número | Hoje | O que destrava, e quando |
|---|---|---|
| **Recall@5** | 1,000 — e vale pouco: a busca mostra ~4,4 documentos distintos de uma base de 7, então "o certo está entre os cinco" é quase geométrico | Volta a informar com a base acima de ~20 documentos ([B-03](../../evidencias/backlog.md#b-03)). Só então vale comparar recall entre receitas de chunking |
| **Precision@1** | 0,556 — 5 acertos em 9 casos; um caso move 11 pontos | Com 25–30 casos com protocolo, passa a distinguir diferenças de 5 pontos, e aí dá para medir re-ranking por ele |
| **Taxas de silêncio** | 5/5 e 4/4 — por acidente, já que nenhum caso passa do corte | Passam a medir discernimento quando algum caso passar. É também o que falta para a régua **escolher** o limiar ([B-11](../../evidencias/backlog.md#b-11)) |

Duas capacidades que só chegam com casos novos:

- **Espécie e idade.** Hoje só b15 toca nisso (cão macho com o protocolo de
  gatos na base). Casos que separem cão de gato e filhote de idoso mediriam
  algo que a busca hoje demonstravelmente não faz.
- **Sinais compartilhados.** Relatos cujo sintoma literal aponta para um
  protocolo e cuja causa aponta para outro — como b01, "comeu chocolate" e
  "vomitando". Hoje é um caso; com mais, viraria uma métrica.

**O que já funciona sem base maior:** comparar **duas versões do mesmo
sistema sobre os mesmos casos**. Antes e depois da virada da base, com e sem
re-ranking, com e sem reescrita de consulta. A comparação pareada não
depende do tamanho do acervo, e é para isso que a linha de base foi
congelada agora.

## Comparar duas rodadas

Depois de indexar documentos, a pergunta é sempre a mesma: melhorou, piorou,
ou não mudou?

```bash
python scripts/run_retrieval_eval.py compare <rodada antes> <rodada depois>
```

Sai um `compare__vs_<rodada antes>.md` na pasta da rodada **depois**, com
cinco blocos: **cobertura** (quais quadros do mapa passaram a ter documento
encontrável), **ordenação** (a tabela pareada, caso a caso), **ruído** (o
protocolo-ímã, os casos acima do corte, e se algum caso leve passou a receber
trecho), **gabarito a atualizar** (casos "sem cobertura" cujo assunto entrou
na base) e a **porta de decisão**, com os quatro critérios que saem daqui.

**A comparação é sobre os casos em comum**, não sobre o arquivo inteiro. Cada
lote de fontes traz relatos de régua novos, e travar por hash do `cases.csv`
abortaria em todo lote. O que aborta é um caso em comum ter mudado de texto ou
de gabarito — aí "antes e depois" deixaria de ser sobre a mesma pergunta — e
limiar diferente entre as duas rodadas.

**Diferença aqui é sinal, não ruído.** A régua é determinística: as duas
rodadas de 11/09 (`20260911-201429` e `20260911-202505`), sobre a mesma base,
devolveram posições e notas **idênticas** nos 18 casos. Isso é o contrário do
runner de classificação, onde 2 ou 3 linhas mudam entre sessões por ruído de
GPU ([B-43](../../evidencias/backlog.md#b-43)) e é preciso teste estatístico
para separar as coisas. Aqui um caso que piorou, piorou.

## Estado

A primeira rodada está em `cited/`. A leitura completa está na
[rodada 11 do João](../../evidencias/joao/2026-09-12-11-regua-de-recuperacao.md).
