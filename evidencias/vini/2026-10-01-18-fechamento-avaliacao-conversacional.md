# Rodada 18 — fechamento da avaliação conversacional

Retomada em 01/10/2026 da avaliação executada em 28/09. A coleta real já estava
concluída; faltava entregar o fechamento ao usuário. Não foram feitas novas
chamadas ao Gemini nem repetidas as medições de latência nesta retomada.

## Conferências executadas nesta retomada

- Todos os hashes de artefatos em `final-integrity.json` conferiram.
- A execução de `scripts/report_conversation_eval.py` regenerou `summary.json`
  com conteúdo idêntico byte a byte.
- Os quatro testes de métricas em `scripts/tests/test_report_conversation_eval.py`
  passaram novamente, incluindo isolamento das rechecagens exploratórias.
- `git diff --check` passou.

## Resultado entregue

O [relatório da rodada 17](2026-09-28-17-avaliacao-pre-triagem-conversacional.md)
contém 145 turnos reais, 185 chamadas lógicas ao Gemini, dados brutos, matrizes,
latências, consumo, transcrições, controles e auditoria dos formulários.

Em 18 casos de calibração, repetidos duas vezes por versão, a concordância com
os rótulos provisórios foi de 34/36 (94,44%) antes para 30/36 (83,33%) depois.
O consumo reportado aumentou 36,0%. A mediana de latência ficou em 2,89 s antes
e 2,99 s depois, com influência de backoff do provedor nas caudas.

Sete formulários tinham resposta factualmente possível e chegaram à expectativa
final; um omitia a opção normal. Oito controles sem dados permaneceram INCERTO.
A diferença repetida entre texto e formulário com os mesmos fatos em c03 é uma
fragilidade de consistência. Não foi demonstrada eficácia humana do formulário.

A ablação exploratória indica que regras/JSON na consulta vetorial prejudicaram
a recuperação nos dois casos que regrediram. A aplicação medida foi preservada;
as correções identificadas continuam pendentes e não foram misturadas à avaliação.

Os 330 testes backend, 221 de scripts, sete testes de navegador e o build React
registrados no pacote foram executados em 28/09; não são apresentados como novas
execuções em 01/10. Os dados da prova final, fichas e coleção ativa não foram
alterados. Não houve commit ou push nesta retomada.
