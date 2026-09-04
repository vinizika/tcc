# docs/

Documentos do time: quem faz o quê, como as partes se encaixam, e o diário do
início do projeto. O registro do que acontece rodada a rodada **não** fica
aqui — fica em [`evidencias/`](../evidencias/README.md).

| Arquivo | O que é | Quando consultar | Quem edita |
|---|---|---|---|
| [`divisao-de-trabalho.md`](divisao-de-trabalho.md) | A divisão em três trilhos (A, B1, B2), o que cada um possui, os acordos de trabalho, o cronograma até novembro e o diagnóstico inicial do código | Para saber de quem é uma pasta, o que está fora do seu escopo, ou quando é cada marco | Qualquer um, em acordo dos três |
| [`CONTRATOS.md`](CONTRATOS.md) | As interfaces entre os trilhos: o formato do que a busca devolve, o JSON da resposta de triagem, as chaves de liga/desliga e os endpoints | Antes de mudar algo que outro trilho consome. Mudança aqui vai em commit separado, avisando o dono do outro lado | O dono do lado que muda |
| [`anotacoes.md`](anotacoes.md) | O diário do início do projeto (abril a agosto): dados, primeiras métricas, handovers | Para entender de onde vieram o dataset, o data augmentation e os 70,41% de 04/05 | Histórico — não editar; registros novos vão para `evidencias/` |

## Onde fica o quê, no projeto inteiro

| Pergunta | Onde |
|---|---|
| Como subir e usar o sistema? | [`README.md`](../README.md) da raiz |
| De quem é este arquivo? O que é o meu escopo? | `divisao-de-trabalho.md` |
| Que formato a API devolve? Que chaves existem? | `CONTRATOS.md` |
| O que foi feito, por quê, e o que se mediu? | [`evidencias/<nome>/`](../evidencias/README.md) |
| O que está aberto, com quem, e quão urgente? | [`evidencias/backlog.md`](../evidencias/backlog.md) |
| Onde cada trilho está e para onde vai? | `evidencias/<nome>/planejamento.md` |
| Como medir o sistema e ler os números? | [`data/evaluation/README.md`](../data/evaluation/README.md) |
| De onde vêm os dados e o que cada arquivo é? | [`data/README.md`](../data/README.md) |
| O que faz cada script e como rodar? | [`scripts/README.md`](../scripts/README.md) |
