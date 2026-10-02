# Validação final da correção conversacional

Logs completos das verificações finais. Os dados de aplicação usados nos testes
reais são sintéticos, em implantação acadêmica local. Não são pacientes reais.

| Verificação | Artefato | Resultado |
|---|---|---|
| Backend | `backend.txt` | 340 aprovados |
| Scripts | `scripts.txt` | 224 aprovados |
| Protótipo preservado | `mock.txt` | 10 aprovados |
| TypeScript | `typescript.txt` | exit 0 |
| Vite/React com Node 22.23.3 | `vite.txt` | build concluído |
| Fichas e vocabulário | `fichas.txt`, `vocabulario.txt` | consistentes |
| Compilação Python | `compile.txt` | exit 0 |
| API/Gemini/Mongo reais | `api-smoke.json`, `api-assertions.json` | quatro cenários aprovados |
| Playwright | `browser-tests.json` | nove aprovados; zero pulados, falhas ou flaky; 59,36 s |

`commands.json` registra comandos, diretórios, códigos de saída e duração.
`screenshots/` preserva as cinco capturas produzidas nos testes reais: entrada,
chat, clínica, chat móvel e mapa móvel.
`DEBUG=true` foi passado explicitamente para não herdar `DEBUG=release` do ambiente.
Os incidentes iniciais e sua investigação estão no
[registro da primeira tentativa](../2026-10-02-correcao-conversacional/validacao.md).

## Integração real

Após terminar os benchmarks, verificou-se que não havia análise `processing` no
banco da aplicação (`vetai`). O backend local foi reiniciado para carregar a
versão final, e `/health/` respondeu `{"status":"ok"}`.

`api-smoke.json` contém as conversas e os resultados reais; `api-smoke.txt` contém
a saída do runner e `api-assertions.json` as expectativas/conferências. Cenários:
emergência imediata, incerteza resolvida por novo relato, formulário sem dados
novos e emergência revelada apenas por “Não sai nenhum xixi”, sem complemento.
Foram nove turnos reais nesses quatro cenários, concluídos em 50,84 s no total.

```sh
.venv/bin/python scripts/smoke_workspace_followup.py --provider gemini --output evidencias/vini/2026-10-02-validacao-final/api-smoke.json
```

Os testes de navegador usam o React atual no Vite em `http://localhost:5173`,
origem já permitida no CORS. `browser-tests.json` é o relatório completo do
Playwright; `browser-stderr.txt` preserva a saída de diagnóstico. A conversa real
do cenário de emergência alimenta o teste de encaminhamento à clínica acadêmica.
Quatro testes do formulário usam fixtures HTTP explícitas; cinco exercitam
API/Mongo/fluxos reais (entrada/cadastro/pet, cadastro próprio, busca/mapa móvel,
encaminhamento com consentimento e chat entre tutor/clínica, clínica pendente).

```sh
cd frontend-react
APP_URL=http://localhost:5173 LIVE_RAG_CONVERSATION_ID=ID_DA_CONVERSA_REAL npx playwright test --reporter=json
```

## Limites do ambiente e do escopo

O provedor medido é Gemini. O Ollama está acessível, mas só tem `llama3.2:3b`
instalado, enquanto o modelo local configurado é `qwen3:8b`. Portanto, não se
declara desempenho clínico real do Qwen nesta máquina. O contrato local e a
proteção contra estouro de contexto são cobertos pelos testes backend; a réplica
histórica do Qwen permanece na evidência do João de 25/09.

Não foram executados estudo com usuários, ensaio de carga concorrente, teste em
URL remota ou a prova clínica independente nesta rodada. Essas são validações
distintas; os dados atuais não representam esses resultados. Os cenários de
concorrência/idempotência, falha e retentativa são testes de contrato do backend,
além do teste de duplo envio na interface, não uma medição de capacidade de carga.
