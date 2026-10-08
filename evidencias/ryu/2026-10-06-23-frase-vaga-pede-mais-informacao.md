# Frase vaga pede mais informação (proposta ao trilho B2)

**Data:** 06/10/2026 · **Trilho:** B1 (frente prova), com proposta ao B2 · **Rodada:** 23 · **Commit:** este

## O que foi feito

A [rodada 21](2026-10-06-21-as-perguntas-extras-funcionam.md) mostrou o erro mais
perigoso dos testes de conversa: "Oi, meu cachorro tá vomitando e eu tô
preocupado", sem mais nada, foi classificado **NAO_EMERGENCIA no primeiro turno**,
sem nenhuma pergunta. Era um corpo estranho. O app só pergunta quando a IA diz
INCERTO; se ela dá uma classe a uma frase que não permite nenhuma, a pergunta
nunca acontece.

Três coisas, nenhuma mudando o comportamento padrão do sistema:

1. **Uma bateria de teste**, [`data/diagnostico/aberturas_vagas.csv`](../../data/diagnostico/aberturas_vagas.csv):
   14 mensagens vagas (resposta certa: INCERTO), 4 curtas e graves (EMERGENCIA:
   um sinal grave basta) e 4 curtas e leves com o estado do animal descrito
   (NAO_EMERGENCIA). Os controles existem para a regra não esconder emergência
   nem transformar tudo em INCERTO.
2. **Uma versão nova do prompt de triagem**, `v2_suficiencia`: o `v1_grounded`
   com uma regra a mais, logo depois da regra do INCERTO:

   > Para responder NAO_EMERGENCIA, o relato precisa dizer como o animal está
   > agora (por exemplo, se come, se está ativo, se respira normal) ou quantas
   > vezes e desde quando o sinal aparece. Se o tutor citar só um sintoma, sem
   > nada disso (por exemplo: "está vomitando", "está mancando", "está
   > estranho"), responda INCERTO.

   A regra mexe só na porta do NAO_EMERGENCIA; "um único sinal grave basta para
   EMERGENCIA" continua.
3. **O app passa a ler a versão do prompt de uma configuração**
   (`WORKSPACE_PROMPT_VERSION`, padrão `v1_grounded`), em vez de tê-la escrita no
   código. Trocar para `v2_suficiencia` é uma linha no `.env`. Para o runner, o
   preset `producao_suficiencia`.

## Por quê

Melhoria 2 da lista aprovada pelo Ryu em 06/10. O objetivo que ele definiu é o
sistema pedir mais informação **quando falta informação**; a rodada 21 achou o
caso em que falta e ele não pede.

**O prompt de triagem é do trilho B2 (João).** Por isso a regra entra como
versão nova, ao lado da atual, desligada: o João decide se ela vira o padrão,
depois da medição.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Versão nova do prompt, não edição do `v1_grounded` | O `v1_grounded` é o que todas as rodadas citadas mediram (paridade) e é do B2 |
| 2 | A regra só restringe o NAO_EMERGENCIA | O risco que motivou a rodada é rebaixar emergência; restringir a EMERGENCIA criaria o risco oposto |
| 3 | Controles na bateria (4 graves, 4 leves bem descritos) | Uma regra "responda INCERTO" pode passar a valer para tudo: os controles medem isso |
| 4 | Medição para 07/10 | A cota gratuita do Gemini de 06/10 está quase no fim (~400 de 500 chamadas) |

## Resultado esperado

_Escrito antes de medir._ Comandos (07/10):

```
python scripts/run_evaluation.py --api-url http://127.0.0.1:8000 --cases data/diagnostico/aberturas_vagas.csv --preset producao --name r23_vagas_v1
python scripts/run_evaluation.py --api-url http://127.0.0.1:8000 --cases data/diagnostico/aberturas_vagas.csv --preset producao_suficiencia --name r23_vagas_v2
python scripts/run_evaluation.py --api-url http://127.0.0.1:8000 --cases data/prova2/casos.csv --split calibracao --preset producao_suficiencia --name r23_calib_v2
```

| Medida | `v1_grounded` (esperado) | `v2_suficiencia` — critério |
|---|---|---|
| 14 vagas → INCERTO | poucas (o v1 dá classe a frase vaga) | **≥ 12 de 14** |
| 4 curtas graves → EMERGENCIA | 4 | **4 de 4** |
| 4 curtas leves → NAO_EMERGENCIA | 4 | **≥ 3 de 4** |
| Calibração da prova 2 (66), comparada à produção da rodada 18 (0 perdidas · 1 falso alarme · 1 INCERTO falso) | — | **0 emergências perdidas** e **no máximo 2 INCERTO falsos a mais** |

Se passar, a recomendação ao João é tornar `v2_suficiencia` o padrão do app
(`WORKSPACE_PROMPT_VERSION`). Se não, a regra fica registrada como tentativa.

## Resultado obtido

Medido em 07/10, pela API, com o Gemini (`gemini-3.5-flash-lite`), todas as
linhas com status `ok`. Depois dos três comandos previstos, rodei **dois
controles** que o plano não tinha, para separar o efeito da regra da variação do
Gemini entre dias ([B-77](../backlog.md#b-77)): o `v1_grounded` na calibração
**no mesmo dia** (a comparação prevista era com a rodada 18, de 05/10) e uma
**segunda repetição** da bateria com as duas versões.

### A bateria de frases vagas

| Grupo | `v1_grounded` (1ª · 2ª repetição) | `v2_suficiencia` (1ª · 2ª) | Critério do v2 |
|---|---|---|---|
| 14 vagas → INCERTO | 12 · 13 | **14 · 14** | ≥ 12 ✅ |
| 4 curtas graves → EMERGENCIA | 4 · 4 | **4 · 4** | 4 ✅ |
| 4 curtas leves → NAO_EMERGENCIA | 4 · 4 | **4 · 4** | ≥ 3 ✅ |

Os erros do `v1_grounded`, todos para NAO_EMERGENCIA sem pergunta: **v01 "Oi, meu
cachorro tá vomitando e eu tô preocupado"** (o q180 da rodada 21) nas duas
repetições, e v13 "Meu cachorro comeu uma coisa que achou na rua" na primeira.

**O resultado esperado do v1 estava errado, para melhor:** eu esperava "poucas"
vagas viradas INCERTO, e o v1 já acerta 12 a 13 das 14. O problema é mais
estreito do que a rodada 21 sugeria: está concentrado em vômito e "comeu algo",
justamente onde um NAO_EMERGENCIA errado pode esconder um corpo estranho ou
uma intoxicação.

### A calibração da prova 2 (66), no mesmo dia

| Versão | Emergências perdidas | Falsos alarmes | INCERTO falsos |
|---|---|---|---|
| `v1_grounded` (07/10) | 0 de 40 | 1 de 24 | 1 |
| **`v2_suficiencia`** (07/10) | **0 de 40** | **0 de 24** | **1** |

Critério: 0 emergências perdidas ✅ e no máximo 2 INCERTO falsos a mais ✅
(nenhum a mais). Mudaram 2 casos, os mesmos dois erros da rodada 18:

- **q186 (primeiro cio, tutora aflita):** INCERTO → **NAO_EMERGENCIA**, certo;
- **q118 (mordida de gambá, vacina vencida):** EMERGENCIA → INCERTO. Continua
  errado (é leve), mas passou de falso alarme a pedido de mais informação.

Rodadas citadas:
[`20261007-221812_r23_vagas_v1`](../../data/evaluation/cited/20261007-221812_r23_vagas_v1/report.md) ·
[`20261007-222005_r23_vagas_v2`](../../data/evaluation/cited/20261007-222005_r23_vagas_v2/report.md) ·
[`20261007-224327_r23_vagas_v1_rep2`](../../data/evaluation/cited/20261007-224327_r23_vagas_v1_rep2/report.md) ·
[`20261007-224646_r23_vagas_v2_rep2`](../../data/evaluation/cited/20261007-224646_r23_vagas_v2_rep2/report.md) ·
[`20261007-223852_r23_calib_v1`](../../data/evaluation/cited/20261007-223852_r23_calib_v1/report.md) ·
[`20261007-222308_r23_calib_v2`](../../data/evaluation/cited/20261007-222308_r23_calib_v2/report.md)
(conferido: a chave do Gemini não aparece em nenhum arquivo).

## Conclusão

**O `v2_suficiencia` passa em todos os critérios escritos antes**, nas duas
repetições: as frases vagas passam a pedir mais informação, os controles graves
e leves não mudam, e na calibração nada piora (2 erros do v1 viram 1).

**Recomendação ao João (dono do prompt de triagem):** tornar o `v2_suficiencia`
o padrão do app, com uma linha no `.env` (`WORKSPACE_PROMPT_VERSION=v2_suficiencia`)
ou mudando o padrão da setting. O padrão do runner (`TRIAGE_PROMPT_VERSION`)
pode continuar no `v1_grounded` até a matriz final, para não misturar com as
rodadas citadas.

**Limites:** a bateria tem 22 frases escritas por mim e não validadas por
veterinário; a calibração tem 66 casos, poucos para ver diferenças pequenas; o
teste lacrado da prova 2 não foi usado.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/prompts/triage.py` | `REGRA_SUFICIENCIA`, `com_regra_de_suficiencia()` e a escolha da versão em `_sistema_para` |
| `backend/app/schemas/triage.py` | `PromptVersion` aceita `v2_suficiencia` |
| `backend/app/core/config.py`, `.env.example` | `WORKSPACE_PROMPT_VERSION` (padrão `v1_grounded`) |
| `backend/app/services/workspace_service.py` | o app lê a versão da configuração (antes: `"v1_grounded"` escrito no código) |
| `backend/app/services/fingerprint_service.py` | o retrato da API registra o hash do `v2_suficiencia` |
| `scripts/presets.json` | preset `producao_suficiencia` |
| `data/diagnostico/aberturas_vagas.csv`, `data/diagnostico/README.md` | **nova** bateria |
| `backend/tests/test_prompt_suficiencia.py` (novo), `test_workspace.py` | 4 testes: o v1 não muda, o v2 é o v1 mais a regra (com e sem fichas, com CoT), e o app usa a versão configurada |

**Testes:** backend 340 → **344**, todos passando com os padrões do time. Neste
ambiente, 3 testes que conferem os padrões falham porque o `.env` local do Ryu
ainda tem os valores antigos (llama e tradutor ligado); com as variáveis do
`.env.example`, passam os 344.

## Próximo passo

Levar o resultado ao João, com a recomendação de ligar o `v2_suficiencia` no app.
