# Avaliação

Esta pasta guarda as medições do sistema de triagem. Ela é a régua do time:
os números que vão para o TCC saem daqui.

## O que tem aqui

| Caminho | O que é |
|---|---|
| `accuracy_results.csv` | As 98 respostas da medição de 04/05/2026. **Artefato histórico, não regerar.** Serve de teste de regressão das métricas |
| `confusion_matrix.csv` | A matriz daquela mesma medição |
| `runs/` | Rodadas executadas. **Fora do controle de versão** |
| `cited/` | Rodadas citadas por alguma evidência. Versionadas, porque sustentam um número escrito |

Toda rodada grava em `runs/`. Quando um número dela for citado numa
evidência, `report_evaluation.py cite` copia a rodada para `cited/` — assim
cada afirmação do TCC tem os dados que a produziram, e as execuções
descartáveis não incham o repositório.

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
decisão do time com a especialista, e está registrada como bloqueio no
planejamento do trilho B2.

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

Por isso a rodada R1 é chamada de **replicação aproximada**: espera-se que a
faixa contenha 70,41%, não que reproduza o valor exato.

## Contrastes pré-registrados

Com 98 linhas, uma diferença só é detectável a partir de aproximadamente 6
pontos percentuais. Para não transformar ruído em conclusão, os contrastes
são declarados antes de rodar:

- **Primário:** RAG contra LLM puro, na acurácia estrita.
- **Secundário:** o mesmo, restrito às não emergências, onde o ganho é
  esperado.
- **Exploratório:** todo o resto da matriz de ablação, reportado com
  intervalo de confiança e sem valor-p.

## Como usar

```bash
# uma rodada
python scripts/run_evaluation.py --preset naive_rag --subset full --name marco1

# retomar uma rodada interrompida
python scripts/run_evaluation.py --resume data/evaluation/runs/20260904-2130_marco1

# comparar duas rodadas
python scripts/report_evaluation.py compare runs/<A> runs/<B>

# promover uma rodada citada numa evidência
python scripts/report_evaluation.py cite runs/<A>
```

Os scripts rodam no host e conversam com a API em `localhost:8000`, que
precisa estar no ar (`docker compose up -d`). Os testes são executados com
`python -m pytest scripts/tests -q`.
