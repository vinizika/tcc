# Repetição após correções do PR #16

[Relatório da rodada 20](../2026-10-02-20-correcao-regressoes-conversacionais.md).

- `protocolo.md`: critérios definidos antes das chamadas e adendo de compatibilidade.
- `cases.json`, `freeze.json`, `baseline_workspace.py`: entradas históricas intactas.
- `code-and-data-fingerprint.json`: hashes da implementação/dados usados.
- `actions.json`: opções efetivamente disponíveis e complementos literais dos fatos
  congelados, selecionados antes da fase `finish`.
- `auditoria-formularios.csv`: auditoria de engenharia de atomicidade, normalidade,
  alinhamento e estabilidade das chaves; não é revisão clínica independente.
- `raw.jsonl`: turnos reais, chamadas/tokens/tentativas e hashes dos prompts.
- `summary.json`, `turns.csv`: agregações derivadas dos registros.
- `*-runtime.log`: logs preservados por fase.
- `validacao.md`: testes, comandos e incidentes de ambiente.
- `final-integrity.json`: comparação dos canais, integridade e comparação histórica.

Recalcular métricas sem chamar provedores:

```sh
.venv/bin/python scripts/report_conversation_eval.py evidencias/vini/2026-10-02-correcao-conversacional
.venv/bin/python scripts/audit_conversation_eval.py evidencias/vini/2026-10-02-correcao-conversacional --previous evidencias/vini/2026-09-28-avaliacao-conversacional
```

As chamadas reais usaram o mesmo comando abaixo, sequencialmente para `baseline`,
`prepare`, `finish` e `recheck`. Entre `prepare` e `finish`, inspecionaram-se os
formulários e congelaram-se as ações. Reutilizar esta pasta apenas retoma a rodada;
para outra medição, criar outro diretório e outro banco, sem sobrescrever resultados.

```sh
.venv/bin/python scripts/run_conversation_eval.py --phase baseline --output-dir evidencias/vini/2026-10-02-correcao-conversacional --mongo-database tcc_followup_eval_20261002
.venv/bin/python scripts/run_conversation_eval.py --phase legacy_recheck --output-dir evidencias/vini/2026-10-02-correcao-conversacional --mongo-database tcc_followup_eval_20261002 --legacy-dir evidencias/vini/2026-09-28-avaliacao-conversacional
```

`recheck` repete c03 com o formulário novo. `legacy_recheck` reconstrói o histórico
e a resposta exatos de 28/09 no banco novo. As rechecagens não aumentam a amostra
de oito diálogos nem representam novos casos independentes.
