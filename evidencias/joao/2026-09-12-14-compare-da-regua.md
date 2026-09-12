# O compare da régua: o que mudou entre duas rodadas

**Data:** 12/09/2026 · **Trilho:** B2 · **Rodada:** 13 · **Commit:** este

> **Rodada de construção com piloto.** O produto é um instrumento, e o piloto
> possível hoje é compará-lo consigo mesmo: duas rodadas sobre a mesma base,
> que têm de dar **zero em tudo**. O achado da rodada não é um número da
> busca — é sobre o próprio instrumento.

## O que foi feito

O `compare` que o [B-51](../backlog.md#b-51) pedia: dadas duas rodadas da
régua, dizer o que mudou entre elas.

```bash
python scripts/run_retrieval_eval.py compare <rodada antes> <rodada depois>
```

| Peça | O que é |
|---|---|
| [`scripts/retrieval_compare.py`](../../scripts/retrieval_compare.py) | O cálculo. Módulo puro, sem rede e sem disco |
| [`scripts/retrieval_compare_report.py`](../../scripts/retrieval_compare_report.py) | O relatório. Separado do cálculo, como `retrieval_metrics` é do runner |
| `run_retrieval_eval.py compare A B` | O subcomando. Grava `compare__vs_<A>.md` e `.json` na pasta de B |

## Por que ele precisava existir agora

A [porta de decisão](../../data/curadoria/README.md) de 26/09 tem seis
critérios, e **quatro deles saem deste arquivo**. Nenhum existia: contagem de
casos que pioraram, o ímã contra o limite de um terço, casos leves acima do
corte, e a fração dos quadros novos que é de fato encontrável. Todos exigem
parear duas rodadas — nenhum sai do `metrics.json` de uma rodada só.

E a virada da base ([B-37](../backlog.md#b-37)) é o primeiro antes-e-depois
de verdade do projeto. Se ela acontecesse sem o compare, o efeito de trocar a
receita de chunking passaria sem medição — a pergunta aberta desde 07/09.

## O achado: a régua é determinística

Antes de desenhar, comparei as duas rodadas que existem sobre a mesma base
(`20260911-201429` e `20260911-202505`). **Posições e notas idênticas nos 18
casos.** Zero diferença.

Isso muda o instrumento. No runner de classificação, 2 ou 3 linhas mudam entre
sessões por ruído numérico de GPU ([B-43](../backlog.md#b-43)), e por isso o
compare de lá tem McNemar e bootstrap: é preciso separar sinal de ruído. Aqui
não há ruído a separar — a busca é uma consulta a um índice, sem geração.

**Consequência:** o compare da régua não tem estatística. Contagens e
diferenças bastam, e **um caso que piorou, piorou**. Um teste sobre 9 casos
com protocolo não teria poder nenhum, e um "p alto" seria lido como "não
mudou" quando o certo é "não dá para saber com este teste".

## Uma contradição no que já estava escrito

O B-51 dizia: *"recusa comparar quando o `cases.csv` mudou entre as duas
rodadas"*. A §4.5 do plano dizia: *"cada lote de fontes vem com 1 a 3 relatos
de régua novos"*.

As duas coisas juntas travariam o instrumento **em todo lote**, para sempre.
Eu tinha escrito as duas, em dias diferentes, e a contradição só apareceu na
hora de implementar.

A saída é a interseção dos ids — que é o que o compare da classificação já faz
desde setembro. O `SystemExit` fica para o que realmente invalida a
comparação: um caso com o mesmo id ter **outro texto** ou **outro gabarito**.
Caso novo entra como "sem antes" e vale na comparação seguinte. O B-51 foi
reescrito.

## O falso positivo que o piloto pegou

A primeira versão do bloco "gabarito a atualizar" acusou **quatro casos**
numa comparação onde nada tinha sido indexado.

Eram exatamente os quatro casos "sem cobertura" da rodada 11. Meu critério
perguntava *"apareceu algum assunto que o mapa conhece?"* — e a busca sempre
devolve cinco trechos, então num caso sem cobertura eles são todos do assunto
errado. O b12 (torção gástrica) recebia `trauma_and_bleeding` em primeiro
lugar, que é o **protocolo-ímã** do [B-02](../backlog.md#b-02), não cobertura.

Do jeito que estava, o bloco apontaria os mesmos quatro casos em toda
comparação, para sempre — e um aviso que aparece sempre deixa de ser lido. A
pergunta certa é outra: *"apareceu um assunto que **não existia na base
antes**?"*. Com isso, o bloco fica vazio quando nada foi indexado, que é o
correto.

Foi o piloto que pegou. Sem rodar, o defeito entraria no repositório com
teste verde — porque o teste que eu teria escrito testaria o critério errado.

## O que o `compare.md` traz

| Bloco | O que responde |
|---|---|
| Cabeçalho | O que mudou na base: trechos, recorte, conteúdo. Avisa quando a base é **a mesma** — aí tudo deve dar zero, e o arquivo diz isso |
| 1. Cobertura | Quais quadros do mapa têm documento **encontrável**. A distinção importa: indexado que nunca aparece no top-5 é cobertura no papel |
| 2. Ordenação | Δ Precision@1, Δ MRR, Δ Recall@5 — e a tabela caso a caso, com `melhorou` / `piorou` / `entrou` / `saiu` |
| 3. Ruído | O ímã cresceu? Mais casos passaram do corte? Algum **caso leve** passou a receber trecho? |
| 4. Gabarito a atualizar | Casos "sem cobertura" cujo assunto entrou na base. **Avisa e não edita** |
| 5. Porta de decisão | Os quatro critérios, com valor, limite e aprova/reprova |

Ele é artefato **em disco**, não saída de terminal. É o que o roteiro do
agente de ingestão exige: *"número citado aponta para o arquivo, não para a
conversa"*. O compare da classificação só imprime, e por isso nada do que ele
calcula pode ser citado numa evidência sem alguém recontar à mão.

## O piloto

Comparei as duas rodadas de 11/09, sobre a mesma base:

```
  A base é a mesma nas duas rodadas: nada foi indexado entre elas.

  ordenação : 0 melhoraram, 0 pioraram, 9 iguais
  cobertura : 7 -> 7 quadros encontráveis

  porta de decisão:
    Ordenação        passa      0 pioraram, 0 melhoraram
    Ímã              NÃO PASSA  trauma_and_bleeding em 50% dos casos
    Ruído nos leves  passa      0 caso(s) leve(s) acima do corte
    Cobertura real   passa      nenhum assunto novo nesta comparação
```

Zero em tudo, como tinha de ser. E dois números que valem registrar:

**Sete dos oito documentos são encontráveis.** O `canine_heatstroke` — o
único documento real da base, o paper de golpe de calor — **nunca aparece**
no top-5 de nenhum dos 18 casos. Ele está indexado e não muda a resposta de
ninguém. É o primeiro exemplo concreto de "cobertura no papel", e é
justamente o critério que a porta de decisão vai aplicar aos documentos novos.
Virou o [B-55](../backlog.md#b-55): pode ser só falta de caso de régua sobre o
assunto, ou pode ser que 186 trechos de fisiopatologia em inglês não sejam
recuperáveis por um relato de tutor — e as duas hipóteses pedem ações
diferentes.

**O ímã já reprova a porta hoje.** `trauma_and_bleeding` ocupa o primeiro
lugar em metade dos casos, e o limite é um terço. A base nova precisa
melhorar isso, não só crescer.

## O que mudou no repositório

| Arquivo | O quê |
|---|---|
| `scripts/retrieval_compare.py` | **novo** — o cálculo: pareamento, cobertura, ordenação, ruído, gabarito, porta |
| `scripts/retrieval_compare_report.py` | **novo** — o `compare.md`, separado do cálculo |
| `scripts/run_retrieval_eval.py` | subcomando `compare A B`; o comando antigo da régua continua igual |
| `scripts/tests/test_retrieval_compare.py` | **novo** — 23 testes, incluindo um dourado sobre a rodada citada |
| `data/retrieval/cited/20260911-202505_linha_de_base/compare__vs_…` | o piloto, versionado ao lado da rodada |
| `data/retrieval/README.md` | seção "Comparar duas rodadas" |
| `evidencias/backlog.md` | B-51 em andamento, com a trava reescrita; B-53 com a ressalva do `species` |
| `docs/plano-base-e-prova.md`, `data/curadoria/README.md` | passo 6 ✅; a trava corrigida; a porta aponta para o bloco 5 |

Testes: scripts 141 → **164**.

## Observações

**1. A ressalva do silêncio se propaga sozinha.** Quando nenhum caso passa do
corte, o bloco de ruído repete o que o `report.md` da régua já diz: zero casos
leves acima do corte é acidente, não discernimento. Sem isso, a porta
aprovaria esse critério por um motivo que não é mérito.

**2. `species` não existe na rodada.** Nem no `results.jsonl`, nem em
`/health/fingerprint`. O compare lê as fichas do disco no momento da
comparação, então a espécie que ele mostra é a de hoje. Para cobertura basta;
para "antes era X, agora é Y" em espécie, não — e o rodapé do relatório diz
isso.

**3. O `None` da posição foi o cuidado maior.** "Não apareceu entre os cinco"
tem que ordenar como pior que qualquer posição. Tratado como zero, "o
protocolo certo sumiu da lista" viraria "melhorou" — a leitura mais perigosa
que este arquivo poderia produzir. Tem teste próprio.

**4. O que falta para fechar o B-51** é o passo 0: empacotar o ciclo de
ingestão num comando. Ele depende de a ingestão poder acontecer, e entra junto
com o roteiro do agente de ingestão — pela decisão de 12/09, o roteiro só se
escreve quando der para pilotá-lo.

## Para o time

- **Vinicius:** o compare está pronto e espera a virada. Quando ela acontecer,
  ele diz o que a receita nova de chunking fez com a recuperação — a pergunta
  aberta desde 07/09. E o `canine_heatstroke` nunca aparecer no top-5 é dado
  para o re-ranking.
- **Régua:** o gabarito dos casos "sem cobertura" vai precisar de revisão
  quando os documentos novos entrarem; o bloco 4 avisa, e a decisão é do
  trilho A com a especialista.

## Deixado para depois

**O passo 0 do B-51** — `ciclo_de_ingestao.py`, junto com o roteiro do agente
de ingestão.

**Comparar sobre a base nova**, que é o piloto de verdade deste instrumento.
Depende do [B-37](../backlog.md#b-37).

## Próximo passo

**O compare espera a virada.** Ele é a última peça que o B2 podia construir
sozinho antes de a base mudar: o mapa diz o que cobrir, o pesquisador acha as
fontes, e agora existe como medir o efeito de indexá-las. O caminho até lá
está no [B-37](../backlog.md#b-37), e é do trilho A.

Do meu lado, o que anda sem depender de ninguém é a entrega 7 — o driver de
ablação, que cruza as chaves dos três trilhos e gera as tabelas do artigo.
Ele não depende do resultado de nenhum braço.
