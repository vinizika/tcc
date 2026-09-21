# Adaptando o runner para a prova nova, reaproveitando o do Vinicius

**Data:** 21/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 10 · **Commit:** este

## O que foi feito

O plano original (`docs/plano-base-e-prova.md`, seção 5.4) previa escrever um
runner novo para a prova em português, com coluna alternativa, `--relato-lang`
e baselines triviais. Antes de fazer isso, chequei o que o Vinicius já tinha
construído na leva de 20/09: [`scripts/run_map_triage_eval.py`](../../scripts/run_map_triage_eval.py)
já lê relato livre em português direto de um CSV (`text`/`expected_class`/`id`)
e chama `/chat/` com as mesmas opções que o resto do time usa — exatamente o
que a entrega 6 do meu planejamento pedia, só que escrito para outro
propósito (avaliar a régua de recuperação, não a prova de classificação).

Em vez de duplicar essa lógica num script paralelo, estendi o dele:

- `--cases`: aponta para qualquer CSV com as colunas esperadas — antes era
  fixo em `data/retrieval/cases.csv`. Sem o argumento, continua exatamente
  como estava (retrocompatível com o uso que o trilho A já faz).
- `--split`: filtra por uma coluna `split` quando ela existe no arquivo — a
  régua não tem essa coluna, a prova nova tem (`calibracao`/`dev`/`teste`).
  Sem o argumento, roda tudo, como antes.
- `--runs-dir`: separa os resultados da prova (`data/evaluation/prova_runs/`)
  dos resultados da régua (`data/evaluation/map_runs/`), para as duas
  frentes não se misturarem na mesma pasta.
- O manifesto passou a registrar `cases_file`, `split` e `case_count`, para
  qualquer rodada futura dizer sozinha contra qual arquivo e recorte rodou.

## Por quê

Escrever um runner do zero para fazer basicamente a mesma coisa que já
existia seria dívida técnica no nascimento: dois lugares para manter a
lógica de chamar `/chat/`, calcular acurácia balanceada e gravar manifesto —
e o time já tinha resolvido isso bem. O usuário confirmou explicitamente
essa direção ("vamos com o que o Vinicius fez") depois de eu apontar a
sobreposição.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Estender o script do Vinicius em vez de copiar e adaptar | Reduz a superfície de manutenção a um lugar só; qualquer melhoria futura na lógica de avaliação (do B2 ou do trilho A) beneficia as duas frentes |
| 2 | Todo argumento novo é opcional com default igual ao comportamento antigo | O script continua servindo o uso original do trilho A (régua de recuperação) sem nenhuma mudança de comportamento |
| 3 | Não escrevi baselines triviais nesta rodada | Não há lote oficial ainda (só os 18 casos de calibração) — calibrar um baseline de saco de palavras com 18 linhas não sustenta nada; fica para quando o lote de ~150 existir |

## Resultado esperado

_Escrito antes de rodar._ Esperava que o script adaptado lesse
`data/prova/casos_calibracao.csv`, filtrasse só `split=calibracao`, e
gravasse a rodada em `data/evaluation/prova_runs/` sem tocar o
comportamento default do script.

## Resultado obtido

Rodei como fumaça (`--mode no_rag --limit 3 --split calibracao`) contra os
3 primeiros casos do lote de calibração:

```
[ 1/3] p01 EMERGENCIA -> EMERGENCIA ctx=0
[ 2/3] p02 NAO_EMERGENCIA -> NAO_EMERGENCIA ctx=0
[ 3/3] p03 EMERGENCIA -> EMERGENCIA ctx=0
{"total": 3, "correct": 3, "accuracy": 1.0, ...}
```

Os 3 acertos batem com o que a rodada 4 já sabia sobre esses casos-âncora
(`p01`, `p02` fazem parte dos 15/18 que já acertavam). `ctx=0` em todos é
esperado: rodei em `--mode no_rag` de propósito (só validar o encanamento do
script), e a coleção ativa segue vazia de qualquer forma (B-57, ainda aberto).
Manifesto gravado em `data/evaluation/prova_runs/20260921-204205_smoke_prova_calibracao/`
confirma `cases_file`, `split` e `case_count` corretos.

**Verificação de que nada quebrou:** `scripts/tests` — 161 passaram (26
falhas em `test_capturar_fonte.py` são pré-existentes, por um módulo
`trafilatura` ausente neste ambiente host, sem relação com esta mudança).
Suíte do backend inalterada (script roda fora do container, via `requests`).

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/run_map_triage_eval.py` | `--cases`, `--split`, `--runs-dir` adicionados; manifesto passa a registrar `cases_file`/`split`/`case_count` |
| `data/evaluation/prova_runs/` | **novo** — primeira rodada da prova nova através do runner adaptado |
| `evidencias/ryu/planejamento.md` | entrega 6 marcada concluída |

## Observações

O `run_map_triage_eval.py` ainda lê `--api-url` apontando para a API real —
ele não tem (e não precisa ter) o monkeypatch de coleção candidata que
`measure_query_techniques.py` e `measure_query_latency.py` usam. Isso é
proposital: a prova de classificação testa o sistema como um tutor real o
usaria, contra o que estiver ativo — diferente das minhas medições de
consulta, que precisam mirar uma candidata específica para isolar a técnica.

## Deixado para depois

**O lote oficial (~150 casos, dev/teste, hash congelado)** continua sendo o
próximo passo real desta frente — o runner já está pronto para recebê-lo. A
validação do formato com o time (bloqueio aberto desde 13/09,
planejamento.md) precisa ser revisitada: dado tudo que mudou desde então
(base real, reranking, o próprio Vinicius pedindo essa prova no repasse de
20/09), pode já estar resolvida de fato — vale confirmar antes de escrever
os 150 casos.

**Baselines triviais** (seção 5.4 do plano) esperam o lote oficial existir.

## Próximo passo

Escrever o lote oficial é o maior item que resta em aberto no meu trilho.
Antes disso, vale uma confirmação rápida do time sobre o formato — ou seguir
direto, já que o pedido do Vinicius (repasse de 20/09) é o sinal mais forte
de validação que já tive.
