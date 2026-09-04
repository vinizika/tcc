# Evidências de desenvolvimento

Esta pasta registra **o que cada integrante fez, por quê, o que esperava e o
que de fato aconteceu**, rodada por rodada de implementação.

Não é documentação de código (essa mora no próprio código e no `README.md`) nem
planejamento (esse mora em [`docs/divisao-de-trabalho.md`](../docs/divisao-de-trabalho.md)).
É o registro do **percurso**: a matéria-prima da seção de resultados do TCC e o
histórico que permite responder, meses depois, "por que decidimos assim?".

## Organização

```
evidencias/
├── README.md            <- este arquivo
├── joao/
│   ├── README.md        <- índice das rodadas + estado atual do trilho
│   └── AAAA-MM-DD-NN-assunto.md
├── ryu/
└── vinicius/
```

Cada um escreve **só na sua pasta**. Isso evita conflito de merge: três pessoas
editando o mesmo arquivo de diário disputariam as mesmas linhas toda semana.

## O padrão de cada rodada

Um arquivo por rodada de implementação, nomeado `AAAA-MM-DD-NN-assunto.md`,
onde `NN` é o número sequencial da rodada — assim os arquivos ficam em ordem
cronológica mesmo quando há mais de uma rodada no mesmo dia.
O conteúdo segue sempre a mesma estrutura:

```markdown
# Título da rodada

**Data** · **Trilho** · **Commits:** lista dos commits

## O que foi feito
Descrição objetiva da mudança.

## Por quê
O problema concreto que isso resolve. Sem esta seção o registro não serve
para o TCC: é ela que liga a implementação à motivação do projeto.

## Resultado esperado
O que achávamos que ia acontecer, escrito **antes** de medir.

## Resultado obtido
O que aconteceu, com números sempre que houver medição.
Resultado negativo também é resultado: registrar quando não funcionou.

## O que mudou no repositório
Arquivos tocados e o link do commit, para qualquer afirmação acima poder
ser conferida no código.

## Próximo passo
O que esta rodada puxa em seguida.
```

## Três regras

1. **Escrever o "esperado" antes de medir.** Depois do resultado, é fácil
   convencer a si mesmo de que era o que se previa. O valor científico do
   registro está justamente na diferença entre os dois.
2. **Número sempre que houver medição.** As réguas do time são a régua de
   recuperação (trilho A) e o runner de métricas de classificação (trilho B2).
   Sem número, é opinião.
3. **Uma mudança por rodada.** Duas mudanças juntas e o resultado não diz qual
   delas causou o quê.

## Relação com o estudo de ablação

Estas evidências **complementam** o estudo de ablação previsto no artigo, mas
não o substituem. O estudo formal é a matriz sistemática — cada componente
ligado e desligado contra o dataset completo — e roda em outubro. As evidências
contam a história das decisões que levaram até lá.
