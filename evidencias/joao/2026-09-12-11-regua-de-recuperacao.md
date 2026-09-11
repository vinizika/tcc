# Régua de recuperação, construída em nome do trilho A

**Data:** 12/09/2026 · **Trilho:** A (Recuperação), construída pelo B2 ·
**Rodada:** 11 · **Commits:** 74c6dfa (contrato do trilho A), + este

> **Esta rodada é de outro trilho.** A régua de recuperação é a próxima
> entrega planejada do trilho A, e quem a construiu fui eu, do B2, com
> autorização do João. O gabarito — qual protocolo é o certo para cada
> relato — está marcado como **provisório** e precisa da validação do
> Vinicius. O planejamento dele não foi editado por mim.
>
> Arquivo criado **antes** do código, como manda o padrão.

## O que foi feito

Um instrumento que responde a uma pergunta que o projeto nunca conseguiu
responder: **a busca traz o protocolo certo?**

Ele é o irmão do runner de classificação, para um pedaço diferente do
sistema. O runner mede o sistema inteiro, do relato até "emergência ou
não"; a régua mede só o bibliotecário. A pergunta não é "acertou a
resposta?", é "o capítulo certo veio em primeiro?".

| | Runner (existe desde 04/09) | Régua (esta rodada) |
|---|---|---|
| Testa | O sistema inteiro | Só a busca |
| Pergunta | O caso foi classificado certo? | O protocolo certo veio em primeiro? |
| Nota | Acurácia balanceada | Posição: Precision@1, MRR, Recall@5 |
| Casos | 98 listas de sintomas em inglês | 18 relatos de tutor em português |

## Por quê

**Porque ela é o gargalo declarado de dois trilhos.** O trilho A diz no
planejamento dele que não amplia a base sem ela. O B1 não consegue medir
reescrita, multi-query e HyDE sem ela — é o
[B-09](../backlog.md#b-09), aberto desde 04/09. Nenhum dos dois é meu, e os
dois estão parados esperando a mesma peça.

**Porque ela decide um número que hoje é chute.** A
[rodada 10](2026-09-12-10-corte-de-relevancia.md) fez o corte de relevância
valer, em 0,70, e declarou o valor provisório no código: ele é coerente com
o que o sistema já reportava, mas ninguém mediu que é o certo. Quem mede é
esta régua.

**Porque um ensaio de cinco minutos já mostrou o que ela vai encontrar.**
Antes de escrever qualquer código, rodei os 18 relatos contra a busca ao
vivo. O resultado está na seção "O que o ensaio mostrou" — e ele achou um
padrão que ninguém tinha visto.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **Reaproveitar os 18 relatos do benchmark de voz** em vez de escrever casos novos | O trilho A planejou quatro casos e não disse de onde viriam os textos. Os 18 que o Ryu escreveu para medir o Whisper são relatos de tutor em português, cobrem os sete protocolos e trazem cinco casos leves. A **mesma frase** passa a ser testada na transcrição, na busca e (quando o conjunto for refeito) na classificação |
| 2 | O gabarito aceita um **conjunto** de protocolos, não um só | Um cão atropelado e ofegante casa com trauma **e** com dificuldade respiratória. Exigir um único documento puniria acerto legítimo |
| 3 | Três categorias de caso, não duas: **com protocolo**, **caso leve**, **sem cobertura** | O trilho A previu que o caso leve aceita "nenhum protocolo". Faltava uma terceira: relatos que são emergência mas cujo assunto **não existe na base**. Misturar as duas confundiria "a busca acertou ao ficar quieta" com "a base não tem o que buscar" |
| 4 | Julgar por `topic`, não por título | Título é texto livre e muda quando o protocolo é reescrito. Exigiu levar `topic` e `source_file` até a rota de busca — mudança em arquivo do trilho A, em commit separado (`74c6dfa`) |
| 5 | Medir também a **concentração no primeiro lugar** | Não estava no plano do trilho A. O ensaio mostrou um protocolo aparecendo em primeiro em quase metade dos casos, e isso não aparece em nenhuma das três métricas clássicas |
| 6 | O gabarito vai versionado com o **motivo** de cada marcação | Quatro casos exigiram julgamento clínico, não técnico. O Vinicius precisa poder discordar de uma linha específica sem refazer o trabalho todo |
| 7 | Não medir "silêncio" como acerto enquanto a busca estiver silenciosa em tudo | Com a base atual nenhum trecho passa do corte em nenhum caso. Contabilizar isso como "a busca soube ficar quieta nos casos leves" seria dar crédito por um acerto acidental |

## O gabarito, e onde ele precisa de validação clínica

Nove casos têm protocolo na base e são os que medem Precision@1:

| Caso | Relato, em resumo | Protocolo esperado |
|---|---|---|
| b01 | comeu chocolate, tremendo e vomitando | intoxicação por chocolate |
| b02 | gata sem urinar desde ontem, miando de dor | obstrução urinária (gatos) |
| b03 | respiração difícil, língua roxa | dificuldade respiratória |
| b04 | convulsão de dois minutos | convulsões |
| b06 | atropelado, mancando, sangramento na pata | trauma e hemorragias |
| b07 | vômito e diarreia desde ontem, cinco vezes | vômito e diarreia |
| b08 | comeu cebola e alho, gengiva pálida | intoxicação por cebola e alho |
| b13 | cortou a pata em vidro, sangrando há dez minutos | trauma e hemorragias |
| b16 | picado por abelha, focinho inchando rápido | dificuldade respiratória |

**Cinco casos leves**, em que a resposta certa é não trazer protocolo de
emergência: b05 (espirros, comendo bem), b09 (coçando a orelha, casquinha),
b10 (manca de leve depois de correr), b11 (olho lacrimejando há dois dias),
b18 (secreção nasal, sem febre).

**Quatro casos sem cobertura na base** — são emergências, mas nenhum
protocolo trata do assunto:

| Caso | Por quê | O que faltaria na base |
|---|---|---|
| b12 | barriga inchada e dura, tentando vomitar sem sair nada | dilatação-torção gástrica |
| b14 | filhote molinho, não mama, boca fria | hipoglicemia e hipotermia neonatal |
| b15 | cão **macho** urinando gotinhas com dor | obstrução urinária em cães (o protocolo da base é **de gatos**) |
| b17 | cadela idosa sem levantar as pernas de trás, ofegante | emergência neurológica |

**O que preciso que o trilho A valide**, com a especialista se necessário:

1. Os quatro casos sem cobertura. Marquei b12 e b15 assim depois de errar no
   primeiro ensaio: eu havia apontado b12 para "vômito e diarreia" e b15
   para "obstrução urinária". Os dois estavam errados, e por motivos
   diferentes — b12 é outro quadro, b15 é a espécie errada.
2. O caso b16. Picada de abelha com edema de face é risco de via aérea, por
   isso apontei para dificuldade respiratória. Não apontei para trauma,
   porque é reação alérgica.
3. Se "manca de leve depois de correr" (b10) é mesmo caso leve.

## Resultado esperado

_Escrito antes do código. **Atenção ao que isto é:** um ensaio manual já
mediu parte destes números, com um gabarito que depois corrigi em dois
casos. Não é previsão às cegas, é pré-medição sem instrumento — e a
diferença fica registrada porque, do contrário, a evidência pareceria uma
previsão mais precisa do que foi._

| Métrica | Esperado | Base |
|---|---|---|
| Precision@1 | ≈ 5 de 9 | Ensaio deu 5/11 com o gabarito antigo; dois casos saíram da conta |
| MRR | ≈ 0,6 | Ensaio |
| Concentração no 1º lugar | "trauma" em ≈ 8 de 18 | Ensaio |
| Casos com algum trecho acima de 0,70 | **0 de 18** | Ensaio, e coerente com as 98 linhas do runner |
| Silêncio nos leves | 5 de 5, **por acidente** | Ver abaixo |

**A armadilha que a evidência precisa dizer em voz alta:** com a base
atual, a busca não passa do corte em **nenhum** caso. Então ela "acerta"
todos os cinco leves e todos os quatro sem cobertura — mas não porque soube
ficar quieta, e sim porque está sempre quieta. Um relatório que
comemorasse 100% de silêncio estaria mentindo. O relatório vai dizer isso
explicitamente quando os dois números coincidirem.

**O que esta rodada acrescenta ao ensaio:** o instrumento versionado, o
gabarito com motivo, a reprodutibilidade, e a capacidade de medir a mesma
coisa antes e depois da virada da base. Não é o número.

## O que o ensaio mostrou, e o que a régua confirmou

Antes de escrever código, rodei os 18 relatos contra a busca ao vivo com um
gabarito improvisado. A régua depois confirmou o padrão, com dois números
diferentes porque o gabarito foi corrigido em dois casos (b12 e b15 saíram
da conta de "com protocolo" e viraram "sem cobertura").

Rodada [`20260911-202505_linha_de_base`](../../data/retrieval/cited/20260911-202505_linha_de_base/report.md)
· 18 casos · base de 18 trechos (`eeba9f51…`) · commit `74c6dfa`.

| Métrica | Valor |
|---|---|
| **Protocolo certo em 1º lugar** | **5 de 9** (0,556) |
| Posição média invertida (MRR) | 0,698 |
| Protocolo certo entre os cinco devolvidos | **9 de 9** (1,000) |
| Casos com algum trecho acima de 0,70 | **0 de 18** |
| Nota máxima média | 0,504 |

### 0,556 é bom? Comparado com o quê

Um número sozinho não diz nada. O runner de classificação compara com
estratégias burras desde setembro, e a régua passou a fazer o mesmo:

| Estratégia | Protocolo certo em 1º |
|---|---|
| Escolher um documento ao acaso entre os 7 da base | 0,143 |
| Responder sempre "trauma", o protocolo mais frequente em 1º | 0,222 |
| **A busca** | **0,556** |

A busca ganha das duas com folga — vale quase quatro vezes o acaso. É o que
justifica tratar o problema como **ordenação**, e não como "a busca não
funciona".

### O achado: existe um protocolo-ímã

| Protocolo em 1º lugar | Casos |
|---|---:|
| **Trauma, quedas e hemorragias** | **9 de 18** |
| Obstrução urinária em gatos | 4 |
| Vômito e diarreia | 3 |
| Dificuldade respiratória | 1 |
| Intoxicação por cebola e alho | 1 |

Metade dos casos tem "trauma" como primeiro resultado — inclusive convulsão,
picada de abelha, cadela idosa que não levanta as pernas e cão urinando
gotinhas. Um documento está atraindo consultas de assuntos que não são dele.

Isso é o [B-02](../backlog.md#b-02) com número pela primeira vez, e é a
explicação mais provável para o que a [rodada 10](2026-09-12-10-corte-de-relevancia.md)
mediu: injetar os três primeiros trechos custava 22 emergências
classificadas como leves. O modelo estava lendo protocolo de hemorragia para
um gato que espirra.

### Onde o protocolo certo ficou, caso a caso

| Caso | Protocolo esperado | Posição |
|---|---|---:|
| b02 gata sem urinar | obstrução urinária | **1** |
| b03 respiração difícil | dificuldade respiratória | **1** |
| b06 atropelado | trauma | **1** |
| b07 vômito e diarreia | vômito e diarreia | **1** |
| b13 corte sangrando | trauma | **1** |
| b08 cebola e alho | intoxicação por allium | 2 |
| b16 picada de abelha | dificuldade respiratória | 3 |
| b04 convulsão | convulsões | 4 |
| b01 comeu chocolate | intoxicação por chocolate | **5** |

**Recall@5 é 1,000**: o protocolo certo está **sempre** entre os cinco
devolvidos. O problema não é a busca não encontrar; é ela não colocar em
primeiro. Isso muda o diagnóstico — não é um problema de cobertura do
índice, é de ordenação.

E o pior caso é revelador. "Meu cachorro comeu um pedaço grande de chocolate
hoje de manhã e agora está tremendo e vomitando" coloca o protocolo de
chocolate em **quinto**, atrás de vômito e diarreia. A busca está casando
com "vomitando", a palavra mais literal do relato, e ignorando "chocolate",
que é a informação que decide o caso.

### O silêncio é acidente, não mérito

| Natureza | Casos | Busca ficou quieta |
|---|---:|---:|
| Caso leve | 5 | 5 de 5 |
| Sem cobertura na base | 4 | 4 de 4 |

Parece perfeito, e não é. **Nenhum dos 18 casos teve trecho acima do corte**,
então a busca "acerta" os leves porque está sempre quieta. O relatório da
rodada emite essa ressalva sozinho, para ninguém ler 100% como discernimento.

Dito de outro jeito: hoje a régua não consegue distinguir "a busca soube
ficar quieta" de "a busca não consegue falar".

### Os quatro casos sem cobertura, e o que a busca ofereceu

| Caso | Quadro | O que a busca ofereceu em 1º |
|---|---|---|
| b12 | dilatação-torção gástrica | trauma (0,562) |
| b14 | filhote hipoglicêmico | intoxicação por allium (0,376) |
| b15 | obstrução uretral em **cão** | trauma (0,600) |
| b17 | emergência neurológica em idosa | trauma (0,546) |

Nos quatro, a busca oferece o protocolo errado com convicção parecida à dos
casos que ela acerta. Ela não tem como dizer "não tenho isso" — só devolve o
menos distante. É o argumento mais concreto para o corte que a rodada 10
implementou.

## As previsões

| # | Esperado | Obtido |
|---|---|---|
| Precision@1 ≈ 5 de 9 | **5 de 9** ✅ |
| MRR ≈ 0,6 | 0,698 — um pouco melhor |
| "Trauma" em 1º em ≈ 8 de 18 | **9 de 18** — um a mais |
| Nenhum caso acima de 0,70 | ✅ confirmado |
| Silêncio nos leves 5/5, por acidente | ✅ confirmado, e o relatório diz isso sozinho |

O ensaio previu bem porque **era** uma medição, feita à mão. O valor desta
rodada não está nos números: está em eles serem agora reprodutíveis,
versionados, e comparáveis antes e depois da virada da base.

## O que mudou no repositório

| Arquivo | O quê |
|---|---|
| `data/retrieval/cases.csv` | **novo** — 18 casos com gabarito, motivo clínico e marca de provisório |
| `scripts/retrieval_metrics.py` | **novo** — módulo puro: posição, MRR, recall, silêncio por natureza, concentração no 1º lugar |
| `scripts/run_retrieval_eval.py` | **novo** — o runner, reaproveitando `ApiClient`, escrita atômica, fingerprint e conferência de base do runner de classificação |
| `scripts/tests/test_retrieval_metrics.py` | **novo** — 16 testes, valores conferíveis à mão |
| `data/retrieval/README.md` | **novo** — o que é, como rodar, como o gabarito foi marcado e o que o trilho A precisa validar |
| `data/retrieval/cited/20260911-202505_linha_de_base/` | a rodada citada |
| `backend/app/models/retrieved_document.py`, `clients/retrieval_client.py`, `schemas/search.py`, `services/search_service.py`, `tests/test_api_search.py` | commit `74c6dfa`, **arquivos do trilho A**: `topic` e `source_file` atravessam até a rota de busca |
| `.gitignore` | `data/retrieval/runs/` fora do Git, mesma regra das rodadas de avaliação |

Testes: scripts 76 → 92, backend 129 → 134.

## Observações

**1. O diagnóstico do B-02 mudou de natureza.** Recall@5 em 1,000 significa
que o índice **tem** o documento certo e **o encontra** — ele só não o põe em
primeiro. O problema não é cobertura nem chunking: é ordenação. Isso reforça
o re-ranking (entrega 6 do trilho A).

**Com uma ressalva que precisa andar junto do número:** a base tem sete
documentos e a busca devolve cinco trechos, em média 4,4 documentos
distintos. "O certo está entre os cinco" é, com esse acervo, quase
geométrico — escolhendo 5 dos 7 ao acaso o recall já daria ≈ 0,71. O 1,000
é verdadeiro e é **fraco**: ele não prova que a recuperação está resolvida,
e não é argumento para desprioritizar a ampliação da base
([B-49](../backlog.md#b-49)).

**2. A busca casa com o sintoma literal, não com a causa.** O caso do
chocolate é o exemplo limpo: o relato diz "comeu chocolate" e "vomitando", e
a busca escolhe o protocolo de vômito. Para triagem isso é exatamente o
inverso do desejado — a causa decide a conduta, o sintoma não.

**3. O protocolo-ímã provavelmente tem explicação no texto.** "Trauma,
quedas e hemorragias" cobre vários sinais genéricos (dor, sangramento,
prostração, dificuldade de locomoção) que aparecem em quase todo relato de
emergência. É hipótese, não medição: confirmar exige olhar os trechos, e
isso é do trilho A.

**4. A régua está cega para o efeito do corte.** Com nenhum caso acima de
0,70, ela não distingue silêncio deliberado de silêncio forçado. Quando a
base melhorar, essa distinção volta a ter sentido — e é ela que vai dizer o
limiar certo, que a rodada 10 deixou provisório.

**5. Os quatro casos sem cobertura são a lista de compras da curadoria.**
Dilatação-torção gástrica, neonato, obstrução uretral em cães e emergência
neurológica. Os quatro são quadros clássicos de pronto-socorro veterinário,
e nenhum está na base.

**6. O gabarito precisa de validação, e eu errei duas vezes nele.** No
ensaio marquei b12 como vômito/diarreia e b15 como obstrução urinária. Os
dois estavam errados — b12 é outro quadro, b15 é a espécie errada. Se eu
errei duas em dezoito lendo com atenção, o trilho A e a especialista vão
achar mais.

## O que melhora quando a base crescer e houver mais casos

A régua está pronta e já produziu dois achados. Mas convém registrar, antes
que alguém cite os números fora de contexto, **o que ela ainda não consegue
dizer** — e que nada disso se conserta com código. É dado que falta.
Registrado como [B-49](../backlog.md#b-49).

| Número | Por que hoje diz pouco | O que destrava, e quando |
|---|---|---|
| **Recall@5 = 1,000** | A base tem 7 documentos; a busca mostra ~4,4 distintos por caso. Está quase mostrando o acervo inteiro | Com a base acima de ~20 documentos ([B-37](../backlog.md#b-37), [B-03](../backlog.md#b-03)), 5 de 20 volta a ser uma escolha de verdade. Só então vale comparar recall entre duas receitas de chunking |
| **Precision@1 = 0,556** | São 5 acertos em 9 casos. **Um caso mudando move 11 pontos**: diferenças menores que isso entre duas rodadas são ruído | Com 25–30 casos com protocolo, passa a distinguir diferenças de ~5 pontos — que é a ordem de grandeza esperada do re-ranking |
| **Silêncio nos leves = 5/5** | Nenhum caso passa do corte, então ela "acerta" por estar sempre quieta | Quando algum caso passar de 0,70, a taxa passa a medir discernimento. É também o que falta para a régua **escolher** o limiar ([B-11](../backlog.md#b-11)) |
| **Baselines** | O acaso vale 0,143 porque a base tem 7 documentos. Numa base de 30, o acaso cai para ~0,03 | O piso desce, e a mesma Precision@1 passa a valer mais. Comparar 0,556 de hoje com um 0,556 futuro exigirá olhar o baseline junto |

Duas capacidades novas que só chegam com **casos** novos, não com
documentos:

1. **Espécie e idade.** Hoje só b15 toca nisso — cão macho com dificuldade
   de urinar, e o único protocolo de obstrução da base é de gatos. A busca
   ofereceu trauma. Casos que separem cão de gato e filhote de idoso
   mediriam algo que hoje ela demonstravelmente não faz, e que importa
   clinicamente.
2. **Sintoma literal contra causa.** O caso b01 (comeu chocolate, está
   vomitando → a busca escolhe "vômito e diarreia") é o exemplo mais limpo
   do problema, e é **um** caso. Com cinco ou seis relatos desse tipo,
   "casou com o sintoma em vez da causa" vira uma métrica, não uma anedota.

**O que já funciona sem nada disso**, e é por isso que a rodada foi feita
agora: comparar **duas versões do mesmo sistema sobre os mesmos casos**.
Antes e depois da virada da base, com e sem re-ranking, com e sem reescrita
de consulta. A comparação pareada não depende do tamanho do acervo — o
mesmo raciocínio que faz o runner de classificação usar McNemar pareado em
vez de comparar acurácias soltas. A linha de base congelada hoje vale
exatamente por isso.

## Deixado para depois

**Validação do gabarito pelo trilho A** ([B-48](../backlog.md#b-48)). É o
passo que transforma esta régua de "instrumento provisório" em "régua do
trilho A". Sem ele, os números são meus, não do time.

**Medir a mesma coisa depois da virada da base.** O retrato da base antiga
está guardado, então dá para medir as duas sobre os mesmos casos e separar
"a receita de picar melhorou" de "o conteúdo melhorou". Depende da virada
([B-37](../backlog.md#b-37)).

**Descobrir por que "trauma" atrai tudo** ([B-02](../backlog.md#b-02)).
Precisa olhar o texto dos trechos, e é do trilho A.

**Usar a régua para escolher o limiar** ([B-11](../backlog.md#b-11)). Só faz
sentido quando algum caso passar do corte. Hoje qualquer limiar acima de
0,60 dá o mesmo resultado: silêncio em tudo.

## Próximo passo

**Levar a régua ao time.** Ela existe, mede, e já produziu dois achados que
mudam prioridades: o protocolo-ímã e o Recall@5 em 1,000. O trilho A ganha o
instrumento que planejou e a linha de base congelada antes da virada; o
trilho B1 ganha como medir as técnicas de consulta, que era o
[B-09](../backlog.md#b-09).

Do meu lado, a fila não mudou: as três correções continuam sendo a
prioridade, e duas delas dependem da especialista.
