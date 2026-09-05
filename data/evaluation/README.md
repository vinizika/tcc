# Avaliação

Esta pasta guarda as medições do sistema de triagem. Ela é a régua do time:
os números que vão para o TCC saem daqui.

## O que tem aqui

```
evaluation/
├── README.md               <- este arquivo
├── accuracy_results.csv    <- as 98 respostas da medição de 04/05/2026 (histórico)
├── confusion_matrix.csv    <- a matriz daquela medição (histórico)
├── runs/                   <- rodadas executadas nesta máquina. FORA do Git
└── cited/                  <- rodadas citadas por alguma evidência. Versionadas
```

Os dois CSVs históricos **não se regeram**: são o artefato de 04/05 e servem
de teste de regressão das métricas (o "teste dourado").

Toda rodada grava em `runs/`. Quando um número dela for citado numa
evidência, `report_evaluation.py cite` copia a rodada para `cited/` — assim
cada afirmação do TCC tem os dados que a produziram, e as execuções
descartáveis não incham o repositório.

### Anatomia de uma rodada

Cada rodada é um diretório `AAAAMMDD-HHMMSS_<nome>` com cinco arquivos:

| Arquivo | O que é | Fonte de verdade? |
|---|---|---|
| `predictions.jsonl` | Uma linha por relato: o que foi enviado, a resposta completa, tempos, fontes citadas, saída bruta do modelo | **Sim** |
| `manifest.json` | O que foi executado: configuração pedida **e** a efetiva (ecoada pela API), commit, hash do dataset, identidade do backend (modelo, base, prompts), máquina, horários | **Sim** |
| `metrics.json` | Os números, calculados a partir das previsões | derivado |
| `report.md` | Leitura humana das métricas | derivado |
| `predictions.csv` | As previsões em planilha, sem os textos longos | derivado |

Os derivados podem ser regerados a qualquer momento com
`report_evaluation.py report <rodada>`.

## Passo a passo

**Antes de qualquer rodada**, a API precisa estar de pé com a base indexada:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
curl localhost:8000/health/fingerprint      # chunk_count deve ser > 0
```

**1. Rodar.** Escolha um preset (a configuração do braço) e um subconjunto:

```bash
python scripts/run_evaluation.py --preset naive_rag --subset full --name marco1
```

| Opção | O que faz |
|---|---|
| `--preset` | `llm_only` (sem busca; a linha de base), `naive_rag` (busca ligada, consulta desligada), `rag_query` (pipeline completo), `legacy` (reproduz 04/05). Definidos em `scripts/presets.json` |
| `--set chave=valor` | Sobrescreve uma opção do preset (ex.: `--set temperature=0.8`). Chave desconhecida falha antes de qualquer requisição |
| `--subset` | `smoke` (12 + 12 linhas, para iterar), `balanced` (27 + 27), `full` (98). Os números do TCC são sempre `full` |
| `--limit N` | Só as N primeiras, alternando entre as classes |
| `--repeat K` | Roda cada linha K vezes, para medir estabilidade |
| `--base-seed N` | Com temperatura acima de zero, dá uma seed diferente a cada repetição (N, N+1, …). Sem isso a API usa a seed fixa e as repetições saem idênticas |
| `--name` | O sufixo do diretório |

O runner aquece o modelo com uma chamada e **aborta ali** se a API recusar a
configuração (erro 400 ou 422) — erro de configuração não é dado. Durante a
rodada, grava cada linha imediatamente e confere que a configuração efetiva
não mudou (um backend reiniciado com outro `.env` aborta).

**2. Retomar**, se a rodada foi interrompida:

```bash
python scripts/run_evaluation.py --resume data/evaluation/runs/<diretório>
```

Refaz só as linhas que faltam ou falharam. Não aceita mudar o preset nem as
opções — para isso, comece uma rodada nova.

**3. Comparar** duas rodadas:

```bash
python scripts/report_evaluation.py compare data/evaluation/runs/<A> data/evaluation/runs/<B>
```

Ele imprime, nesta ordem: as **diferenças de configuração** (se houver mais
de uma, o resultado não diz qual causou o quê — é a regra de uma mudança por
rodada), a tabela de métricas nas linhas em comum, o **teste de McNemar**
pareado (quantas linhas A acertou e B errou, e vice-versa, com o valor-p), o
**intervalo de confiança** da diferença de acurácia, e as linhas que mudaram
de classificação. Só a primeira repetição de cada rodada entra na comparação.

**4. Citar** numa evidência:

```bash
python scripts/report_evaluation.py cite data/evaluation/runs/<A>
```

Copia a rodada para `cited/` e imprime o trecho em markdown para colar.

## Métricas

**A métrica principal é a acurácia balanceada**, média do recall das duas
classes. O motivo: o conjunto tem 71 emergências e 27 não emergências, então
um sistema que sempre responde "emergência" acerta 72,4%. A acurácia simples
premia esse comportamento; a balanceada, não.

A **acurácia estrita** continua sendo calculada porque é ela que liga os
resultados novos ao histórico — foi assim que os 70,41% foram medidos.

Ao lado delas vai sempre o par clínico:

- **falsos não urgentes** (de 71 emergências, quantas passaram como leves) —
  o erro grave;
- **falsos urgentes** (de 27 não emergências, quantas viraram emergência) —
  o erro que causa o gargalo nas clínicas que o projeto quer reduzir.

Abstenções (INCERTO) e respostas mal formadas contam como erro em todas as
acurácias. `coverage` mostra quanto o sistema decidiu, e `accuracy_decided`,
o quanto acertou entre as decididas — sempre lidos juntos, porque
`accuracy_decided` sozinho premia quem se recusa a responder.

O relatório traz também métricas de **ancoragem** (quantas fontes foram
citadas, quantas linhas não tiveram nenhum trecho acima do limiar de 0,70),
de **latência** por etapa, e, com `--repeat`, de **estabilidade** (quantas
linhas mudaram de classificação entre execuções idênticas).

## O que este conjunto mede, e o que não mede

Uma limitação importante, encontrada ao construir o runner e que precisa
acompanhar qualquer leitura destes números.

Nas 98 linhas avaliadas, o rótulo é **trivialmente separável**:

| | Emergência (71 linhas) | Não emergência (27 linhas) |
|---|---|---|
| Sintomas por linha | sempre 5 | 3 ou 4 (uma com 5) |
| Vocabulário | 192 termos distintos | **5 termos** |
| Origem | todas originais | todas sintéticas |

Duas regras sem nenhum modelo:

| Regra | Acurácia |
|---|---|
| "Só sintomas leves → não emergência" | **98/98** |
| "Menos de 5 sintomas → não emergência" | 97/98 |

Por isso o relatório traz essas regras como baselines. Elas deixam claro que
o conjunto mede **"o sistema parou de exagerar a urgência de cinco sinais
leves"**, e não a capacidade geral de triagem. Além disso, a classe não
emergência tem só 15 combinações distintas em 27 linhas, ou seja, as linhas
são quase duplicatas — o que enfraquece qualquer teste estatístico que
assuma independência.

Ampliar o vocabulário permitido ou rotular casos reais como não urgentes é
decisão do time com a especialista: [B-05](../../evidencias/backlog.md#b-05).

## Reprodução da medição de 04/05

O preset `legacy` chega perto, mas **não é idêntico**. Diferenças conhecidas:

1. Hoje o sistema tenta duas vezes quando a saída vem mal formada; antes era
   tiro único. A métrica `accuracy_single_attempt` recontabiliza as linhas
   que precisaram de segunda tentativa como inválidas.
2. A classificação é normalizada: "Nao Emergencia" hoje é aceito, antes seria
   contado como erro.
3. A seed é fixa. A rodada de 04/05 usou a seed aleatória padrão do Ollama,
   por isso a reprodução usa três repetições com seeds diferentes para obter
   uma faixa, em vez de um ponto.
4. O tamanho de contexto é enviado explicitamente; antes ficava no padrão.
5. Não se sabe qual versão exata do modelo rodou em 04/05.

A rodada R1 (04/09) mediu essa replicação: faixa de 0,714 a 0,765 de
acurácia estrita, com **28 das 98 linhas mudando de classificação** entre
execuções — os 70,41% de 04/05 eram um sorteio de uma distribuição larga,
não um ponto. Detalhe na
[rodada 4](../../evidencias/joao/2026-09-04-05-runner-de-avaliacao.md).

## Contrastes pré-registrados

Com 98 linhas, uma diferença só é detectável a partir de aproximadamente 6
pontos percentuais. Para não transformar ruído em conclusão, os contrastes
são declarados antes de rodar:

- **Primário:** RAG contra LLM puro, na acurácia estrita.
- **Secundário:** o mesmo, restrito às não emergências, onde o ganho é
  esperado.
- **Exploratório:** todo o resto da matriz de ablação, reportado com
  intervalo de confiança e sem valor-p.

## Estado das medições

As rodadas citadas até agora estão em `cited/`; a leitura completa, com as
decisões e o que cada braço ensinou, está na
[rodada 4 do trilho B2](../../evidencias/joao/2026-09-04-05-runner-de-avaliacao.md).
Em resumo (98 linhas, temperatura zero):

| Braço | Acurácia balanceada | Falsos não urgentes |
|---|---|---|
| Prompt antigo, sem RAG | 0,572 | 3/71 |
| **Prompt novo, sem RAG** | **0,893** | 8/71 |
| Prompt novo, com RAG (3 trechos) | 0,763 | 30/71 |
| Pipeline completo (04/09, instável) | 0,701 (média de 3) | 36/71 |
| Pipeline completo (05/09, após `b907d6e`) | 0,704 | 40/71 |

As duas linhas do pipeline completo medem o mesmo braço em commits
diferentes. A de 04/09 é a média de três execuções que discordavam entre si
em 33 das 98 linhas — a etapa de consulta ainda rodava a temperatura 0,8 com
seed aleatória. A de 05/09 é posterior à correção do trilho B1, com 6 linhas
instáveis. A diferença entre elas **não é estatisticamente significativa**
(McNemar p = 0,50), o que era o esperado: a correção mudou a
reprodutibilidade, não o desempenho. Detalhe na
[rodada 6 do trilho B2](../../evidencias/joao/2026-09-05-06-determinismo-da-consulta.md).

## Testes

```bash
python -m pytest scripts/tests -q
```
