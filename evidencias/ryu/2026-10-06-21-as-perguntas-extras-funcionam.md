# As perguntas extras levam à resposta certa?

**Data:** 06/10/2026 · **Trilho:** B1 (Consulta, frente prova) · **Rodada:** 21 · **Commit:** este

## O que foi feito

Quando a IA responde INCERTO, o app do Vinicius faz **uma pergunta objetiva**
ao tutor (de um catálogo fixo de 16) e, se a conversa não avança, oferece um
**formulário com opções**; a cada resposta, a IA decide de novo
([`docs/pre-triagem-conversacional.md`](../../docs/pre-triagem-conversacional.md)).
O Vinicius mediu o mecanismo com 8 diálogos sintéticos, respondidos à mão
(rodadas 17 e 20 dele). Esta rodada mede **se as perguntas trazem a informação
que decide o caso**, com um **tutor simulado**:

- o tutor simulado (Gemini) recebe o **relato completo** de um caso da
  calibração da prova 2, que o sistema **não vê**;
- ele abre a conversa com **uma frase vaga** ("meu gato está estranho"), sem os
  sinais importantes;
- a cada pergunta do app, responde **só com fatos do relato completo**, ou "não
  sei, não reparei" quando o relato não diz; no formulário, escolhe a opção que
  bate com o relato, ou "Não observei";
- o sistema do outro lado é o **workspace de verdade** (`WorkspaceService`:
  classificação, seleção de pergunta, formulário e os limites do app), gravando
  num banco do MongoDB separado (`tcc_conversa_simulada_ryu_20261006`).

Casos: 8 emergências e 8 não emergências da calibração da prova 2 (sorteio
fixo, semente `conversa-2026-10-06`) e os 2 INCERTO dela (relatos que, de fato,
não têm informação suficiente). Lista em
[`dados/2026-10-06-casos-conversa-simulada.json`](dados/2026-10-06-casos-conversa-simulada.json).

## Por quê

Ponto 3 da lista combinada com o Ryu em 06/10. O cenário do projeto diz "se
precisar de mais contexto, ele deve pedir". Pedir já funciona; o que ninguém
mediu é se **o que ele pede** é o que falta para decidir.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | O tutor simulado só responde com o que está no relato completo | Isola a qualidade da **pergunta**: se a resposta certa não aparece, é porque a pergunta não foi atrás do fato que existia |
| 2 | Relatos da calibração da prova 2 | Rótulos validados pela ASAVET, e a calibração pode ser usada à vontade. O teste não é tocado |
| 3 | A abertura vaga é escrita pelo Gemini, a partir do relato completo | Ninguém do time escreve a abertura sabendo o que o sistema vai perguntar. Se a abertura vazar o sinal decisivo e a IA decidir no primeiro turno, isso fica registrado como tal |
| 4 | O mesmo modelo faz o papel de tutor e de atendente | Limitação declarada: é o único gerador disponível com cota; um tutor humano responde pior (esquece, exagera) |

## Resultado esperado

_Escrito antes de rodar._

- **Abertura:** espero INCERTO no primeiro turno na maioria dos 18 (é para isso
  que ela é vaga), em pelo menos 12.
- **Ao fim da conversa,** nas 16 emergências e não emergências: espero a classe
  certa em **pelo menos 12 de 16**, com **nenhuma emergência rebaixada a
  NAO_EMERGENCIA**. A referência é o relato completo dado de uma vez, em que o
  Gemini acertou 16 de 16 destes casos na rodada 18 (o q186 e o q118, que ele
  errou, não estão no sorteio).
- **Nos 2 INCERTO verdadeiros:** espero que a conversa termine **sem inventar
  uma classe** (INCERTO, ou o estado "informação insuficiente").
- **Custo:** espero de 1 a 3 perguntas por conversa.

**Critério de "as perguntas funcionam":** ≥ 12 de 16 certos ao fim, 0
emergências rebaixadas a NAO_EMERGENCIA e os 2 INCERTO verdadeiros sem classe
inventada.

## Resultado obtido

`python /tmp/experimento_conversa_simulada.py rodar` no container, 18 conversas,
todas concluídas sem erro; o diálogo inteiro de cada uma em
[`dados/2026-10-06-conversa-simulada-resultados.jsonl`](dados/2026-10-06-conversa-simulada-resultados.jsonl).

| Grupo | Começou INCERTO | Classe certa ao fim | Perguntas por conversa |
|---|---|---|---|
| Emergências (8) | 3 | **7** | 0 a 2 |
| Não emergências (8) | 3 | **6** | 0 a 3 |
| INCERTO verdadeiros (2) | 2 | **2** (terminaram em "informação insuficiente") | 2 e 3 |

| Parte do critério | Resultado | |
|---|---|---|
| ≥ 12 de 16 certos ao fim | 13 de 16 | ✅ |
| Nenhuma emergência rebaixada a NAO_EMERGENCIA | **1** (q180) | ❌ |
| Os 2 INCERTO verdadeiros sem classe inventada | 2 de 2 | ✅ |

**O critério não passa** por um caso, e o resultado esperado da abertura também
errou: só 8 de 18 conversas começaram INCERTO (eu esperava ≥ 12). Nas outras
10, a abertura do tutor simulado já bastou para a IA decidir no primeiro turno,
sem nenhuma pergunta.

### Quando a pergunta acontece, ela funciona para emergências

As 3 emergências que começaram INCERTO terminaram EMERGENCIA, com 1 ou 2
perguntas. Exemplo, a piometra (q245): a abertura "umas coisas estranhas
saindo dela" virou INCERTO; o app perguntou o **aspecto da secreção** ("meio
marrom amarelado, grosso e fede muito") e **quando começou** ("saiu do cio tem
tipo um mês"); a IA concluiu EMERGENCIA. É exatamente o comportamento do
cenário do projeto.

### O erro grave: decidir sem perguntar

**q180 — corpo estranho, EMERGENCIA.** A abertura foi "Oi, meu cachorro tá
vomitando e eu tô preocupado." A IA respondeu **NAO_EMERGENCIA no primeiro
turno, sem fazer nenhuma pergunta**, e a conversa terminou. O relato completo,
que o sistema nunca soube, tinha vômito 6 vezes desde ontem, inclusive água, 2
dias sem fazer cocô com esforço, posição de reza e uma meia sumida. O catálogo
tem justamente a pergunta que mudaria tudo ("Quantas vezes ele vomitou?"), mas
a pergunta só é feita quando a classe é INCERTO, e a IA deu uma classe a uma
frase que não permitia nenhuma.

É o espelho do problema que o Ryu definiu em 06/10 ("INCERTO só quando falta
informação"): aqui faltava informação e o sistema **não** disse INCERTO. Entre
as 10 conversas decididas no primeiro turno, há outras aberturas tão vagas quanto
("meu cachorro tá comendo menos", "meu cachorro está se coçando todo"), que
acertaram NAO_EMERGENCIA, mas sem saber há quanto tempo nem o que mais havia.
Isso é da decisão (prompt de triagem, trilho B2), não das perguntas.

### Quando a pergunta não serve, a conversa termina sem conclusão

Os dois leves que terminaram em "informação insuficiente" mostram o limite do
catálogo de 16 perguntas ([B-79](../backlog.md#b-79)):

- **q153 — picada de vespa na pata, só um inchaço local.** O app perguntou da
  respiração ("respirando normal") e depois "como ele está andando?", que o
  relato não diz. O que decidiria o caso (o inchaço ficou só ali? há inchaço na
  cara?) não tem pergunta no catálogo.
- **q269 — parto normal em andamento.** O app perguntou "quando você percebeu
  essa mudança?". O tutor simulado respondeu "não sei" — **erro do simulador**,
  porque o relato diz "começou a parir às 5h". Mas, mesmo com a resposta, o que
  decide um parto (intervalo entre filhotes, se mamam, se a mãe faz força sem
  sair nada) não está no catálogo.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/experimento_conversa_simulada.py` | **novo** — o tutor simulado contra o `WorkspaceService` real |
| `evidencias/ryu/dados/2026-10-06-casos-conversa-simulada.json`, `…-conversa-simulada-resultados.jsonl` | **novos** — os casos e os diálogos |

O banco `tcc_conversa_simulada_ryu_20261006` fica no MongoDB local, separado do
banco do app (`vetai`).

## Observações

**1. O tutor simulado é um modelo, e erra.** No q269 ele disse "não sei" a uma
pergunta que o relato respondia. Um tutor humano também erra, de outro jeito
(esquece, exagera, responde outra coisa). O experimento mede o caminho do
sistema, não a conversa com uma pessoa.

**2. A abertura vaga foi menos vaga que o pedido.** Das 5 emergências decididas
no primeiro turno, 4 aberturas já carregavam o sinal grave ("gengiva meio
branquinha e espirrou sangue", "caiu da janela", "tremendo e babando desde
ontem", "filhote tremendo e meio molinho") e foram decididas certo; o q180 é a
exceção. Das 5 leves, duas eram leves por natureza (bafo, carrapatos sem sinais)
e três eram vagas ("comendo menos", "se coçando todo", "uma bolinha na barriga"):
acertaram NAO_EMERGENCIA sem perguntar nada.

## Deixado para depois

- **A decisão não deve dar classe a uma frase sem informação** (q180): levar ao
  João (prompt de triagem, B2). Um teste barato seria uma lista de aberturas
  vagas ("está vomitando", "está mancando", "está estranho") em que a resposta
  esperada é sempre INCERTO.
- **O catálogo de perguntas** (B-79): faltam perguntas para inchaço local e para
  parto; levar ao Vinicius, com a validação veterinária que o B-79 já pede.

## Próximo passo

Levar ao time os dois achados. Juntos com a rodada 19, eles mostram os dois
lados do mesmo objetivo: o sistema às vezes diz "não sei" quando sabia (ficha
errada) e às vezes decide quando não sabia (abertura vaga).
