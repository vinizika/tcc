# Evidências de desenvolvimento

Esta pasta registra **o que cada integrante fez, por quê, o que esperava e o
que de fato aconteceu**, rodada por rodada de implementação — e a fila do que
ainda falta fazer.

Não é documentação de código (essa mora no próprio código e nos `README.md`
de cada pasta) nem planejamento do time (esse mora em
[`docs/divisao-de-trabalho.md`](../docs/divisao-de-trabalho.md)). É o
registro do **percurso**: a matéria-prima da seção de resultados do TCC e o
histórico que permite responder, meses depois, "por que decidimos assim?".

## O que tem aqui

```
evidencias/
├── README.md              <- este arquivo: o padrão que todos seguem
├── backlog.md             <- a fila única de melhorias do projeto (dos três)
└── <seu-nome>/            <- uma pasta por integrante
    ├── README.md          <- índice das suas rodadas e estado atual do trilho
    ├── planejamento.md    <- onde você está, o que vem, o que está travando
    └── AAAA-MM-DD-NN-assunto.md   <- uma rodada de implementação
```

**Cada um escreve só na própria pasta** (e no `backlog.md`, que é comum).
Isso evita conflito de merge: três pessoas editando o mesmo arquivo de diário
disputariam as mesmas linhas toda semana. Hoje existe `joao/`; `ryu/` e
`vinicius/` seguem a mesma estrutura quando forem criadas.

### Os três arquivos e o papel de cada um

| Arquivo | Pergunta que responde | Quando muda |
|---|---|---|
| `<nome>/AAAA-MM-DD-NN-assunto.md` | O que aconteceu **nesta** rodada? | Começa antes de codar; fecha quando a rodada termina. Depois, não muda mais |
| `<nome>/planejamento.md` | Onde o trilho está e para onde vai? | A cada rodada concluída |
| `<nome>/README.md` | Que rodadas existem e qual é o estado? | A cada rodada concluída |
| `backlog.md` | O que está aberto no projeto, com quem, e quão urgente? | Sempre que um achado nasce ou um item muda de status |

## A dinâmica de uma rodada, passo a passo

Uma rodada é uma unidade de trabalho que produz um resultado verificável —
em geral, uma entrega ou um experimento. Ela pode ter mais de um commit.

1. **Antes de codar, crie o arquivo da rodada** em `<seu-nome>/` com o nome
   `AAAA-MM-DD-NN-assunto.md`, onde `NN` é o número sequencial (assim os
   arquivos ficam em ordem cronológica mesmo com várias rodadas no mesmo
   dia). Preencha **já** as seções "O que foi feito" (o plano), "Por quê",
   "Decisões desta rodada" e, principalmente, **"Resultado esperado"**.
2. **Escreva o esperado antes de medir.** Depois do resultado, é fácil se
   convencer de que era o que se previa. O valor científico do registro está
   na diferença entre os dois — inclusive quando a previsão erra feio (ver a
   [rodada 4 do João](joao/2026-09-04-05-runner-de-avaliacao.md), em que as
   duas previsões principais estavam erradas e isso virou o achado).
3. **Durante o trabalho, anote o que "pescar" de passagem** — comportamento
   estranho, oportunidade, algo do trilho de outra pessoa. Vai para
   "Observações".
4. **Ao medir, registre o obtido com o número da régua.** As réguas do time
   são o runner de avaliação (`data/evaluation/`, trilho B2) e a régua de
   recuperação (trilho A). Se a rodada rodou uma avaliação, promova-a com
   `python scripts/report_evaluation.py cite <rodada>` e cole o trecho que
   ele imprime — assim o número tem os dados que o produziram.
5. **Ao terminar, feche o arquivo:** "O que mudou no repositório" com os
   commits, "Deixado para depois" com o que foi adiado e por quê, "Próximo
   passo".
6. **Leve para o `backlog.md`** toda observação que exija ação de alguém —
   sua ou de outro trilho. Uma observação anotada vira pauta; uma só falada
   se perde. O item do backlog aponta para a rodada onde nasceu.
7. **Atualize seu `planejamento.md`** (entrega concluída, próxima, bloqueios)
   e a tabela de rodadas do seu `README.md`.

Com isso, quem chega depois lê o `README.md` da sua pasta para saber o estado,
o `planejamento.md` para saber o rumo, e a rodada para saber o detalhe.

## O padrão de cada rodada

```markdown
# Título da rodada

**Data** · **Trilho** · **Commits:** lista dos commits

## O que foi feito
Descrição objetiva da mudança.

## Por quê
O problema concreto que isso resolve. Sem esta seção o registro não serve
para o TCC: é ela que liga a implementação à motivação do projeto.

## Decisões desta rodada
As escolhas feitas no caminho, cada uma com o motivo. Uma tabela
"decisão | motivo" basta. Isto vale tanto quanto os números: daqui a dois
meses, na escrita, ninguém lembra por que um limiar é 0.7 ou por que a
temperatura é zero, e refazer o raciocínio custa mais do que anotá-lo.

## Resultado esperado
O que achávamos que ia acontecer, escrito **antes** de medir.

## Resultado obtido
O que aconteceu, com números sempre que houver medição.
Resultado negativo também é resultado: registrar quando não funcionou.

## O que mudou no repositório
Arquivos tocados e o link do commit, para qualquer afirmação acima poder
ser conferida no código.

## Observações
O que foi notado de passagem: comportamento estranho, oportunidade de
melhoria, algo que afeta o trilho de outra pessoa. Não precisa ser
conclusivo — precisa ficar registrado. O que exigir ação vai também para
o backlog.md, com link para esta rodada.

## Deixado para depois
O que foi adiado de propósito, por quê, e o que faria voltar. Uma decisão
de adiar é decisão; sem registro, o item some.

## Próximo passo
O que esta rodada puxa em seguida.
```

## Três regras

1. **Escrever o "esperado" antes de medir.** Depois do resultado, é fácil
   convencer a si mesmo de que era o que se previa. O valor científico do
   registro está justamente na diferença entre os dois.
2. **Número sempre que houver medição.** Sem número, é opinião. E o número
   vem com a rodada que o produziu, promovida para `data/evaluation/cited/`.
3. **Uma mudança por rodada.** Duas mudanças juntas e o resultado não diz
   qual delas causou o quê. Quando não der para separar, dizer isso.

## O `planejamento.md` de cada trilho

Serve de controle para o time e o orientador acompanharem sem ler commits.
Deve ter, nesta ordem:

- **Objetivo do trilho** e os números de referência atuais.
- **Onde estou**: tabela das entregas com situação.
- **Próxima entrega**: o problema que resolve, o que vai fazer, como será
  medido.
- **Marcos** do cronograma.
- **O que está travando**: só os itens que travam **este** trilho, uma linha
  cada, com data, origem e link para o item do `backlog.md`, onde mora o
  detalhe. Esta seção **só cresce**: um bloqueio entra e permanece até o
  trilho responsável resolvê-lo — então vai para "Resolvidos", com a data.
  Nada é apagado ou substituído.
- **Fora do escopo** deste trilho.

O do João está em [`joao/planejamento.md`](joao/planejamento.md) e serve de
modelo.

## Relação com o estudo de ablação

Estas evidências **complementam** o estudo de ablação previsto no artigo, mas
não o substituem. O estudo formal é a matriz sistemática — cada componente
ligado e desligado contra o dataset completo — e roda em outubro. As evidências
contam a história das decisões que levaram até lá.

## Relação com `docs/`

- [`docs/divisao-de-trabalho.md`](../docs/divisao-de-trabalho.md): quem faz
  o quê, marcos, acordos de trabalho.
- [`docs/CONTRATOS.md`](../docs/CONTRATOS.md): as interfaces entre os
  trilhos. Só interfaces — pendências ficam no `backlog.md`.
- [`docs/anotacoes.md`](../docs/anotacoes.md): o diário do início do projeto,
  anterior a esta pasta. Histórico; novas anotações vão para a rodada de quem
  as fez.
