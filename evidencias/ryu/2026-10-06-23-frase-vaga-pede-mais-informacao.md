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

_A medir em 07/10._

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

Medir em 07/10 com os comandos acima e levar o resultado ao João.
