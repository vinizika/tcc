# Rodada 17 — comparação real da pré-triagem conversacional

**O fluxo novo não melhorou a acurácia de primeira resposta nesta rodada.**
A concordância com os rótulos de calibração caiu de **94,4% para 83,3%**.
O acompanhamento conseguiu resolver casos com informações novas e encerrar os
casos desconhecidos, mas o formulário apresentou uma opção ausente e dependência
indevida da origem da resposta. Há correções necessárias antes de tratar esta
versão como uma evolução validada para uso pela equipe.

## O que foi realmente executado

- **145 turnos reais e 185 chamadas lógicas ao Gemini**, incluindo aquecimentos,
  controle antigo, versão nova, conversas e verificações exploratórias.
- Mesma coleção ativa: `veterinary_documents__20260925T061349534255Z__280baf13`.
- Provedor registrado: `gemini-3.5-flash-lite`, sem substituição por dublê.
- Mongo real separado: `tcc_followup_eval_20260928`; não substitui o histórico da equipe.
- **18 casos de calibração × 2 repetições × 2 versões = 72 decisões principais.**
  Os 18 casos são 9 emergências, 8 não emergências e 1 incerto.
- Oito conversas sintéticas congeladas antes das chamadas; 31 decisões finais em
  braços pareados, pois um formulário não tinha resposta factualmente possível.
- Oito decisões exploratórias de recuperação e seis de estabilidade do caso c03.
- 330 testes backend, 221 testes de scripts, build TypeScript/Vite e sete testes
  de navegador passaram novamente. Logs incluídos no pacote desta rodada.

A referência anterior é o `WorkspaceService` extraído literalmente do commit
`6737665`, antes das mudanças conversacionais. O novo é o código não commitado
presente no checkout `codex/integrate-joao-react`. Nenhum código de produção foi
ajustado durante esta avaliação para melhorar os resultados. A ablação alterou
somente objetos do processo de benchmark, sem escrever na aplicação.

**Limite dos rótulos:** o conjunto usado é de calibração, com rótulos provisórios
já existentes; os casos conversacionais têm expectativas de engenharia, sem
validação veterinária. A prova final e a prova 2 não foram executadas nem alteradas.
Estes números não são a acurácia clínica final do TCC. Repetir um caso duas vezes
não cria duas amostras independentes.

## Antes e depois: classificação do mesmo relato

| Métrica, 36 decisões por versão | Antes | Depois |
|---|---:|---:|
| Acertos exatos | 34/36 | 30/36 |
| Acurácia de três classes | 94.44% | 83.33% |
| Macro-F1 | 0.8667 | 0.7328 |
| Acurácia balanceada de três classes | 95.83% | 87.96% |
| Recall de emergência | 18/18 (100%) | 16/18 (88,89%) |
| Emergência rebaixada a não emergência | 0 | 0 |
| Emergência deixada incerta | 0 | 2 |
| Cobertura binária | 88.89% | 77.78% |
| Falhas de serviço / JSON inválido observado | 0 / 0 | 0 / 0 |

A diferença foi **−11,11 pontos percentuais**, sem ganho em nenhum caso.
O bootstrap agrupado pelos 18 casos (4.000 reamostragens, seed 42) produziu
intervalo de 95% de **−27,78 a 0 pontos percentuais**. A amostra é pequena e de
conveniência; isso não sustenta uma afirmação de significância populacional.
As duas repetições repetiram as mesmas classes em cada versão.

Matriz de confusão agregada, colunas na ordem E / N / I:

| Classe esperada | Antes | Depois |
|---|---|---|
| EMERGENCIA | 18 / 0 / 0 | 16 / 0 / 2 |
| NAO_EMERGENCIA | 0 / 14 / 2 | 0 / 12 / 4 |
| INCERTO | 0 / 0 / 2 | 0 / 0 / 2 |

`INCERTO` é acerto quando a referência também é incerta. Nos relatos completos
rotulados E/N, conta como abstenção incorreta para essa métrica. Isso distingue
falta legítima de informação de uma perda de decisão frente ao mesmo relato.

### Onde regrediu

| Caso | Referência | Antes, nos dois ciclos | Depois, nos dois ciclos |
|---|---|---|---|
| p11: sangramento pequeno, vulva inchada, cadela ativa/comendo | NAO_EMERGENCIA | NAO_EMERGENCIA | INCERTO |
| p14: contato com matagal, claudicação e inchaço rápido | EMERGENCIA | EMERGENCIA | INCERTO |
| p16: destruição de sapatos e latidos ao ficar sozinho | NAO_EMERGENCIA | INCERTO | INCERTO |

p16 é erro compartilhado de concordância, não regressão nova. p11/p14 são os
quatro pares discordantes, contando as duas repetições.

## Recuperação: hipótese testada separadamente

A similaridade de conjuntos de fontes (Jaccard) entre versões foi em média
**21.11%**, mediana 20%; nenhum par manteve exatamente
as três fichas. A coleção não mudou: mudou o texto usado para consultá-la.

- Em p11, antes aparecia **Cio normal** junto de Piometra/Ferida superficial.
  Depois apareceram Trauma/Ferida superficial/Claudicação leve.
- Em p14, antes aparecia **Acidente com cobra, escorpião ou aranha** junto de
  Claudicação leve/Reação alérgica grave. Depois apareceram
  Claudicação leve/Ferida superficial/Trauma.

O novo `transcript()` inclui regras e JSON no texto entregue ao pipeline, e esse
mesmo texto entra na busca vetorial. Na ablação exploratória, mantivemos o prompt
clínico novo e retiramos apenas regras/JSON da consulta vetorial, usando o relato
original. Em p11/p14 e nos controles p01/p02, duas repetições cada, houve **8/8
acertos**. p11 voltou a N e p14 voltou a E nas duas repetições.

Isso é evidência localizada de que contaminar a consulta de recuperação com
instruções de orquestração explica estas regressões. A ablação foi escolhida após
observar as falhas; **não substitui os 83,3% medidos na implementação entregue**
nem demonstra recuperação de acurácia em uma prova independente.

## Performance e consumo

Tempos medidos ao chamar o serviço real no Docker: submit, Mongo, RAG, geração e
persistência. Não incluem HTTP, fila de background, polling, renderização ou tempo
humano. Execução sequencial; não houve ensaio de carga ou capacidade concorrente.
O primeiro aquecimento da comparação levou 18.54 s e foi separado.

| Métrica da comparação principal | Antes | Depois |
|---|---:|---:|
| Latência média por turno | 4.38 s | 4.32 s |
| Mediana | 2.89 s | 2.99 s |
| p95 interpolado | 20.30 s | 6.23 s |
| Máximo | 24.23 s | 42.59 s |
| Chamadas lógicas ao modelo | 36 | 44 |
| Tokens reportados, entrada + saída | 36,560 | 49,726 |
| Tokens médios por decisão | 1015.6 | 1381.3 |

O consumo aumentou **36,0% em tokens** e **22,2% em chamadas lógicas** na comparação
principal. As medianas ficaram próximas, mas não há evidência de ganho estável de
velocidade: houve backoff por limite/capacidade do Gemini, e o máximo do novo fluxo
foi maior. O p95 menor do novo fluxo não deve ser interpretado isoladamente.

Na rodada inteira, os logs registram **14 esperas por 429 e 3 por 503**. Todas as
chamadas medidas terminaram; esses eventos foram mantidos, não removidos da
amostra. Os logs guardam horários e tempos de recuo. Houve também latência alta
sem evento de backoff registrado. Chamadas lógicas não equivalem ao número exato
de requisições HTTP, pois o cliente faz retentativas internamente.

Foram reportados **210.116 tokens** em toda a rodada: 161.899 na classificação e
48.217 no acompanhamento, incluindo controles e aquecimentos. A chamada de
acompanhamento teve mediana de 1,32 s e máximo de 37,18 s. Não estimamos custo em
reais/dólares: cobrança, cache e tokens de eventuais tentativas não são inferidos.

Nos relatos inicialmente incertos das oito conversas, a mediana do turno inicial
foi 1,74 s antes e 3,35 s depois; o novo fluxo faz duas chamadas por turno incerto,
enquanto o antigo faz uma. A primeira medição antiga dessa fase contém partida
fria; por isso esses números não são um novo ensaio controlado de performance.
Nas sete jornadas completas com formulário, foram três envios do tutor e cinco
ou seis chamadas de modelo; mediana de 12,20 s de processamento somado, **sem
contar o tempo humano** e sem equivaler a uma única requisição HTTP.

## O formulário ajudou de fato?

**Ajudou mecanicamente a estruturar a próxima resposta e encerrou os casos sem
informação. Esta rodada não comprova que tutores reais observam/respondem melhor
por causa dele, nem que melhorou globalmente a classificação.**

Todos os oito relatos iniciais foram INCERTO nas duas versões. No novo fluxo,
os oito chegaram a formulário após uma resposta “Não sei dizer”, pelo motivo
`repeated_question`. O limiar de duas respostas sem progresso não foi o gatilho
observado nesta amostra; a regra de repetição antecipou o formulário.

| Controle | Resultado observado |
|---|---|
| Formulário, resposta factualmente possível | 7/7 de acordo com a expectativa final: 3 E, 2 N, 2 I |
| Mesma informação, texto livre no sistema novo | 7/8 de acordo; c03 permaneceu INCERTO |
| Mesma informação, sistema antigo | 8/8 de acordo |
| Formulário sem dado novo: “Não observei” | 8/8 INCERTO e encerramento `insufficient` |
| Formulário sem opção verdadeira disponível | 1/8: c05; excluído do braço formulário, mantido como falha de cobertura |

As cinco respostas de formulário com novos fatos suficientes resolveram os cinco
casos. Os dois casos sem novas observações continuaram incertos. Porém o sistema
antigo também resolveu os casos quando recebeu os mesmos fatos. O controle antigo
recebeu gratuitamente a informação elicitada pelo novo fluxo; isso não reproduz
a UX antiga nem prova que a pessoa a forneceria espontaneamente.

Não se deve escrever “o formulário teve 100% de eficácia”: há sete respostas
avaliáveis, uma resposta inviável e somente oito casos de conveniência. Entre os
seis casos com fatos finais conhecidos, apenas **3/6** tinham preset diretamente
compatível; **2/6** dependeram de “Não observei” para a informação perguntada mais
um sinal diferente no complemento; **1/6** não permitia resposta verdadeira entre
as opções. Os complementos repetem exclusivamente fatos congelados; não foram
inventados para induzir a classificação.

### Consistência: c03

Com o animal caído, sem levantar e sem reagir, a resposta literal foi igual nos
dois braços, incluindo complemento. As três fichas recuperadas foram iguais.
O formulário produziu E; o texto produziu I. Em **três pares extras**, a diferença
se repetiu: **3/3 E no formulário e 3/3 I no texto**. Com o par original: 4/4 contra
0/4, **em um único caso**, sem aumentar o número de casos independentes.

A origem do envio, serializada no contexto, é a diferença controlada entre os
braços. Trata-se de uma sensibilidade indesejada a metadados, não de evidência de
melhor observação por humanos. A justificativa incerta pediu informação sobre a
causa da fraqueza, apesar do sinal grave já relatado. Esse comportamento precisa
ser corrigido e receber teste de invariância antes de uma conclusão de robustez.

### Qualidade das perguntas e opções

- **c05:** pergunta pressupõe “recusou ou comeu menos” e omite “comeu normalmente”.
  Usamos o chat livre; não marcamos desconhecimento falso só para preencher o campo.
- **c02:** pergunta inicial sobre boca aberta/esforço mudou para língua/gengiva
  azulada, conservando a mesma chave `resp_effort_mouth_open`. A chave não garantiu
  identidade semântica; o código registrou repetição apesar da troca de informação.
- **c06:** combina apetite e vômito em uma única pergunta. Um único `?` no schema
  não garante uma única informação discriminativa.
- **c03:** apareceu o erro lexical “cometeu menos”. A saída validada estruturalmente
  não equivale a uma boa pergunta em linguagem leiga.
- Em todos os oito formulários havia opções explícitas de desconhecimento; nenhum
  dos oito controles sem dados virou falsa não emergência.

A auditoria é de engenharia, feita nesta sessão, sem revisão veterinária ou estudo
IHC. Perguntas sobre apetite em relatos totalmente vagos foram marcadas como
alinhamento indeterminado, não automaticamente como erro clínico.

## Prioridades identificadas, sem correção silenciosa

1. **Alta — recuperar somente a partir do conteúdo clínico**, separando regras,
   estado e metadados da consulta vetorial. Repetir o lote inteiro após a correção.
2. **Alta — invariância à origem da resposta:** texto e formulário com os mesmos
   fatos não devem mudar a urgência. Não exigir causa/diagnóstico para reconhecer
   um sinal grave suficiente. Reproduzir c03 após a correção.
3. **Alta — opções factualmente completas:** permitir normalidade/negativa quando
   pertinente e resposta livre sem obrigar uma opção falsa. Reproduzir c05.
4. **Média — chave semântica estável e uma informação por pergunta:** validar c02/c06,
   além de apenas contar pontos de interrogação e comparar strings/chaves.
5. **Média — custo ao encerrar:** o fluxo ainda chama o planejador após resposta ao
   formulário mesmo quando vai encerrar; reduzir trabalho descartado sem perder
   a reclassificação clínica prioritária.
6. Fazer estudo com membros da equipe/tutores após corrigir os pontos anteriores:
   conclusão da tarefa, erros de seleção, tempo humano, clareza e taxa de abandono.
   Só esse estudo permitirá sustentar que o formulário facilita a coleta na prática.

## Reprodução e arquivos

Pacote completo: [2026-09-28-avaliacao-conversacional/](2026-09-28-avaliacao-conversacional/).

- [Protocolo e adendos](2026-09-28-avaliacao-conversacional/protocolo.md): distingue
  comparação principal de verificações escolhidas após observar falhas.
- [Resumo estruturado](2026-09-28-avaliacao-conversacional/summary.json),
  [turnos CSV](2026-09-28-avaliacao-conversacional/turns.csv) e
  [resultados brutos](2026-09-28-avaliacao-conversacional/raw.jsonl).
- [Transcrições e braços](2026-09-28-avaliacao-conversacional/conversas.md),
  [auditoria dos formulários](2026-09-28-avaliacao-conversacional/auditoria-formularios.csv),
  [respostas conferidas](2026-09-28-avaliacao-conversacional/actions.json).
- `cases.json`, `freeze.json`, `baseline_workspace.py` e recibos de hashes
  identificam entradas, baseline e código. Os logs de runtime registram 429/503.
- `backend-tests.txt`, `scripts-tests.txt`, `react-build.txt` e `browser-tests.txt`
  registram os testes repetidos nesta rodada. O navegador tem dois testes de
  contrato com fixtures HTTP e cinco fluxos reais com API/Mongo.

Gerar novamente métricas offline:

```sh
.venv/bin/python scripts/report_conversation_eval.py \
  evidencias/vini/2026-09-28-avaliacao-conversacional
```

Para nova rodada, copie `cases.json` e `baseline_workspace.py` para uma pasta nova
antes de executar; o runner retoma fases já salvas e não apaga resultados antigos:

```sh
.venv/bin/python scripts/run_conversation_eval.py --phase baseline --output-dir PASTA
.venv/bin/python scripts/run_conversation_eval.py --phase prepare --output-dir PASTA
# Inspecionar os formulários reais e criar actions.json com respostas verdadeiras.
.venv/bin/python scripts/run_conversation_eval.py --phase finish --output-dir PASTA
# Diagnósticos exploratórios específicos desta rodada:
.venv/bin/python scripts/run_conversation_eval.py --phase ablation --output-dir PASTA
.venv/bin/python scripts/run_conversation_eval.py --phase recheck --output-dir PASTA
.venv/bin/python scripts/report_conversation_eval.py PASTA
```

O runner usa o container existente `backend-api` e credenciais já configuradas,
sem imprimi-las. O benchmark chama serviços diretamente; os testes de navegador
cobrem a integração HTTP separadamente. Não houve teste remoto, ensaio de carga,
validação clínica independente ou conversa completa com Ollama nesta rodada.
Os dados sintéticos do Mongo foram mantidos para auditoria. Nenhuma coleção ou
base documental foi promovida, e não houve commit/push nesta tarefa.
