# Artefatos da rodada 17

Leia primeiro o [relatório de resultados](../2026-09-28-17-avaliacao-pre-triagem-conversacional.md).

| Arquivo | Uso |
|---|---|
| [protocolo.md](protocolo.md) | Desenho da comparação e adendos exploratórios identificados |
| [cases.json](cases.json), [freeze.json](freeze.json) | Entradas/expectativas congeladas e hashes |
| [baseline_workspace.py](baseline_workspace.py) | Fonte antiga de `6737665`, usada pelo runner |
| [code-and-data-fingerprint.json](code-and-data-fingerprint.json) | Fingerprint inicial de aplicação, dados e ferramentas |
| [final-integrity.json](final-integrity.json) | Conferência final, versões finais das ferramentas e hashes dos resultados |
| [raw.jsonl](raw.jsonl) | 145 turnos reais, ambientes e formulários preparados, sem pensamento bruto/credenciais |
| [summary.json](summary.json) | Métricas agregadas regeneráveis |
| [turns.csv](turns.csv) | Uma linha por turno; filtros por fase/braço/caso |
| [actions.json](actions.json) | Seleções verdadeiras definidas antes de responder aos formulários reais |
| [conversas.md](conversas.md) | Transcrições legíveis dos oito casos e braços pareados |
| [auditoria-formularios.csv](auditoria-formularios.csv) | Revisão de engenharia de pertinência/cobertura/consistência |
| `*-runtime.log` | Logs por fase, incluindo esperas 429/503 e aquecimento |
| `*-tests.txt`, `react-build.txt` | Saídas dos testes e build repetidos nesta rodada |

`baseline`, `prepare` e `finish` são o experimento principal. `ablation` e `recheck`
são análises exploratórias pós-achado, preservadas separadamente. Não somar
repetições como se fossem animais/casos independentes.

O erro de montagem de código no início de `baseline-runtime.log` ocorreu antes
da primeira chamada ao modelo; foi corrigido no runner e mantido no log. Não
houve substituição de resultados clínicos malsucedidos por respostas simuladas.

O benchmark roda serviços reais diretamente no container e usa Mongo separado.
Os testes de navegador usam a aplicação acadêmica local e, nos dois testes de
contrato do formulário, fixtures HTTP explicitamente identificadas. Nenhum teste
usou pacientes reais ou inferiu satisfação/tempo humano.

Para recalcular sem rede:

```sh
.venv/bin/python scripts/report_conversation_eval.py \
  evidencias/vini/2026-09-28-avaliacao-conversacional
```

Para novas chamadas reais, veja os comandos do relatório. Crie outra pasta,
confira as opções efetivamente geradas e não reutilize IDs/seleções desta rodada
como se fossem formulários novos.
