# Plano das duas frentes: a base e a prova

**Escrito em 12/09/2026, pelo João (trilho B2), a partir do que as rodadas 9,
10 e 11 mediram.** É um plano do time, não de um trilho. Qualquer um dos três
deve conseguir abrir este arquivo e saber o que fazer na segunda-feira.

O que está aqui foi **proposto**, não combinado a três. A seção
[A confirmar com o time](#10-a-confirmar-com-o-time) diz exatamente o que ainda
precisa de acordo.

---

## Índice

1. [Por que estas duas coisas, e por que agora](#1-por-que-estas-duas-coisas-e-por-que-agora)
2. [O que foi decidido](#2-o-que-foi-decidido)
3. [O desenho: duas frentes e uma peça comum](#3-o-desenho-duas-frentes-e-uma-peça-comum)
4. [Frente base](#4-frente-base)
5. [Frente prova](#5-frente-prova)
6. [O mapa de assuntos](#6-o-mapa-de-assuntos)
7. [Agentes](#7-agentes)
8. [Sequência — três semanas](#8-sequência--três-semanas)
9. [Quem faz o quê](#9-quem-faz-o-quê)
10. [A confirmar com o time](#10-a-confirmar-com-o-time)
11. [Próximos passos](#11-próximos-passos)

---

## 1. Por que estas duas coisas, e por que agora

Três rodadas seguidas do trilho B2 chegaram, por caminhos diferentes, no mesmo
par de problemas.

**A [rodada 9](../evidencias/joao/2026-09-12-09-autopsia-do-cot.md) — autópsia
do Chain-of-Thought.** O CoT reprovou (acurácia balanceada de 0,856 para
0,408). A causa não era o modelo: a rubrica pedia que ele julgasse gravidade e
duração de cada sinal, e **o relato de avaliação não tem gravidade nem
duração** — é uma lista de sintomas. A mesma rodada mostrou que os braços com
RAG mediram injeção de ruído: em 98 de 98 linhas nenhum trecho passou do
limiar de relevância, e mesmo assim três trechos entravam em todo prompt.

**A [rodada 10](../evidencias/joao/2026-09-12-10-corte-de-relevancia.md) —
corte de relevância.** O sistema deixou de injetar trecho irrelevante. Com a
base atual o resultado é **idêntico** ao braço sem RAG, porque a busca fica
silenciosa em todas as linhas. O par com e sem corte isolou o custo do ruído:
11,8 pontos de acurácia e 22 falsos não urgentes.

**A [rodada 11](../evidencias/joao/2026-09-12-11-regua-de-recuperacao.md) —
régua de recuperação.** O instrumento que mede se a busca traz o protocolo
certo. Precision@1 de 5 em 9, e dois achados: o protocolo certo está
**sempre** entre os cinco devolvidos (o problema é ordenação, não cobertura), e
existe um **protocolo-ímã** — "trauma" aparece em primeiro lugar em 9 dos 18
casos, inclusive para convulsão e picada de abelha. A mesma rodada listou
**quatro quadros que a base não cobre**: dilatação-torção gástrica,
hipoglicemia neonatal, obstrução uretral em cães e emergência neurológica.

### O que trava, e em quem

| Trilho | O que está parado | Por causa de |
|---|---|---|
| **A** — recuperação | Ampliar a base; qualquer medição de RAG que não seja "o ruído custa caro" | Base sintética, só de emergências, sem cobertura dos assuntos ([B-03](../evidencias/backlog.md#b-03), [B-01](../evidencias/backlog.md#b-01)) |
| **B1** — consulta | Medir reescrita, multi-query e HyDE | Precisava da régua de recuperação — **destravou na rodada 11** ([B-09](../evidencias/backlog.md#b-09)) |
| **B2** — decisão | Escolher a próxima técnica de prompt sem medir no escuro | A prova é trivialmente separável e serve ao mesmo tempo para desenvolver e medir ([B-05](../evidencias/backlog.md#b-05), [B-45](../evidencias/backlog.md#b-45)) |

Na prova atual, a regra "só tem sintoma leve, então não é emergência" acerta
**98 de 98 casos sem modelo nenhum**. Enquanto isso for verdade, nenhum número
do projeto diz o que o sistema sabe fazer.

As duas frentes são independentes o bastante para andar em paralelo, e é isso
que este plano organiza.

---

## 2. O que foi decidido

| Tema | Decisão | Motivo |
|---|---|---|
| **O que entra na base** | **Fontes originais**, indexadas como estão. Documento escrito pelo time só como exceção, para lacuna sem fonte utilizável | O caminho curto: achar → especialista aprova → indexar. Escrever protocolo da casa para cada quadro custaria semanas que não temos |
| **Tipo de fonte** | Material de **orientação a tutores, triagem, primeiros socorros e guidelines** vale mais que artigo de pesquisa | O classificador precisa de "quais sinais, quando é emergência, quando pode esperar". Um paper de fisiopatologia não responde isso |
| **Especialistas** | Recebem a **fonte original** e dizem se serve. Não precisam de material mastigado | São vários e estão disponíveis. Validam também o mapa de assuntos |
| **Repositório** | Vira **privado**, antes do primeiro commit de fonte nova | Fonte de terceiro em repositório público é distribuição. Ver [B-52](../evidencias/backlog.md#b-52) |
| **Classes de saída** | **EMERGENCIA / NAO_EMERGENCIA / INCERTO**, mantido | Mudar para níveis de urgência a um mês da ablação invalidaria tudo que já foi medido. O nível fino pode ir numa coluna extra da prova, para quem quiser colapsar de outro jeito depois |
| **Agentes** | Ferramentas para **construir** o projeto, não partes dele. Roteiros versionados em [`agentes/`](../agentes/README.md). Sem sistema multi-agente orquestrado | A curadoria é feita uma vez; ferramenta de uso único se roteiriza, não se automatiza. E nada disso entra na ablação nem na arquitetura do artigo |
| **Divisão da frente base** | Sem separar "pipeline" de "conteúdo": **quem estiver trabalhando roda os dois agentes** | O João e o Vinicius dificilmente trabalham na mesma hora. Dividir por tipo de tarefa criaria dependência entre duas pessoas que não se encontram |
| **Frente prova** | **Inteira do trilho B1**, inclusive adaptar o runner | Quem escreveu os prompts do classificador não deve escrever a prova que o mede. Ver [a muralha](#a-muralha-entre-base-e-prova) |
| **O que vem primeiro** | O **mapa de assuntos**, feito pelo time por completo; especialistas validam depois | É a peça comum: sem ele, base e prova voltam a não se encaixar — que é o problema de hoje |

---

## 3. O desenho: duas frentes e uma peça comum

```
                      MAPA DE ASSUNTOS
         (a lista de quadros clínicos que importam)
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       FRENTE BASE                   FRENTE PROVA
              │                           │
   agente 1: achar fontes         escrever relatos de tutor
              │                      em português
   especialistas: serve?                 │
              │                    especialistas: o rótulo
   agente 2: indexar +                está certo?
   dizer o que melhorou                  │
              │                     prova congelada
       base ampliada                 (hash, dev/teste)
              └─────────────┬─────────────┘
                            ▼
                 medir de verdade, em outubro
```

### A muralha entre base e prova

A autópsia do CoT deixou um alerta que precisa virar regra agora que três
pessoas e ferramentas de IA vão trabalhar nas duas pontas:

> Se algum documento da base disser o que a prova considera leve, o sistema
> acerta **por construção**, e a medição perde o sentido.

Quatro regras:

1. **Quem trabalha na base não escreve caso da prova**, e vice-versa.
2. **Quem escreve a prova não lê os documentos da base** enquanto escreve.
3. **A prova é congelada assim que estiver validada** — o conteúdo para de
   mudar, com o hash registrado, e a partir daí quem muda é o sistema.
   Congelar **não é deixar de usar**: ver a [cadência](#a-cadência-congelar-não-é-deixar-de-usar)
   logo abaixo. O que nunca acontece é editar um caso depois de ver o sistema
   errar nele.
4. Antes de fechar, **um passo automático confere sobreposição de texto**
   entre os casos da prova e os documentos da base.

Isso vale também para os casos da régua de recuperação: eles são escritos a
partir da linha do mapa, **antes** de ler a fonte — senão o relato copia a
linguagem do documento e a busca "acerta" por eco.

### A cadência: congelar não é deixar de usar

Congelar a prova significa que **o conteúdo dela para de mudar**, não que
fiquemos sem medir até a base estar pronta. Medir o tempo todo é justamente o
que este desenho permite, e é para isso que existem **dois conjuntos**:

| Conjunto | Para quê | Com que frequência |
|---|---|---|
| **Desenvolvimento** (~50 casos) | Testar à vontade: ajustar prompt, ver o efeito de um lote de documentos, errar e tentar de novo | Sempre que precisar |
| **Teste** (~100 casos, congelado) | O número que vai para o artigo | Em marcos |

Com os três instrumentos do projeto, a cadência fica assim — e nenhuma linha
espera a base ficar pronta:

| Quando | Pergunta | Instrumento | Custo |
|---|---|---|---|
| A cada lote de documentos | A busca melhorou? | Régua de recuperação, 18 casos | segundos |
| A cada mudança de prompt | Vale a pena? | Conjunto de **desenvolvimento** | minutos |
| Em marcos | Qual é o número? | Conjunto de **teste**, congelado | mais demorado |

**O que o congelamento protege** são duas coisas, e a segunda é menos óbvia:

1. **Não reescrever um caso que o sistema errou.** É mover a trave depois do
   chute.
2. **Não escolher a melhor de trinta medições.** Rodar o conjunto de teste em
   trinta configurações e reportar a melhor produz um número inflado por
   seleção. Explorar no desenvolvimento e confirmar no teste evita isso — e
   como cada rodada é versionada com manifesto, dá para **contar** quantas
   vezes o conjunto de teste foi tocado. Isso é defensável; "a gente foi
   medindo" não é.

**E o gabarito da prova não envelhece quando a base cresce.** "Este cão com a
barriga dura e inchada é emergência" continua verdade com 7 ou com 40
documentos — é fato clínico, não fato da base. Quem envelhece é o gabarito da
**régua de recuperação**, que aponta para documentos: um caso hoje marcado
"sem cobertura" precisa ganhar o documento novo quando ele entrar. Por isso o
[`compare`](#45-agente-2--indexar-e-dizer-o-que-melhorou) do agente 2 tem o
bloco "gabarito a atualizar".

---

## 4. Frente base

### 4.1 O que a base vai ser

Fontes originais indexadas como estão, com uma ficha JSON ao lado. O formato
já existe e está documentado em
[`backend/data/documents/README.md`](../backend/data/documents/README.md) — e
o README é explícito: *"adicionar um paper novo não deve exigir nenhuma
alteração no código Python"*.

| Item | Regra |
|---|---|
| **Tipo de fonte preferido** | Orientação a tutores ("quando levar ao pronto-socorro"), guias de primeiros socorros, listas de triagem, fichas de protocolo, capítulos com seção de sinais clínicos e encaminhamento |
| **Tipo que vale menos** | Artigo de pesquisa. Entra quando é o que existe sobre o quadro, com as seções inúteis excluídas na ficha |
| **Idioma** | Português quando existir (universidades, CRMVs, ANCLIVEPA, SciELO); inglês é aceito — o embedder é multilíngue — e o efeito é **medido**, não presumido |
| **Curadoria por seção** | A ficha aceita `include_sections`, `exclude_sections` e `exclude_pages`. Tirar "Referências", "Métodos" e "Agradecimentos" leva minutos por documento |
| **Exceção** | Quadro sem fonte utilizável ganha um resumo escrito pelo time a partir da fonte, marcado na ficha como `document_type: team_summary` |

### 4.2 Por que originais, e o que isso custa

| | Fontes originais (escolhido) | Documentos escritos pelo time |
|---|---|---|
| **Ganha** | Caminho curto: achar → aprovar → indexar · sem etapa de redação · procedência direta, boa para o artigo | Linguagem casa com o relato do tutor · uma página validável em minutos · trechos pensados para recuperação |
| **Perde** | Trecho de artigo **não é** trecho de triagem · idioma pode divergir do relato · seções inúteis precisam de curadoria | Semanas de redação e revisão · o examinador pergunta quem escreveu a base |

**Vale a pena, e o risco que sobra tem nome.** O paper de heatstroke que já
está na pasta virou **186 trechos** de fisiopatologia; um relato leigo casa com
qualquer um deles. A auditoria do trilho A já tinha dito:

> *"uma base maior pode aumentar a quantidade de contexto plausível e
> irrelevante"* — [auditoria do repositório, 07/09](../evidencias/vini/2026-09-07-01-auditoria-do-repositorio.md)

E a rodada 10 mediu o preço disso: 22 falsos não urgentes. Três proteções, que
já existem ou estão previstas:

- o **corte de relevância** (rodada 10) descarta trecho abaixo de 0,70 — mas o
  valor é provisório, e hoje até o trecho certo pontua ~0,5;
- a **escolha do tipo de fonte** (tabela acima) é a proteção mais barata;
- o **retorno por lote** (§4.5) vigia se o ruído cresceu, a cada ingestão.

### 4.3 Antes da primeira ingestão

Dois itens do trilho A são pré-requisito, e não é burocracia:

| Item | O quê | Por que antes |
|---|---|---|
| [B-36](../evidencias/backlog.md#b-36) | Cada trecho novo recebe `Document title: … Section: …` colado no texto, e esse texto chega ao prompt | É como fotocopiar uma página com um carimbo em cima do texto. Indexar fontes novas antes de corrigir é medir o defeito, não o documento |
| [B-37](../evidencias/backlog.md#b-37), passos 2–4 | A "virada": a base viva ainda é a antiga, de 18 trechos, que não se reproduz mais. Trocar pela nova nas três máquinas, conferindo que o `content_sha256` bate | Sem isso, cada máquina gera uma base diferente e o time acha que mede a mesma coisa |

### 4.4 Agente 1 — encontrar fontes

**Recebe:** uma linha do mapa de assuntos (um quadro clínico, espécie, se é
emergência ou não, que sinais o tutor relata).

**Produz:** uma lista de fontes candidatas para aquele quadro, em
`data/curadoria/fontes/<topic>.md`. Uma linha por fonte, com:

- **URL ou DOI** — confirmado que abre;
- tipo (orientação a tutor, guideline, primeiros socorros, revisão, capítulo);
- idioma, ano, autoria/instituição, espécie;
- que quadros do mapa a fonte cobre;
- **por que serve**, em uma frase;
- rascunho da **ficha JSON**, que o ingestor vai precisar de qualquer jeito.

**O que o agente não faz:** não resume o conteúdo clínico (aponta a fonte),
não decide se um quadro é emergência (isso é do mapa e dos especialistas), e
não inventa referência — link que não abre não entra.

Uma regra veio de erro real: **espécie errada não serve**. Na régua, o caso
b15 (cão macho com dificuldade de urinar) recebeu o protocolo de obstrução
urinária **de gatos** em primeiro lugar. Assunto próximo, espécie errada.

**Onde procurar, para PT-BR:** SciELO, hospitais veterinários universitários
(USP, UNESP, UFMG, UFRGS), CFMV e CRMVs, ANCLIVEPA. Em inglês: WSAVA
(guidelines livres), RECOVER (reanimação), materiais de extensão de escolas
veterinárias.

### 4.5 Agente 2 — indexar e dizer o que melhorou

Seis dos sete passos **já existem no repositório**. O ciclo:

| # | Passo | Ferramenta | Estado |
|---|---|---|---|
| 1 | Régua **antes** | `scripts/run_retrieval_eval.py --expect-base-hash …` | ✅ |
| 2 | Inspecionar o documento sem tocar no banco | `ingest_documents --inspect --file X` | ✅ |
| 3 | Indexar | `ingest_documents` | ✅ |
| 4 | Conferir que a base mudou como esperado | `GET /health/fingerprint` | ✅ |
| 5 | Régua **depois**, nos mesmos casos | `run_retrieval_eval.py` | ✅ |
| 6 | **Comparar** e dizer o que mudou | `compare` da régua | **a fazer** ([B-51](../evidencias/backlog.md#b-51)) |
| 7 | Escrever o retorno em linguagem simples | opcional, um agente lê o passo 6 | opcional |

**O ciclo inteiro leva de 1 a 3 minutos** — a régua de recuperação não chama o
modelo de linguagem. (A régua de classificação, que roda os 98 relatos contra
o modelo, leva dezenas de minutos: essa roda por marco, não por lote.)

O que o `compare` devolve:

| Bloco | O que mostra | Por que importa |
|---|---|---|
| **Cobertura** | Quais quadros do mapa passaram a ter documento; quais ainda faltam | É o progresso da curadoria, em número |
| **Ordenação** | Δ Precision@1, Δ MRR e a **tabela caso a caso**: posição antes → depois, marcada melhorou / piorou / igual | Uma base maior pode **piorar** a ordenação; a tabela pareada mostra exatamente onde |
| **Ruído** | Δ concentração do protocolo-ímã · Δ casos acima do corte · para os casos **leves**, a nota máxima subiu (ruim) ou desceu (bom) | É o mecanismo que custou 22 falsos não urgentes, vigiado a cada lote |
| **Gabarito a atualizar** | Casos marcados "sem cobertura" cujo assunto agora tem documento | O `expected_topics` daquele caso precisa mudar — o compare avisa em vez de alguém lembrar |
| **Trava** | Recusa comparar se o `cases.csv` mudou entre as duas rodadas | Antes/depois só vale sobre os mesmos casos |

**Duas expectativas, para ninguém se frustrar:**

1. **Para medir melhora num quadro novo, a régua precisa de casos daquele
   quadro.** Cada lote de fontes vem com 1–3 relatos de régua novos, escritos
   a partir do mapa antes de ler a fonte.
2. **Com 20–30 casos, um lote de três documentos costuma mover 0 a 2 casos.**
   O valor do retorno por lote é **cobertura** ("o quadro X agora tem
   documento") e **guarda de regressão** ("nada piorou"). O "melhorou X
   pontos" aparece entre ondas, não a cada documento. É a limitação já
   registrada em [B-49](../evidencias/backlog.md#b-49).

---

## 5. Frente prova

### 5.1 O que a prova é hoje

| Fato | Onde está registrado |
|---|---|
| 98 linhas de cão e gato, vindas de um dataset do Kaggle | [`data/README.md`](../data/README.md) |
| Cada "relato" é uma lista de sintomas **em inglês**: `Animal: Dog. Sintomas observados: Fever, Vomiting…` | [B-15](../evidencias/backlog.md#b-15) |
| 71 emergências (todas originais) e 27 leves (todas sintéticas, combinatória de 5 sintomas) | [B-05](../evidencias/backlog.md#b-05) |
| **"Só tem sintoma leve" acerta 98 de 98 sem modelo**; "menos de 5 sintomas" acerta 97 | [B-05](../evidencias/backlog.md#b-05) |
| "Sempre emergência" acerta 72%, contra 70,41% do sistema na primeira medição | [`data/evaluation/README.md`](../data/evaluation/README.md) |
| Não há conjunto de desenvolvimento: todo ajuste de prompt foi medido no próprio conjunto de teste | [B-45](../evidencias/backlog.md#b-45) |
| O gabarito não tem justificativa por linha, e não há validação de especialista registrada em arquivo | [B-05](../evidencias/backlog.md#b-05) |

### 5.2 O que a prova nova precisa permitir medir

Requisitos do instrumento — o desenho é de quem vai construir:

1. **Que o sistema seja avaliado na língua e no formato em que ele opera**:
   relato de tutor, em português, texto livre. Fecha o [B-15](../evidencias/backlog.md#b-15).
2. **Que as regras triviais parem de acertar.** Critério já escrito no
   [B-05](../evidencias/backlog.md#b-05): nenhuma regra sem modelo passa de
   0,90.
3. **Que se possa ajustar prompt sem contaminar a medição**: conjunto de
   desenvolvimento separado do de teste, por semente, nunca misturados. Fecha
   o [B-45](../evidencias/backlog.md#b-45).
4. **Que cada rótulo seja rastreável**: por que este caso é emergência, de
   onde veio o rótulo, quem validou. O padrão já existe em
   [`data/retrieval/cases.csv`](../data/retrieval/cases.csv), que tem colunas
   `note` e `marked_by` para o especialista discordar de **uma linha** sem
   refazer o resto.
5. **Que a prova seja congelada** por hash assim que validada, e usada desde
   o primeiro dia — ver [a cadência](#a-cadência-congelar-não-é-deixar-de-usar).

### 5.3 O que o time aprendeu, e suspeita

Hipóteses, não regras. Quem construir a prova testa, adapta ou descarta.

- **Duração e gravidade dentro do texto.** Foi a causa raiz do fracasso do
  CoT: a rubrica pedia julgamento que o dado não permitia. Um relato que diz
  "desde ontem, já foram cinco vezes" mede algo que "Vomiting" não mede.
- **Casos difíceis dos dois lados.** Leve com palavra de emergência ("vomitou
  uma vez, mas está brincando e comendo"); emergência descrita com calma
  ("está quietinho", com barriga dura e inchada). É o que separa uma prova de
  um exercício de palavra-chave.
- **Casos fora da base**, de propósito. Medem se o sistema fica quieto ou
  responde INCERTO em vez de inventar. A régua já mostrou que, sem o corte, a
  busca oferece o protocolo errado com convicção parecida à dos acertos.
- **Balanço mais perto de 50/50.** Hoje é 72/28, e o chute "sempre
  emergência" ganha do modelo.
- **Tamanho na casa de 150 relatos**, divididos em teste e desenvolvimento.
  Com 100 de teste, cada caso vale 1 ponto — diferenças menores que isso são
  ruído.
- **Rótulo ancorado em referência publicada** de triagem veterinária, não em
  opinião. A escala escolhida vira coluna do gabarito.
- **Relatos reais, se der.** Quinze ou vinte mensagens verdadeiras de tutores,
  anonimizadas, valem muito: texto gerado por modelo é limpo demais, e tutor
  real escreve com erro, falta de informação e pressa.
- **Escrever a partir do cenário clínico, não da coluna de sinais do mapa.**
  Copiar a coluna faz a prova voltar a ser separável por palavra.

### 5.4 O runner, que precisa aprender a ler a prova nova

**O que é o runner** ([`scripts/run_evaluation.py`](../scripts/run_evaluation.py)):
o corretor automático. Pega cada caso da prova, manda para o sistema como se
fosse um tutor perguntando, recebe a classificação, compara com o gabarito e
calcula as notas — acurácia balanceada, falsos não urgentes, cobertura,
latência, ancoragem.

**O que ele sabe ler hoje:** uma planilha com cinco colunas de sintoma em
inglês, que ele monta como `Animal: Dog. Sintomas observados: …`. O caminho do
arquivo é uma constante no código, e os baselines triviais dependem de contar
sintomas.

**O que muda para ler texto livre:**

| Mudança | Detalhe |
|---|---|
| Coluna `text` | Uma função de montagem alternativa, em vez das cinco colunas |
| `--relato-lang` | Registrar o idioma no manifesto — já previsto no [B-15](../evidencias/backlog.md#b-15) |
| Caminho por opção | Hoje é constante; passa a ser argumento, com o hash do arquivo no manifesto (o `--resume` confere) |
| Baselines triviais novos | Os atuais contam sintomas e não funcionam com texto livre. Substitutos: saco de palavras com validação cruzada, "tem palavra de alarme", comprimento do relato. **São eles que denunciam se a prova nova também é trivial** — sem isso, perde-se o instrumento que detectou o problema do [B-05](../evidencias/backlog.md#b-05) |

`scripts/` é pasta do trilho B2 ([`CONTRATOS.md`](CONTRATOS.md)): a mudança é
do B1, com revisão do B2.

---

## 6. O mapa de assuntos

### 6.1 O que é, e por que vem primeiro

Uma planilha com os quadros clínicos que importam para triagem de cão e gato.
Parece burocracia e não é: **é cinco coisas no mesmo arquivo.**

1. **A análise do que falta.** É o insumo do agente 1 — sem ela, uma busca por
   "emergências veterinárias" volta com duzentas coisas.
2. **A lista de tarefas.** Cada linha é um trabalho de busca, que dá para
   dividir entre pessoas e rodar em paralelo.
3. **O painel de progresso.** A coluna de status diz onde a base está a
   qualquer momento — e é o que o `compare` lê para medir cobertura.
4. **O que os especialistas validam primeiro**, e o mais barato para eles:
   validar 25 linhas leva meia hora e define o escopo inteiro.
5. **A tabela que o artigo precisa.** "O sistema cobre estes N quadros,
   escolhidos por isto" responde à pergunta "por que esses documentos?".

Tem um sexto uso, que aparece depois: quando um caso errar, o mapa diz se foi
**falta de cobertura** (o assunto não está na base) ou **erro de busca ou de
classificação** (o assunto está e o sistema não achou, ou leu mal). Hoje só a
régua faz essa distinção, em quatro casos.

### 6.2 Os datasets do Kaggle não bastam

Pergunta legítima: o `dataset1` já diz quais sintomas são perigosos, e o
`dataset2` já traz nomes de doença. Não dá para usar?

| | `dataset1` (é a prova atual) | `dataset2` |
|---|---|---|
| Cão e gato | 70 linhas, **todas** `Dangerous = Yes` | 147 linhas, 48 doenças distintas |
| Nomeia o quadro clínico? | **Não** — é saco de sinais em inglês, com erros de grafia | Sim, mas do tipo errado |
| O que cobre | Não dá para saber: sem quadro, não há assunto | Quase tudo infeccioso ou crônico: parvovirose, cinomose, tosse dos canis, PIF, calicivirose, FeLV, artrite, renal |
| Emergências clássicas | — | **Nenhuma.** Nada de trauma, intoxicação, torção gástrica, obstrução uretral, convulsão, dispneia aguda, golpe de calor, distocia |
| Lado "pode esperar" | **Zero** linhas originais leves | Algumas (conjuntivite, rinite alérgica, artrite) |

E um cuidado a mais: **o `dataset1` é a prova de hoje**. Usar as combinações
dele para decidir o que entra na base é olhar a chave de resposta antes de
montar a biblioteca — o mesmo raciocínio que levou o time a **não** indexar os
datasets como conhecimento ([B-44](../evidencias/backlog.md#b-44)).

**Conclusão:** os dois servem como **checagem**, não como esqueleto. O
esqueleto precisa de quadro clínico, e ele vem de referência publicada.

### 6.3 Como construir — oito passos

1. **Esqueleto por eixos:** sistema orgânico × classe (emergência / pode
   esperar) × espécie. Sistemas: digestivo, respiratório, urinário,
   neurológico, pele e ouvido, olhos, musculoesquelético e trauma,
   toxicológico, cardiovascular, reprodutivo, metabólico, ambiental,
   neonatos e idosos.
2. **Lado emergência**, de três entradas: os 7 protocolos atuais; os 4 quadros
   que a régua apontou como sem cobertura; e uma referência publicada de
   triagem veterinária, mais estudos de motivo de atendimento em
   pronto-socorro — que dão **frequência**, e frequência vira prioridade.
3. **Lado "pode esperar"**, por sistema: coceira e otite leve, espirro isolado
   em animal que come bem, vômito único em animal ativo, claudicação leve que
   apoia a pata, conjuntivite leve, diarreia leve sem outros sinais, pulgas,
   unha quebrada sem sangramento. É o critério do
   [B-03](../evidencias/backlog.md#b-03) aplicado: ao menos um quadro leve por
   sistema orgânico frequente.
4. **Par de confusão** — a coluna que faz a diferença. Para cada emergência, a
   gêmea leve que usa as mesmas palavras: vômito único ↔ torção gástrica ·
   espirro ↔ dispneia · manca leve ↔ fratura · coceira ↔ reação alérgica com
   edema de face · xixi fora do lugar ↔ obstrução uretral. É aqui que a
   inteligência clínica do projeto fica escrita **uma vez**, servindo à base e
   à prova.
5. **Colunas:** `id`, `quadro` (PT), `sistema`, `especie`, `classe`,
   `sinais_que_o_tutor_relata`, `par_de_confusao`, `por_que_entra` (a
   referência), `prioridade` (A/B/C, por frequência × gravidade), `status`
   (na base / falta fonte / fonte enviada / validada / indexada), `dono`.
6. **Checagem cruzada com os datasets:** cada um dos ~98 sinais do `dataset1`
   cai em pelo menos uma linha, ou é marcado "inespecífico"; cada uma das 48
   doenças do `dataset2` está coberta ou foi excluída de propósito.
7. **Ondas.** Onda 1: 20 a 25 linhas — os 7 atuais, os 4 sem cobertura, uns 10
   pares leves, e os clássicos que faltam (distocia, anafilaxia, engasgo,
   raticida, hipoglicemia de filhote; golpe de calor já tem fonte). Onda 2
   depois da virada da base.
8. **Especialistas validam:** acrescentam, cortam, reclassificam, mudam
   prioridade. Só então a lista vira o índice das duas frentes.

**Onde fica:** `data/curadoria/mapa-de-assuntos.csv`, com um README ao lado
explicando as colunas. CSV porque o `compare` do agente 2 lê dele para medir
cobertura.

---

## 7. Agentes

**Princípio: agentes para construir o projeto, não dentro do projeto.** Eles
ajudam a curar a base e a organizar o trabalho. Nenhum deles entra no sistema,
na matriz de ablação ou na arquitetura descrita no artigo. Quando a curadoria
terminar, eles param de ser usados — o que fica é o que produziram, e o
registro de como foram usados.

| Papel | Roda | Entrada | Produz | Usa LLM? |
|---|---|---|---|---|
| **Cartógrafo** | uma vez (por onda) | régua, backlog, referências de triagem | `data/curadoria/mapa-de-assuntos.csv` | sim |
| **Pesquisador** (agente 1) | uma vez por quadro | uma linha do mapa | `data/curadoria/fontes/<topic>.md` + rascunho da ficha JSON | sim, com busca na web |
| **Redator de lacuna** | só quando não há fonte | a fonte que existe | resumo do time, `document_type: team_summary` | sim |
| **Ingestão e retorno** (agente 2) | uma vez por lote | fontes aprovadas | base atualizada + `compare.md` | **não** — é script |

O detalhe de cada roteiro está em [`agentes/README.md`](../agentes/README.md).

---

## 8. Sequência — três semanas

| Semana | Frente base (quem estiver trabalhando) | Frente prova (B1) | Trilho A | Especialistas |
|---|---|---|---|---|
| **1** — até 19/09 | Repositório privado · roteiros em `agentes/` · **mapa de assuntos** rascunhado e revisado pelos três | Escolher a referência de triagem · primeiro lote pequeno de casos, para calibrar | Fechar [B-36](../evidencias/backlog.md#b-36) · preparar a virada | Validam o **mapa** |
| **2** — até 26/09 | Agente 1 por quadro da onda 1 → listas de fontes + fichas · fontes enviadas · `compare` escrito · casos de régua dos quadros novos | Restante dos relatos · regras triviais medidas · ajustes | Virada ([B-37](../evidencias/backlog.md#b-37) passo 4): `content_sha256` igual nas três máquinas · régua na base nova | Dizem **sim ou não às fontes** |
| **3** — até 03/10 | Ciclo do agente 2 por lote aprovado: indexar → comparar · lacunas com redator · onda 2 do mapa | Prova congelada (hash) · divisão teste/desenvolvimento · runner adaptado | Re-ranking começa (entrega 6 do trilho A) | Validam **rótulos da prova** |
| **Outubro** | **Matriz de ablação completa**, os três juntos | | | |

**Escopo da onda 1:** 20 a 25 quadros com fonte, e a prova nova na casa de 150
relatos. Mais que isso não cabe em três semanas.

---

## 9. Quem faz o quê

| Quem | O quê |
|---|---|
| **João (B2)** | Construção dos agentes e dos roteiros · mapa de assuntos (rascunho) · `compare` da régua · casos de régua dos quadros novos · revisão da mudança no runner |
| **Ryu (B1)** | Frente prova inteira: desenho, casos, gabarito, adaptação do runner |
| **Vinicius (A)** | [B-36](../evidencias/backlog.md#b-36) e a virada da base ([B-37](../evidencias/backlog.md#b-37)) · depois, re-ranking |
| **Qualquer um dos três** | Rodar o agente 1 (achar fontes) e o agente 2 (indexar e comparar) quando estiver trabalhando na base |
| **Especialistas** | Validar o mapa de assuntos · dizer se cada fonte serve · validar os rótulos da prova |

---

## 10. A confirmar com o time

Proposto pelo João em 12/09, a partir das rodadas 9, 10 e 11. **Ainda não foi
combinado a três.** Ajustes entram aqui, com data e quem pediu.

1. **A curadoria e ampliação da base** é a entrega 4 do
   [planejamento do trilho A](../evidencias/vini/planejamento.md). Este plano
   propõe que ela passe a ser **compartilhada**, com qualquer um dos três
   rodando os agentes — e que o Vinicius concentre nos pré-requisitos
   (B-36 e a virada) e, depois, no re-ranking, que a régua apontou como a
   correção certa para a ordenação.
2. **O [B-15](../evidencias/backlog.md#b-15)** (relatos em inglês) passa a ser
   do **trilho B1**, junto com a prova nova e a adaptação do runner. Hoje está
   com o B2. Troca de dono é acordo entre os dois — regra 3 do
   [backlog](../evidencias/backlog.md).
3. **Quem torna o repositório privado**, e quando. É configuração do GitHub e
   o repositório está na conta do Vinicius. Precisa acontecer antes do
   primeiro commit de fonte ([B-52](../evidencias/backlog.md#b-52)).

---

## 11. Próximos passos

Nesta ordem, porque cada um alimenta o seguinte:

| # | O quê | Produz | Quem |
|---|---|---|---|
| 1 | **Mapa de assuntos** | Roteiro do cartógrafo em `agentes/` + primeiro rascunho de `data/curadoria/mapa-de-assuntos.csv` | João rascunha; os três revisam |
| 2 | **Roteiros dos agentes** | `agentes/pesquisador.md`, `agentes/ingestao.md`, `agentes/redator-de-lacuna.md` e os atalhos em `.claude/agents/` | João |
| 3 | **`compare` da régua** | O retorno por lote do agente 2 ([B-51](../evidencias/backlog.md#b-51)) | João |
| 4 | **Frente prova** | A partir da [seção 5](#5-frente-prova) | Ryu |

Os quatro cabem na primeira semana, e nenhum deles chama o modelo de
linguagem.
