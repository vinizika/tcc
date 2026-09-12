# O pesquisador: o agente que decide o que entra na base

**Data:** 12/09/2026 · **Trilho:** B2, para a frente base · **Rodada:** 12 ·
**Commit:** este

> **Rodada de construção com piloto.** O produto é um roteiro, um script e uma
> linha do mapa levada de ponta a ponta. Não há esperado × obtido de acurácia;
> os números aqui são de captura e de recorte — e o achado principal é sobre
> **quais fontes existem**, que nenhum de nós sabia.

## O que foi feito

O agente que, para cada linha do [mapa de assuntos](../../data/curadoria/README.md),
acha as fontes, julga se servem, captura o texto e deixa a pergunta pronta
para o especialista. Três peças:

| Peça | O que é |
|---|---|
| [`agentes/pesquisador.md`](../../agentes/pesquisador.md) | O roteiro: onde procurar, como julgar, nove passos, o que ele não faz |
| [`scripts/capturar_fonte.py`](../../scripts/capturar_fonte.py) | A captura determinística — baixa, extrai o texto principal, grava com hash e monta a ficha. 28 testes, sem rede |
| [`data/curadoria/fontes/`](../../data/curadoria/fontes/README.md) | Onde o trabalho mora: o dossiê por quadro, as capturas e a mesa dos especialistas |

E o piloto: a linha `gastric_dilatation_volvulus` (torção gástrica) levada do
início ao fim.

## O achado que muda a frente base

Procurei a fonte ideal — **autoritativa, em português, escrita para tutor**.
Ela não existe em volume. O que existe:

| O que procurei | O que achei |
|---|---|
| MSD Manual Veterinário "em português" | **Traduz os títulos e deixa o corpo em inglês.** Vale para as duas versões, profissional e para tutores. Não é fonte em PT |
| Fonte em PT com autoridade | Existe, e é **acadêmica**: artigos do SciELO, Cadernos Técnicos da UFMG, repositórios de universidades. Falam de fisiopatologia e cirurgia, não do que o tutor vê |
| Fonte em PT para tutor | Existe, e é **comercial**: clínicas 24 h, portais de ração. Autoridade baixa |
| Fonte para tutor com autoridade | Existe, e está **em inglês**: PDSA, VCA, Cornell, MSD owner, International Cat Care |
| Lista brasileira de triagem para tutores (CFMV, CRMV, hospital universitário) | **Não achei.** O que o CFMV publica é a definição normativa de urgência e emergência |

O sistema recebe relato em português de tutor. O embedder é multilíngue.
**Ninguém sabe se ele prefere a língua certa com o registro errado, ou o
registro certo na língua errada** — e essa é uma pergunta de engenharia, não
de curadoria.

**A saída adotada:** cada linha coleta **as duas naturezas** — uma fonte em PT
com autoridade e uma em EN para tutor — com `language` e `register` marcados
na ficha. A régua de recuperação diz qual delas a busca encontra. Isso
transforma a etapa 1 num **experimento de idioma × registro**, e a porta de
decisão de 26/09 passa a ter uma pergunta a mais para responder, com dado.

Se a resposta for "a busca nunca encontra a fonte em português", isso é
resultado, não fracasso: significa que o caminho é o
[redator de lacuna](../../agentes/README.md) — o time escrevendo em português
a partir das fontes — e o projeto saberá disso com número, não por intuição.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **O agente lê para julgar; um script captura para guardar** | O que um modelo devolve de uma página é o que ele entendeu dela. Indexar isso faria a base ser paráfrase — o oposto da decisão de usar fontes originais |
| 2 | **O especialista aprova um arquivo com hash e data**, não uma URL | A página pode mudar amanhã. O que ele aprovou tem de ser o que será indexado |
| 3 | **Duas fontes por linha, de naturezas opostas** | Ver o achado acima |
| 4 | **Curadoria por seção**: sinais e urgência entram; tratamento, cirurgia e dose ficam de fora | O sistema orienta a procurar atendimento, não a tratar em casa. E menos trecho irrelevante competindo na busca |
| 5 | **Todo "sim" da régua de aptidão carrega uma citação literal** | Sem a frase, "responde o discriminador: sim" é opinião. É a mesma disciplina do mapa |
| 6 | **Fonte que não abriu nunca é primária** | AVMA, AAHA e International Cat Care bloqueiam leitura automatizada. A linha existe; quem abre é uma pessoa |
| 7 | **Estado novo: `fonte_encontrada`** | O painel precisa distinguir "ninguém procurou" de "achou e está na mesa de alguém" |
| 8 | **Os casos da régua são escritos antes da primeira busca** | Relato escrito depois de ler a fonte copia a linguagem dela, e a busca acerta por eco. É a muralha aplicada ao pesquisador |
| 9 | **O pesquisador para em `fonte_encontrada`** | Aprovar é do especialista; indexar é do agente de ingestão |

## O piloto: torção gástrica

A primeira linha da fila — prioridade A, sem documento, com o caso b12 da
régua esperando desde a rodada 11. O dossiê completo, com as citações, está em
[`fontes/gastric_dilatation_volvulus.md`](../../data/curadoria/fontes/gastric_dilatation_volvulus.md).

| | PDSA (EN, tutor) | Ciência Rural 2012 (PT, acadêmico) |
|---|---|---|
| Cobre os sinais | **sim** — "Retching or unproductive vomiting" | **parcial** — sinais de exame, não o que o tutor vê |
| Responde o discriminador | **sim** — "Bloat (swollen tummy) – this is not always obvious" | **não** |
| Diz quando ir | **sim** — "Contact your vet straight away" | parcial |
| Palavras | 1.189 | 5.745 |
| Seções indexadas | 4 de 6 | 1 de 16 |
| **Trechos** | **9** | **29** |
| Recomendação | primária | complementar |

### Duas armadilhas que o piloto pagou para descobrir

**1. Declarar seção a partir do resultado de busca não funciona.** Declarei
`"When to contact your vet"` porque o buscador dizia que existia. No texto
capturado, não existe — a página tem `Overview`, `What is GDV?`,
`Which dogs are most at risk of GDV?`, `GDV Symptoms`. O ingestor ignora uma
seção declarada que não encontra, **em silêncio**, e a curadoria teria saído
diferente do que eu pensava. Virou regra no passo 6 do roteiro: as seções se
declaram lendo o arquivo capturado.

**2. Declarar só o que entra faz a seção engolir o documento.** O artigo do
SciELO, com `include_sections` apontando só para a seção de definição,
produziu **217 trechos** — de fisiopatologia, tratamento conservador e
cirurgia. O motivo: o ingestor só enxerga um heading que a ficha declarou, e
os 15 seguintes não estavam lá; sem limite, a seção desejada continuou até o
fim do arquivo. Declarando os 15 em `exclude_sections`, caiu para **29**.

Essa segunda é a mais séria: 217 trechos de conteúdo cirúrgico entrando na
base é exatamente o ruído que a [rodada 10](2026-09-12-10-corte-de-relevancia.md)
mediu custando 22 emergências rebaixadas. E não havia erro visível — só
muitos trechos.

### Custo por linha: o que dá para contar, e o que não dá

**Contado:** 3 buscas na web · 5 páginas abertas, das quais 4 responderam ·
2 fontes escolhidas · 3 capturas (a da PDSA refeita depois do erro de seção) ·
2 inspeções mais 2 diagnósticos · 1 dossiê escrito.

**Não medido: o tempo.** Não cronometrei, e o relógio de uma sessão de agente
com chamadas em paralelo não é o de uma pessoa fazendo o mesmo trabalho. Uma
estimativa a partir de uma única linha — ainda por cima uma que tinha fonte
sobrando — não sustentaria a projeção para 31.

Então o eixo "velocidade" da [porta de decisão](../../data/curadoria/README.md)
**ainda não tem número**, e o critério dele não é tempo: é quantas das 31
linhas chegaram a `fonte_aprovada` ou `indexada` até 26/09. Essa contagem sai
da coluna `cobertura` do mapa, e é ela que decide.

O que o piloto permite dizer sobre esforço é qualitativo, e já é útil: o que
custou não foi achar candidatas — foi **abrir cada uma e conferir o corpo da
página**, que é onde as duas armadilhas apareceram. Linhas com fonte já em
`referencias.md` devem custar menos; linhas sem fonte em português, mais, e o
custo delas é de decisão, não de busca.

## O que o piloto não fez

**Não indexou nada.** As capturas estão em
`data/curadoria/fontes/capturas/`, e a pasta da base segue com os mesmos oito
documentos. A cópia temporária para rodar `--inspect` foi desfeita, e
conferi: `backend/data/documents/` está intacta.

**Não aprovou nada.** As duas fichas dizem
`validation_status: pending_specialist`, e a linha do mapa está em
`fonte_encontrada` — não em `fonte_aprovada`.

**Não mexeu no `cases.csv`.** O caso b12 continua marcado "sem cobertura", o
que é verdade hoje. Quando a linha for indexada, ele precisa virar "com
protocolo" com `expected_topics = gastric_dilatation_volvulus`; está anotado
no dossiê, e o `compare` ([B-51](../backlog.md#b-51)) avisa.

## Observações

**1. A captura é uma peça de método, não de infraestrutura.** Ela existe para
que a frase "a base é feita de fontes originais" continue verdadeira quando um
agente estiver no meio do caminho. O hash na ficha é o que liga a aprovação do
especialista a um texto específico.

**2. O corte de tratamento e dose é uma decisão de produto.** Nenhuma fonte
entra inteira: as seções de conduta ficam de fora de propósito. Vale o
especialista concordar explicitamente — está na terceira pergunta de
`PARA-VALIDAR.md`.

**3. O `--inspect` é a rede de segurança.** As duas armadilhas do piloto só
apareceram porque ele foi rodado antes de qualquer decisão. Um documento que
produz 217 trechos em vez de 29 não dá erro — só polui a base. O número de
trechos virou item de conferência no roteiro.

**4. Os vocabulários das fichas ainda não estão no README da base.**
`document_type`, `validation_status` e `register` são validados hoje pelo
script de captura. O trilho A pode formalizá-los quando quiser
([B-03](../backlog.md#b-03), nota de 12/09).

**5. Uma dependência nova.** `trafilatura`, em `scripts/requirements.txt` —
extrai o texto principal de uma página sem menu, rodapé nem banner de cookie.
Roda fora do Docker, é pura Python, e não toca no backend.

## Adendo de 12/09 — o que o teste de estresse achou

Depois de escrever o roteiro, submeti a captura a entradas que o mundo real
produz. **Sete falhas**, e o script passava em todas em silêncio:

| O que eu joguei nele | O que acontecia | Agora |
|---|---|---|
| Página em **Latin-1** | "Sinais clínicos" virava "Sinais cl�nicos", sem erro nenhum | Decodifica pelo charset do header, pelo `<meta>` do HTML, ou tentando — e confere se o resultado tem cara de texto |
| Página em Latin-1 **com charset declarado** | Idem: eu ignorava o cabeçalho | Idem |
| **404 disfarçado** ("Página não encontrada") | Virava documento de 3 palavras | Recusa abaixo de 50 palavras; avisa abaixo de 150 |
| HTML que o servidor **anuncia como PDF** | Virava `.pdf` de 0 palavras | Recusa: confere os bytes `%PDF-` |
| **Seção declarada que não existe** | Passava — é a armadilha nº 1 do piloto | Recusa, listando as ausentes |
| Seção declarada **sem um acento** | Idem, e é a variante mais sutil | Recusa |
| **Título de 25 palavras** | Passava, e era cobrado em todo trecho | Recusa acima de 6 |
| **Recapturar com o mesmo nome** | Sobrescrevia em silêncio | Recusa; `--forcar` quando for de propósito |

A da codificação é a mais séria para este projeto: material de universidade e
de conselho regional brasileiro costuma estar em Latin-1, e é exatamente a
fonte em português que mais nos falta. Os quatro testes de codificação
produzem hoje **o mesmo hash** — que é a prova de que a normalização funciona,
e de que a aprovação do especialista não depende de qual servidor entregou a
página.

**Uma trava nova que o piloto não tinha como pedir:** o script agora **avisa**
quando o idioma declarado na ficha não parece o do corpo. É a armadilha do
MSD, e uma ficha errada nesse campo faria o experimento de idioma × registro
medir outra coisa. Avisa, não recusa — a heurística não é boa o bastante para
decidir sozinha.

**O que o endurecimento não mudou:** a captura do piloto, refeita com todas as
travas, saiu byte a byte idêntica (`b049102f`). As travas recusam entrada
ruim; não transformam entrada boa.

### E uma lacuna no roteiro, não no script

Testei o roteiro contra uma linha **leve** (`single_vomiting_or_mild_diarrhea`)
e ele não servia: as famílias de busca estavam todas orientadas a emergência, e
ninguém escreve artigo sobre "vomitou uma vez e está bem". Onze das 31 linhas
da etapa 1 são assim. O roteiro ganhou uma seção com três ajustes: buscar pela
**queixa** e não pelo quadro; capturar a **mesma página duas vezes**, com
seções diferentes, para a linha leve e para a grave (a página "Vomiting in
dogs" da PDSA cobre as duas); e inverter o critério "diz quando ir" — numa
linha leve, o que importa é a fonte dizer **quando pode esperar**. Uma página
que só lista alarme ensina o sistema a ter medo de tudo, que é o defeito que o
[B-03](../backlog.md#b-03) descreve.

O roteiro também ganhou a tabela **"o que o script recusa, e o que só você
pega"** — porque metade do que dá errado continua fora do alcance dele: fonte
de autoridade baixa disfarçada de boa, conteúdo certo sobre a espécie errada,
e o limite de seção não declarado, que só o `--inspect` revela.

Testes: 124 → **138**.

## Deixado para depois

**Rodar o pesquisador nas outras 30 linhas da etapa 1**, por sistema orgânico,
na ordem da prioridade. É a fila, e ela começa agora.

**O Caderno Técnico nº 87 da UFMG** (Emergência em Medicina Veterinária) — a
melhor candidata institucional brasileira, com PDF acima de 10 MB que a
leitura automatizada não abriu. Vale alguém baixar à mão: se ele servir, muda
o quadro do achado principal para vários quadros de uma vez.

**O roteiro da ingestão** e o [`compare`](../backlog.md#b-51), que fecham o
ciclo e alimentam a porta de decisão.

## Próximo passo

As fontes da torção gástrica estão prontas para a mesa. Do meu lado, a fila
continua: `fading_neonate`, `acute_hindlimb_paralysis` e os três tóxicos
brasileiros são as próximas linhas A sem documento.
