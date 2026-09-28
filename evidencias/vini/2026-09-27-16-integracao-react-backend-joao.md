# Integração do frontend React ao backend do João — 27/09/2026

## Base e preservação

Origem atualizada por `git fetch origin`: `e365f3e2d6e6f50145afc44ba52d5cb1926479e9`.
Trabalho local preservado antes do merge no commit `077da3d`, na branch
`codex/integrate-joao-react`. A análise documental antecedente está na
[auditoria correta do João](2026-09-27-15-auditoria-joao-peterutto.md).
Nenhum push foi realizado. Credenciais permanecem exclusivamente no `.env`
ignorado; não estão neste registro nem no código.

## Conflitos e decisões

- Chroma binário: adotado o snapshot do João, com ponteiro para as 61 fichas
  `veterinary_documents__20260925T061349534255Z__280baf13`. A coleção local
  anterior é recuperável no commit de preservação. Não houve reingestão.
- Contratos: preservado o fingerprint novo e mantida a autenticação/proteção
  de titularidade implementada no fluxo local. Não foi reintroduzido acesso
  por ID sem sessão nas rotas protegidas.
- A configuração local ainda fixava a antiga coleção acadêmica de artigos.
  `POC_RAG_COLLECTION` agora fica vazio: workspace acompanha o ponteiro ativo.
- Chroma escreve arquivos mesmo durante uso de consulta. Com backend parado,
  a base foi copiada para `backend/data/chroma/runtime-joao-e365f3e`, ignorado
  pelo Git. `CHROMA_PATH` local aponta para essa cópia; arquivos versionados
  foram restaurados exatamente a `e365f3e`. Atualizações futuras do snapshot
  exigem atualização explícita da cópia, não uma migração automática.
- Autenticação, pets, histórico Mongo, Maps e encaminhamentos foram mantidos;
  pipeline científico, fichas, prompts e resultados de ablação não foram
  reescritos para adaptar a interface.

## Adaptação do chat

O workspace mantém envio assíncrono (HTTP 202) e consultas de estado. Usa
busca vetorial BGE-M3, três fichas de leitura, sem corte de score e sem
reescrita/multi-query/HyDE. Contexto anterior contém apenas relatos do tutor;
o relato atual não é truncado. Contexto cadastral do animal continua separado.

A interface oferece Gemini/nuvem ou Ollama/local e informa o envio do relato
e contexto do animal ao Google. Gemini é o padrão; fallback está desativado.
A escolha é persistida por envio. Modelo local depende da instalação do
modelo configurado; não se afirma aqui que Qwen foi validado nesta máquina.

Respostas persistem procedência (modelo, versão, provedor e eventual troca),
configuração, tempos, coleção e referências completas das fichas. A interface
exibe provedor/modelo, títulos e links HTTP(S) das referências. Conversas
antigas sem esses campos continuam renderizando. Erros de cota/provedor têm
código e mensagens específicas, sem expor texto bruto upstream. Retentar o
mesmo relato após falha não duplica a mensagem do tutor. INCERTO não é exibido
como uma falsa certeza de que faltam informações.

## Verificações executadas

- Build Docker backend e frontend: concluído; TypeScript/Vite compilam.
- Backend: **315 testes passaram** no container com dependências do projeto.
  Comando: `docker compose exec -T -e CHROMA_PATH=chroma_db backend python -m pytest tests -o addopts= -q`.
  O caminho explícito isola a suíte de um override operacional local.
- Scripts de pesquisa: **217 testes passaram** (`DEBUG=false GEMINI_API_KEY= .venv/bin/python -m pytest scripts/tests -q`).
- Navegador real: **5 testes passaram**, sem respostas de API/modelo simuladas:
  entrada e pet persistente; conta própria; mobile/Maps; encaminhamento com
  consentimento, localização e chat tutor-clínica; clínica pendente sem acesso.
  Comando em `frontend-react/`: `LIVE_RAG_CONVERSATION_ID=adab75f2-3ae0-47a8-b1d0-fcfd477db71e npx -y -p node@22 node node_modules/@playwright/test/cli.js test`.
- Busca real: coleção ativa com **61 registros**, consulta fictícia de retenção
  urinária trouxe obstrução uretral em primeiro lugar.
- Gemini real: credencial acessou `gemini-3.5-flash-lite`; relato fictício
  de gato sem urinar há oito horas foi analisado pelo workspace e salvo como
  **EMERGENCIA**, com três fichas, referências nas três fontes (2/1/1), versão
  do modelo e `fallback_from=null`. Esta é uma prova de integração, não uma
  nova medição de acurácia ou validação clínica.

Os testes criaram contas, pets e encaminhamentos fictícios identificados como
teste no Mongo local. Nenhum cadastro clínico externo foi enviado ou alterado.
Houve avisos de depreciação das dependências, sem falhas na rodada final.

## Limites

Entrega executável local, não publicação em produção. Mantêm-se os limites
de contas acadêmicas compartilhadas, aprovação manual de clínicas, fila
BackgroundTasks não durável e necessidade de endurecimento operacional.
O carregamento inicial do BGE-M3 baixa pesos e consome memória significativa;
o cache Hugging Face está em volume persistente. O desempenho medido pelo
João continua sendo o das suas rodadas, não o destes testes funcionais.

Operação e configuração: [POC utilizável](../../docs/poc-utilizavel.md).
