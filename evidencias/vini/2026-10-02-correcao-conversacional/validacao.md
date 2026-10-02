# Verificações da implementação

Executadas em 02/10/2026, sem chamadas simuladas contadas como avaliação clínica.

- `DEBUG=true .venv/bin/python -m pytest -q backend/tests`: 340 aprovados.
  Inclui separação do texto de busca/roteamento, preservação do primeiro relato,
  igualdade de entradas dos dois canais, complemento com informação nova,
  perguntas/opções estáveis e término quando não há discriminador no catálogo.
- `DEBUG=true .venv/bin/python -m pytest -q scripts/tests`: 222 aprovados na
  execução final, após acrescentar o teste que isola a rechecagem do histórico v1.
- TypeScript (`tsc -b`) e Vite (`vite build`): aprovados com Node 22.23.3.
- Playwright `tests/followup.spec.ts`: quatro aprovados em 5,3 s contra Vite
  `http://127.0.0.1:5173`, com Node 22.23.3. Fixtures de API identificadas;
  cobrem recarga, confirmação da opção, texto complementar e envio único.
- `sync_retrieval_terms.py --check` e `sync_fichas.py --check`: consistentes.
- `git diff --exit-code d4af6d6 -- data backend/data backend/chroma_db/active_collection.json`:
  sem alteração das fichas, datasets ou ponteiro versionado.

Incidentes de ambiente conservados neste registro: a primeira coleta de testes
herdou `DEBUG=release` do ambiente e foi rejeitada antes da execução; a repetição
usou `DEBUG=true`. O Node padrão 18 concluiu o build com aviso, mas foi recusado
pelo Playwright; a validação final usa Node 22.23.3 já disponível localmente.

Os primeiros dois testes Playwright apontaram para a imagem antiga em `:3000`,
com API em `/api`, enquanto as fixtures interceptavam somente `:8000`; falharam
ao localizar o formulário. Repetidos contra o código atual no Vite em `:5173`,
os dois passaram. As fixtures foram ampliadas para aceitar ambos os caminhos
de API e exercitar também alimentação normal e alternativa livre.

O benchmark real usa processos novos no container com o código montado do
workspace; não depende de a API Uvicorn antiga ter recarregado os módulos.
Não confundir tempo de serviço do benchmark com latência percebida no navegador.
