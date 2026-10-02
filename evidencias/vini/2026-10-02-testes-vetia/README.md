# Dados da rodada 24 — VetIA

Síntese e interpretação: [rodada 24](../2026-10-02-24-nova-rodada-vetia.md).

## Arquivos

- `protocolo.md`: escopo definido antes da execução.
- `snapshot.json`, `code-and-data-fingerprint.json`: versão, diff local e hashes.
- `cases.json`, `baseline_workspace.py`, `freeze.json`: cópias byte a byte da
  comparação anterior; a data interna de freeze é a original, não esta execução.
- `raw.jsonl`, `baseline-runtime.log`, `calibration.log`: 73 turnos instrumentados,
  com aquecimento, chamadas, tokens, fontes, hashes e esperas do cliente.
- `summary.json`, `turns.csv`: agregação e linhas da calibração; campos de jornadas
  não executadas aparecem vazios, nunca devem ser interpretados como aprovados.
- `api-smoke.json`, `api-smoke.log`, `api-assertions.json`: quatro cenários reais.
- `manual-cases.json`, `manual-raw.jsonl`, `manual.log`: exploração do relato
  manual e controles, separada da calibração.
- `comparison.json`: comparação pareada com PR16 original e correção v2,
  exploração, smokes, browser e conferência dos hashes de código.
- `commands.jsonl`, `*.log`: comandos, códigos de saída, duração e resultados.
- `browser-tests.json`, `browser-live-input.json`, `screenshots/`: execução dos
  12 testes e identificação da conversa real usada no encaminhamento.
- `diagnostico-espera.md`: investigação das esperas HTTP 503/429 e limites causais.
- `integrity.json`: hashes dos artefatos finais, integridade histórica e busca
  de padrões de credenciais. Nenhuma chave real é necessária nos artefatos.
- `run_round.py`, `run_manual.py`, `compare.py`, `finalize.py`: scripts desta
  rodada. O orquestrador preserva caminhos desta máquina para rastreabilidade.

## Reproduzir agregação sem chamadas externas

Na raiz do repositório:

```sh
.venv/bin/python scripts/report_conversation_eval.py evidencias/vini/2026-10-02-testes-vetia
.venv/bin/python evidencias/vini/2026-10-02-testes-vetia/compare.py
```

Uma nova execução com Gemini deve usar outra pasta e banco, copiando o protocolo
e entradas antes de começar. Não execute novamente os runners sobre este pacote
fechado: eles podem sobrescrever logs ou acrescentar repetições à amostra.

Não contém prova clínica independente nova, estudo humano, teste de carga ou
medição de desempenho Ollama. São verificações locais e casos sintéticos.
