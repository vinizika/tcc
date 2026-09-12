# Curadoria da base: o mapa de assuntos

Uma planilha com os quadros clínicos que a base de conhecimento deve cobrir e
sobre os quais a prova deve perguntar. É a peça comum das duas frentes do
[plano](../../docs/plano-base-e-prova.md): sem ela, a busca por fontes não
tem critério, o `compare` não tem definição de cobertura, e base e prova
voltam a não se encaixar — que é o problema de hoje.

```
data/curadoria/
├── mapa-de-assuntos.csv       <- o mapa: 61 quadros, um por linha
├── referencias.md             <- as fontes que sustentam cada linha, com o grau de verificação
├── vocabulario-dataset1.csv   <- cada sinal do conjunto de avaliação → linha do mapa, ou "inespecifico"
├── doencas-dataset2.csv       <- cada doença do dataset2 → linha do mapa, ou excluída com motivo
└── fontes/                    <- (etapa seguinte) uma lista de fontes por quadro, do pesquisador
```

Parece burocracia e não é. O mesmo arquivo é cinco coisas:

| Uso | Quem lê |
|---|---|
| **A análise do que falta** na base — o insumo do pesquisador | agente pesquisador |
| **A lista de tarefas**: cada linha é uma busca de fonte | quem estiver trabalhando na base |
| **O painel de progresso**: a coluna `cobertura` diz onde a base está | o time, e o `compare` do agente 2 |
| **O que os especialistas validam primeiro**: 61 linhas em uma sentada, antes de qualquer documento | especialistas |
| **A tabela do artigo**: "o sistema cobre estes quadros, escolhidos por isto" | a escrita |

## Como o mapa foi construído

Em 12/09, pelo roteiro do [cartógrafo](../../agentes/cartografo.md). O esqueleto veio de referência publicada, não dos datasets: a tabela de três níveis do MSD Veterinary Manual para tutores, a *Veterinary Triage List*, a casuística de 3.180 atendimentos de emergência (Lee 2014) e as casuísticas brasileiras de intoxicação e de doenças infecciosas. Tudo em [`referencias.md`](referencias.md), com o grau de verificação de cada fonte — o que foi lido de verdade, o que veio de resumo e o que estava bloqueado.

Os datasets do Kaggle entraram só como **checagem**: no `dataset1`, todas as 70 linhas de cão e gato são "perigosas" e nenhuma nomeia um quadro — além de ser a prova atual, o que faria a base ser montada olhando a chave de resposta. No `dataset2`, 48 doenças quase todas infecciosas ou crônicas, sem uma emergência clássica. A checagem está nos dois CSVs: dos 194 termos do conjunto de avaliação, 162 caem em alguma linha e 32 são inespecíficos (febre, dor, cansaço — sinais que sozinhos não apontam quadro); das 48 doenças, 34 têm linha e 14 ficaram de fora com motivo.

A leitura completa — o que a pesquisa mudou no desenho, o que não foi possível verificar, as linhas mais contestáveis — está na [rodada 11 do João](../../evidencias/joao/2026-09-12-12-mapa-de-assuntos.md).

## As colunas

| Coluna | Valores | O que é |
|---|---|---|
| `id` | slug em inglês, snake_case | **É o `topic` da ficha JSON do documento.** É por igualdade exata com esse metadado que o `compare` mede cobertura |
| `quadro` | texto | O nome em português |
| `sistema` | `digestivo` · `respiratorio` · `urinario` · `neurologico` · `pele_e_ouvido` · `olhos` · `musculoesqueletico_e_trauma` · `toxicologico` · `cardiovascular` · `reprodutivo` · `metabolico` · `ambiental` · `neonatos_e_idosos` | O eixo de sistema orgânico |
| `especie` | `cao` · `gato` · `ambos` | Cobertura é conferida **por espécie** (ver abaixo) |
| `classe` | `emergencia` · `pode_esperar` | O que o sistema decide. Binária, derivada de `urgencia` pela regra de colapso |
| `urgencia` | `imediato` · `ate_24h` · `rotina` | Os três níveis do MSD. Preserva a nuance clínica que a classe binária perde |
| `sinais_que_o_tutor_relata` | itens separados por `;` | Em português leigo, **sem frases completas** — a coluna alimenta a base, e quem escreve a prova escreve relatos a partir do cenário, não copiando daqui |
| `discriminador` | uma ou mais perguntas | O que separa esta linha do seu par de confusão. É o que o documento precisa responder e o que o relato da prova precisa conter |
| `par_de_confusao` | ids separados por `;` | A gêmea do outro lado: o quadro leve que usa as mesmas palavras do grave, e vice-versa. Sempre atravessa as classes |
| `motivo` | uma frase | Por que a linha entra |
| `referencias` | ids `R..` separados por `;`, ou `SEM_FONTE` | Sustentação em [`referencias.md`](referencias.md). `SEM_FONTE` declara a lacuna em vez de inventar |
| `prioridade` | `A` · `B` · `C` | Mérito clínico e frequência (regra abaixo). Ordena a fila **dentro** de cada etapa |
| `etapa` | `1` · `2` | O corte que a porta de decisão pode mover (abaixo) |
| `cobertura` | `sem_documento` → `fonte_enviada` → `fonte_aprovada` → `indexada`; e `sintetico` | Onde a linha está no caminho até a base. `sintetico` marca os sete protocolos de teste que ainda precisam de fonte real |
| `validacao` | `rascunho` · `validada:<nome>:<DD/MM>` · `contestada` | O que os especialistas disseram desta linha |
| `observacoes` | livre | O que não cabe nas outras colunas |

### A regra de colapso, e por que "até 24 h" é a zona cinzenta

Os três níveis viram dois assim: `imediato` → `emergencia`; `ate_24h` e `rotina` → `pode_esperar`. A regra segue as definições que o prompt do classificador já usa: EMERGENCIA exige "atendimento imediato"; NAO_EMERGENCIA "pode aguardar uma consulta comum" — e consulta em 24 horas é consulta comum.

As linhas `ate_24h` são onde a regra mais aperta. O sistema vai dizer "não emergência" para elas, e a mensagem precisa dizer *consulta hoje ou amanhã*, não *não precisa de veterinário*. Isso é do prompt, não do mapa; mas é aqui que fica anotado, e são as primeiras linhas que os especialistas devem olhar.

Duas decisões de produto ficaram conservadoras de propósito, porque o erro grave em pré-triagem é o falso não urgente: **a primeira convulsão é `imediato`** (Cornell; a PDSA admite observar em casa se breve), e **gato que faz força para urinar vai agora, mesmo que ainda saia um pouco** (PDSA: "never wait to see if your cat improves"; Cornell: morte em menos de 24–48 h).

### A regra de prioridade

Escrita para os três aplicarem igual:

| | Quando |
|---|---|
| **A** | Frequente no pronto-socorro (Lee 2014: vômito/diarreia, dispneia, trauma, convulsão, letargia; em gatos, dispneia e disúria) **ou** específico do Brasil com casuística (chumbinho, diclofenaco, parvovirose, permetrina) **ou** já tem caso na régua de recuperação |
| **B** | Clássico de emergência, menos frequente |
| **C** | Raro, ou sem fonte firme ainda |

### A checagem por espécie

Uma linha `ambos` está coberta para gato e descoberta para cão se só houver documento de gato — é exatamente o caso b15 da régua (obstrução uretral: protocolo de gatos, caso de cão macho). O `compare` confere `topic` **e** `species`. Mapeamento com a ficha JSON: `cao` ↔ `dog`/`dogs`, `gato` ↔ `cat`/`cats`, `ambos` ↔ `dogs_and_cats`. As fichas de hoje usam os três formatos misturados ([B-53](../../evidencias/backlog.md#b-53)); o `compare` normaliza singular e plural até o trilho A fechar o vocabulário.

## A fila, as etapas e a porta de decisão

O mapa tem 61 linhas; ninguém busca 61 fontes em três semanas. A fila é por **prioridade**, A → B → C, e a coluna `etapa` diz o corte: a **etapa 1** (31 linhas: os oito documentos que já existem, os quatro quadros que a régua apontou sem cobertura, os tóxicos brasileiros, colapso, parvovirose, o par ocular, a permetrina em gato — e a gêmea leve de cada emergência) é o que se busca, aprova e indexa primeiro. A **etapa 2** (30 linhas) está escrita só no esqueleto — id, quadro, classe, urgência, motivo, referência — de propósito: completar os sinais e o discriminador dela é trabalho para o dia em que a porta disser "vai".

**Não decidimos hoje se vamos às 61.** A porta de decisão abre quando todas as linhas A da etapa 1 estiverem indexadas, **ou em 26/09**, o que vier primeiro. Os três decidem juntos, com os números na mão, e a decisão fica registrada aqui e no [B-50](../../evidencias/backlog.md#b-50), com data. Os critérios estão escritos **antes**, porque porta sem critério vira "achamos que foi bem":

| Eixo | Pergunta | Número | De onde vem |
|---|---|---|---|
| Velocidade | Deu tempo? | ≥ 25 das 31 linhas da etapa 1 com `fonte_aprovada` ou `indexada` | coluna `cobertura` |
| Ordenação | Adicionar documento piorou onde? | Na tabela pareada da régua, **casos que pioraram ≤ casos que melhoraram** | `compare`, bloco ordenação |
| Ímã | Um documento ainda atrai tudo? | Nenhum documento em 1º em mais de **1/3 dos casos** (hoje: trauma em 9 de 18) | `compare`, bloco ruído |
| Ruído nos leves | A base nova empurra caso leve para dentro do prompt? | Nenhum caso leve acima do corte — ou o corte remedido antes ([B-11](../../evidencias/backlog.md#b-11)) | `compare`, bloco ruído |
| Cobertura real | O documento indexado é **encontrável**? | ≥ 70% dos quadros novos aparecem no top-5 do próprio caso da régua | `compare`, bloco cobertura |
| Classificação | O RAG com base real ajuda ou atrapalha? | Acurácia balanceada com RAG **não pior** que sem RAG, além do ruído entre sessões (2–3 linhas, [B-43](../../evidencias/backlog.md#b-43)) | runner de classificação, uma rodada citada |

Três saídas:

1. **Velocidade ok e recuperação ok → entra a etapa 2**, pela mesma fila, até a data de congelamento.
2. **Velocidade ok, recuperação piorou → pausa de documentos, bola para a ordenação** (re-ranking, entrega 6 do trilho A; corte remedido). Voltar a adicionar só quando o `compare` mostrar que parou de piorar. Adicionar documento a uma busca que não separa assunto é pagar para piorar.
3. **Velocidade ruim → fica na etapa 1**; o que sobrar da fila vira trabalho futuro documentado, já com prioridade e fonte apontada.

Independentemente da saída, **a base congela com hash antes da ablação de outubro** (~03/10). Documento que entra depois é outra rodada e obriga a remedir.

Por que não simplesmente cobrir tudo: a base grande **não** deixa o sistema mais lento (a busca cresce milissegundos; o prompt tem tamanho fixo). O risco é outro, e já foi medido — a ordenação de hoje casa com a palavra literal ("vomitou" → protocolo de vômito, mesmo quando o caso é chocolate), e com os pares de confusão todos na base, qual dos quatro documentos sobre vômito vem em primeiro decide o enquadramento. A rodada 10 mostrou quanto custa trecho errado no prompt: 22 emergências rebaixadas. Crescer, sim; crescer medindo.

## Como os especialistas validam

Por linha, e de uma vez — as 61, porque classe e urgência estão preenchidas em todas, e é isso que se valida. Para cada linha: **concordo** (a coluna `validacao` recebe `validada:<nome>:<DD/MM>`), **discordo** (`contestada`, com o motivo em `observacoes` — a classe não muda em silêncio), ou **falta linha** (entra como `rascunho`). Uma linha alterada depois de validada volta a `rascunho`.

Onde a atenção deles rende mais, na ordem: as linhas `ate_24h`; a primeira convulsão como imediato; a espécie da piometra (`ambos`); os três tóxicos brasileiros e a prioridade que receberam; e a linha da raiva, que o sistema vai responder "pode esperar" mas exige serviço de zoonoses.

## Histórico

| Data | O quê | Quem |
|---|---|---|
| 12/09 | Primeira versão: 61 linhas, etapa 1 com 31. Revisão crítica no mesmo dia promoveu colapso, apatia, parvovirose, o par ocular e a permetrina; reescreveu a linha de cistite por segurança; fechou as lacunas do sapo e da hipoglicemia; acrescentou a exposição à raiva | João (B2), pelo roteiro do cartógrafo |
