# Protocolo congelado antes das chamadas

## Objetivos e amostra

1. Regressão de classificação: todos os 18 casos de
   `data/prova/casos_calibracao.csv` (9 EMERGENCIA, 8 NAO_EMERGENCIA, 1 INCERTO),
   dois ciclos por caso, dois braços. Total planejado: 72 decisões, mais aquecimento.
2. Acompanhamento: oito casos sintéticos novos, com relato inicial incompleto e
   fatos finais congelados antes da execução (3 E, 3 N, 2 I). Não são rótulos
   validados por veterinários. Expectativa inicial: INCERTO nos oito casos.
3. Formulário: para cada caso que chegar naturalmente a `form`, clonar o mesmo
   estado persistido para quatro braços. O relato/fatos são sintéticos; perguntas,
   opções, RAG e decisões vêm do provedor real, sem dublês.

Não usar prova 2 nem conjunto final congelado como desenvolvimento. Os rótulos
da calibração são provisórios no arquivo de origem. Acurácia aqui é concordância
com esses rótulos, não acurácia clínica validada/generalizável.

## Braços

- `before`: WorkspaceService extraído literalmente de `6737665`, antes das
  mudanças conversacionais, com o pipeline e configuração preservados.
- `after`: WorkspaceService em desenvolvimento, sem ajustar prompts com base
  nos resultados desta rodada.
- `after_form`: opção real do formulário; complemento apenas quando necessário
  para expressar fatos já congelados.
- `after_same_text`: mesma cadeia de caracteres, mesmo histórico e mesmo backend
  novo, mas origem `text`. Isola o efeito da origem estruturada, não o efeito humano
  de descobrir/observar informação após ver opções.
- `before_same_text`: mesmo histórico do tutor e mesma cadeia de caracteres,
  processados pelo serviço antigo. Recebe gratuitamente a informação elicitada
  pelo novo fluxo; é um controle favorável ao sistema antigo, não sua UX original.
- `after_no_data`: mesmo formulário, resposta “Não observei”, sem novo fato.
  O esperado é continuar INCERTO, não adivinhar o estado oculto do animal.

A etapa `prepare` termina antes de responder ao formulário. As opções retornadas
serão inspecionadas e mapeadas manualmente apenas a fatos congelados. Pergunta sem
opção compatível usa “Não observei” com o fato congelado em complemento, e isso
será identificado como ganho por texto novo, não como sucesso das opções.
Se o sistema concluir antes de oferecer formulário, não forçaremos seu estado.

## Execução e medição

Provedor Gemini real; mesma coleção Chroma ativa, nenhum novo documento. Banco
Mongo separado `tcc_followup_eval_20260928`, sem substituir conversas da equipe.
Chamadas sequenciais, ordem before/after alternada entre casos e ciclos.
Aquecimento medido e excluído das distribuições estáveis. A execução chama os
serviços reais diretamente no container: tempo inclui submit, Mongo, recuperação,
LLM(s) e persistência; não inclui HTTP, fila assíncrona, polling, renderização ou
latência humana. A comparação de UX humana exige outro estudo.

Instrumentação envolve os clientes reais sem mudar seus argumentos/resultados.
Por turno: classe, schema válido, estado, pergunta, opções, motivo do formulário,
fontes/configuração, duração externa, duração de cada etapa LLM, tokens reportados,
tentativas e erros. Os tokens dos clientes existentes refletem a última resposta
na chamada; múltiplas tentativas podem subestimar consumo. Sem preço monetário
estimado, pois tokens/cota e contrato de cobrança precisam de medição própria.

Métricas: acurácia exata de três classes, macro-F1, matriz de confusão,
recall de emergência, emergência rebaixada a NAO_EMERGENCIA, emergência abstida,
cobertura binária, latência média/mediana/p95, tokens/chamadas por decisão,
resolução de INCERTO com e sem novos dados, conversas que chegaram ao formulário,
progresso e classificação final dos braços pareados.

As duas repetições do mesmo caso não são amostras independentes. Intervalos da
diferença de acurácia serão obtidos por bootstrap agrupado por caso (seed 42).
O conjunto é pequeno, de conveniência, já usado em desenvolvimento; não se fará
alegação de causalidade humana, eficácia clínica ou significância populacional.

## Rastreabilidade

`cases.json`, `freeze.json` e `baseline_workspace.py` congelam entradas e baseline.
`raw.jsonl` será incremental: erros não são substituídos por resultados fictícios.
`actions.json` identificará as respostas factualmente permitidas para cada
formulário real. `summary.json`, CSVs e relatório serão derivados desses registros.

## Adendo exploratório após a comparação principal

A comparação principal revelou regressão em p11 e p14 nas duas repetições,
com mudança nas fichas recuperadas. Antes de investigar, foi definida uma
ablação adicional: duas repetições de p11/p14 e dois controles (p01/p02), usando
o prompt clínico e a orquestração novos, mas apenas o relato do tutor como
consulta vetorial. A transformação é injetada somente no processo do benchmark;
não modifica a aplicação. O objetivo é testar a hipótese de que as instruções/
JSON adicionados ao texto de busca afetaram o RAG. O resultado será separado da
comparação confirmatória, por ter sido escolhido depois de observar as falhas.

## Decisão de execução após inspecionar os formulários

Os oito casos chegaram a formulário após uma resposta “Não sei dizer”. Todos
acionaram `repeated_question`, sem aguardar uma segunda resposta sem progresso.
As respostas foram registradas em `actions.json` antes do envio aos braços.

Em c05, o tutor sabe que comeu normalmente, mas nenhuma opção permite afirmá-lo.
Esse caso não terá braço `after_form`: responder “Não observei” nesse contexto
seria falsear os fatos. Executaremos os dois braços de texto com o fato congelado
e o controle contrafactual sem dados. Isso reduz a amostra de formulário para
sete casos (cinco com fatos novos, dois desconhecidos); a indisponibilidade da
opção será contabilizada, não apagada.

Em c02/c03, o tutor não sabe a informação perguntada (cor da mucosa/apetite), mas
tem um novo sinal grave diferente. Nesses dois casos “Não observei” é verdadeiro
para a pergunta, e o sinal grave entra no complemento. Não se atribuirá esse
resultado às opções predefinidas. Em c01/c04/c06, a opção é compatível com parte
dos fatos congelados; o complemento conserva o restante, sem inventar respostas.

## Adendo de estabilidade após os primeiros braços pareados

Em c03, a mesma resposta trouxe EMERGENCIA por formulário e INCERTO por texto,
com as mesmas três fichas. Isso não basta para atribuir causalidade ao formulário.
Será feita uma rechecagem exploratória de três pares adicionais, a partir do
mesmo estado anterior à resposta, alternando a ordem das duas origens. Essa
rechecagem será reportada separadamente, sem aumentar artificialmente o número
de casos independentes nem substituir o resultado inicial.
