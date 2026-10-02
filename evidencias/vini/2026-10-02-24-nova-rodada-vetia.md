# Rodada 24 — reavaliação após comunicação VetIA

Pedido: novos testes, documentação completa e comparações com versões passadas.
Execução em 02/10/2026 sobre HEAD `07bb480` mais alterações locais de comunicação
e marca, registradas em `snapshot.json`. A rodada não alterou código do produto,
prompts, base ou gabaritos. Os dados e scripts estão na
[pasta desta avaliação](2026-10-02-testes-vetia/README.md).

## Resultado principal

A calibração manteve 34/36 acertos por braço (94,44%) e 18/18 emergências
reconhecidas. As 36 classificações atuais foram iguais às da correção v2 anterior,
com os mesmos hashes de entrada clínica e os mesmos conjuntos de fontes.
Isso é evidência de estabilidade nesta amostra, não prova de segurança geral.

O teste manual do usuário reproduziu a limitação em todas as três repetições:
INCERTO no primeiro relato e EMERGENCIA após explicitar dificuldade respiratória.
Também foi observada espera de 326,50 segundos causada principalmente por
retentativas após respostas 503 do provedor. Esses resultados negativos foram
preservados; não declaramos todos os problemas resolvidos porque os testes de
engenharia passaram.

## Escopo realmente executado

- 18 casos congelados × duas repetições × dois braços: **72 decisões**, mais um
  aquecimento separado. 77 chamadas lógicas ao modelo nesse benchmark, incluindo
  quatro chamadas de acompanhamento e a chamada de aquecimento.
- Quatro cenários de API reais, nove turnos, com Gemini/Mongo: emergência direta,
  informação complementar, formulário desconhecido e formulário com sinal grave.
- Exploração manual separada: nove conversas, 12 turnos, três repetições por
  cenário. Não são 12 casos clínicos independentes nem novos rótulos certificados.
- **94 turnos reais no total**, incluindo o aquecimento. A contagem de 77 chamadas
  lógicas se refere apenas à calibração instrumentada; não é o total de todas as
  requisições HTTP ou de chamadas desta rodada.
- 340 testes backend, 224 scripts, 10 mock; TypeScript/Vite e consistência das
  fichas/vocabulário aprovados.
- 12 testes de navegador: sete com fixtures HTTP (formulário/apresentação), cinco
  de integração real. Zero falhas, pulados ou flaky; 61,29 s no relatório Playwright.

O browser usou a imagem Docker atual em `localhost:3000`. O teste de encaminhamento
reutilizou a conversa real de emergência da validação anterior, registrada em
`browser-live-input.json`; não foi substituída por uma resposta clínica simulada.
Os novos smokes da API foram executados em seguida.

## Comparação clínica pareada

| Versão/execução | Acerto | Recall emergência | Resultado nos pares |
|---|---:|---:|---|
| Baseline histórico, rodada original | 34/36 (94,44%) | 18/18 (100%) | Referência antes do acompanhamento |
| PR16 original, 28/09 | 30/36 (83,33%) | 16/18 (88,89%) | Regressões p11 e p14 |
| Correção v2, rodada anterior de 02/10 | 34/36 (94,44%) | 18/18 (100%) | Recuperação das regressões |
| Baseline histórico reexecutado agora | 34/36 (94,44%) | 18/18 (100%) | Igual ao braço atual |
| VetIA atual reexecutado agora | 34/36 (94,44%) | 18/18 (100%) | Zero classes alteradas frente à v2 |

Na versão atual: acurácia balanceada 95,83%, macro-F1 86,67%, cobertura E/N 88,89%.
Matriz (esperado → previsto): E→E 18; N→N 14; N→I 2; I→I 2; demais células zero.
O caso p16 continua INCERTO nas duas repetições e nos dois braços, contra rótulo
provisório N. Não foi relabelado para melhorar a pontuação.

Em relação ao PR16 original: +11,11 pontos percentuais, ganhos em p11/p14 nas duas
repetições e nenhuma regressão pareada. O bootstrap por 18 casos dá intervalo
95% [0; 27,78] pontos; não tratar as 36 repetições como 36 casos independentes.
Frente à v2, diferença observada zero; intervalo empírico zero nessa amostra não
significa certeza de equivalência na população.

As referências de 89,3% nos 122 relatos independentes e 96,3% nos 134 casos de
prova/régua continuam históricas: não foram reexecutadas nem substituídas pela
calibração de 18 casos. Ver [panorama histórico](2026-10-02-21-panorama-historico-e-etapa-atual.md).

## Desempenho e tokens

| Métrica da calibração | Baseline agora | VetIA agora | Correção v2 anterior |
|---|---:|---:|---:|
| Mediana | 3,71 s | 3,74 s | 3,05 s |
| Média | 5,64 s | 16,63 s | 3,67 s |
| p95 | 17,60 s | 47,25 s | 6,72 s |
| Máximo | 28,65 s | 326,50 s | 22,92 s |
| Tokens de entrada + saída | 36.532 | 41.234 | 41.284 |
| Chamadas lógicas, sem aquecimento | 36 | 40 | 40 |

O acompanhamento ainda custa +12,87% em tokens frente ao baseline desta rodada.
A redação fixa no React não adiciona tokens. A diferença de 50 tokens frente à
execução v2 não é economia causada pelo frontend: são saídas do modelo em outra
execução. O PR16 original havia usado 49.726 tokens nesse braço.

O p04 atual gastou 326,50 s, com quatro 503 e esperas de 20+40+80+160 s: **300 s
somente em backoff**. O p02 gastou 84,42 s, incluindo esperas de 20+40 s após 503.
No benchmark inteiro, houve sete eventos de backoff 503 e dois de 429. Os valores
`attempts=1` do resultado não contam esses retries HTTP: são tentativas lógicas
de geração/validação. A análise está em
[diagnóstico de espera](2026-10-02-testes-vetia/diagnostico-espera.md).

Os tempos não foram filtrados. A exploração manual se sobrepôs à parte final da
calibração e os testes de browser rodaram durante o benchmark; portanto diferenças
de tempo entre execuções não são efeito causal isolado da interface. A espera
de cinco minutos ocorreu antes da exploração manual. Não houve teste de carga
planejado, medição de capacidade concorrente ou benchmark de recursos.

## Reprodução do relato manual

| Cenário | Resultado observado | Mediana por turno, incluindo polling |
|---|---|---:|
| Cansada, não fica de pé, boca aberta | INCERTO 3/3 | 10,24 s |
| Complemento: dificuldade para respirar | EMERGENCIA 3/3 | 6,31 s |
| Relato inicial já explicita dificuldade respiratória | EMERGENCIA 3/3 | 4,19 s |
| Respiração sem esforço, anda/come normalmente | NÃO EMERGENCIA 3/3 | 4,16 s |

O primeiro relato recuperou artrose, paralisia aguda das patas traseiras e
obstrução uretral nas três repetições. Após o complemento, dificuldade
respiratória entrou em primeiro. A repetição explícita também recuperou essa
ficha em primeiro. O controle negativo recuperou a ficha respiratória, mas o
modelo respondeu N, compatível com as negativas explícitas do texto sintético.

Isso reproduz a sensibilidade à formulação e a falta da ficha respiratória no
primeiro top-3. Não separa causalmente o efeito da recuperação e o do relato na
decisão. Os casos novos não têm adjudicação veterinária nesta rodada. Próximo
experimento deve comparar relatos equivalentes, presença/ausência de contexto e
recuperação, com revisão clínica; não criar uma regra a partir de uma frase só.

## API, formulário e interface

Os quatro smokes tiveram as mesmas classes finais, estados e número de turnos da
validação anterior: E/completed (1 turno), E/completed (2), I/insufficient (3),
E/completed (3). O último usa somente a opção `Não sai nenhum xixi`, origem form,
sem complemento. Total do runner API: 47,37 s agora versus 50,84 s anteriormente;
o polling e o provedor impedem interpretar essa diferença como ganho de produto.

Navegador: nove testes/59,36 s anteriormente; 12 testes/61,29 s agora. Os três novos
conferem a apresentação E/N/I, preservação da recomendação e justificativa original,
marca VetIA, filtragem visual de sinais vazios/duplicados e viewport móvel.
O restante cobre formulário, cadastro, persistência, mapa, consentimento, clínica
e mensagens. O aumento de testes não é uma porcentagem de cobertura de código.

Não reexecutamos nesta rodada as oito jornadas congeladas/14 pares de canal da
rodada 20. A nova comparação usa a calibração e os quatro smokes descritos acima;
os resultados dos 14 pares continuam históricos. Também não houve estudo de
compreensão com tutores: tom acolhedor e instruções visíveis são mudanças de
interface verificadas, não benefício humano já demonstrado.

## Decisões e próximos passos

1. Manter a alteração de apresentação: não alterou classes nos 36 pares nem
   acrescentou inferência; fontes/hashes coincidiram com a v2.
2. Priorizar a investigação clínica de relatos leigos como o caso manual, com
   revisão veterinária e avaliação reservada. Repetição consistente não torna
   uma resposta clinicamente adequada.
3. Priorizar prazo total de execução, política de retries e comunicação da espera:
   o timeout por HTTP não limita os 300 s de backoff observados.
4. Validar o benefício do formulário/texto com pessoas. Essa conclusão não pode
   ser extraída de fixtures de navegador nem de fornecer os mesmos fatos à LLM.

Todos os artefatos antigos permaneceram intactos. O snapshot compara hashes de
código/dados durante a rodada e com a v2; os resultados completos, comandos,
transcrições, métricas, capturas e integridade estão na pasta vinculada acima.
Não houve merge, push, mudança de implantação remota ou publicação de PR nesta rodada.
