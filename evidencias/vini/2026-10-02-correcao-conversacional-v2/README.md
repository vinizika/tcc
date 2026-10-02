# Versão final — histórico clínico legível

[Relatório completo](../2026-10-02-20-correcao-regressoes-conversacionais.md).

Nova execução completa, após a primeira tentativa registrar uma decisão INCERTO
em seis chamadas de c03 com o histórico antigo. O resultado anterior fica intacto
em `../2026-10-02-correcao-conversacional/`. A única mudança adicional no produto
foi a representação do histórico, agora textual com relato atual separado.

Esta pasta contém o protocolo, casos/baseline congelados, fingerprint do código,
ações escolhidas antes das respostas, auditoria das opções, resultados brutos,
logs por fase, métricas derivadas e auditoria final de integridade e prompts.
As rechecagens de c03 não contam como novos casos independentes.

Executar o runner nesta pasta retoma a execução existente. Para uma medição nova,
usar nova pasta e banco e inspecionar novamente os formulários reais.

```sh
.venv/bin/python scripts/run_conversation_eval.py --phase baseline --output-dir evidencias/vini/2026-10-02-correcao-conversacional-v2 --mongo-database tcc_followup_eval_20261002_v2
```

Fases executadas sequencialmente: `legacy_recheck` (com `--legacy-dir
evidencias/vini/2026-09-28-avaliacao-conversacional`), `baseline`, `prepare`,
inspeção e congelamento de `actions.json`, `finish`, `recheck`.

Recalcular sem novas chamadas ao provedor:

```sh
.venv/bin/python scripts/report_conversation_eval.py evidencias/vini/2026-10-02-correcao-conversacional-v2
.venv/bin/python scripts/audit_conversation_eval.py evidencias/vini/2026-10-02-correcao-conversacional-v2 --previous evidencias/vini/2026-09-28-avaliacao-conversacional
```

Testes de implementação e incidentes iniciais de ambiente estão no
[registro de validação](../2026-10-02-correcao-conversacional/validacao.md).
As saídas completas das suítes finais, da API e do navegador estão no
[pacote de validação final](../2026-10-02-validacao-final/README.md).
Após simplificar o histórico, a suíte completa de 340 testes backend foi
executada novamente e passou. Os dados clínicos da rodada são sintéticos.
