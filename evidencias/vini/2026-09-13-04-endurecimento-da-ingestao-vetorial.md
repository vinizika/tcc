# Endurecimento da ingestão vetorial — reconstrução

**Data:** 13/09/2026 · **Trilho:** A — Recuperação e Conhecimento · **Rodada:** 4

## Resultado

A alteração perdida foi reconstruída na branch
`codex/harden-vector-ingestion`, a partir do HEAD inicial
`c3f09ec5c6a5608e2039a0651a0dec437d19479b`. Nenhuma coleção do projeto foi
alterada: as materializações reais ocorreram somente sob `/private/tmp`.

O fluxo agora prepara todos os documentos antes de abrir o Chroma, aplica os
perfis `curated`, `experimental` e `legacy_rechunk`, escreve em coleção
versionada, exige manifesto, confere contagem e hashes antes da ativação e
preserva rollback. A resolução de ponteiro ativo é estrita e não usa
`get_or_create_collection`.

O corpus `curated` permanece com zero documentos elegíveis. Nenhum documento
foi aprovado clinicamente nesta rodada e nenhuma captura foi tratada como
curada. Os oito documentos existentes foram marcados `experimental_only`; as
cinco capturas permanecem `curated_candidate`, com direitos e aprovação
pendentes.

## Receita reconstruída

Modelo e tokenizer estão fixos em
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, revisão
`e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. A serialização literal da
receita perdida não estava disponível; a reconstrução recebeu uma identidade
nova, `vector-ingestion-recovery-v1`, com hash reproduzido
`1a93e1e7db9a5b5a7766ca11b54162cb74cb76bb4d4c2c02b2dc0d5c4319682b`.

Não houve tentativa de fabricar o hash histórico
`64952a575f5ebf686ef83e595c4f30593f5461f198b15eee0c19a8397bf25c93`.
Os IDs dos chunks coincidiram com o registro de recuperação, mas os hashes de
fontes e conteúdo mudaram porque a receita/sidecars reconstruídos têm nova
identidade.

| Perfil | Documentos | Chunks | `source_set_sha256` | `chunk_ids_sha256` | `content_sha256` |
|---|---:|---:|---|---|---|
| `legacy_rechunk` | 7 | 73 | `6e5c03049c17c3730af55d5ba0747514bdc4993f7383a7588a98fcd6a4e6dde5` | `eefb077334cfc25ca9b0b4ef8d4791ad25fd07a79c47712db4483d7e05fcbaba` | `c37090bb263e45b8039323785ac1e2e8ab4c37ca283159e14453dbb90e8478f7` |
| `experimental` | 8 | 259 | `5c578a44d8d130f39db2ef333542b2e3128704cffa62d096338853a20a4b4d9e` | `0f0c383c3835e41dd9520c0444e66aea6dde544fb387bb04fa011ca2ceb2a6ed` | `598545e66d32b42461cab2036acf0fcb662212afea9a237d0e47229d83ce3bbd` |

O perfil legado teve tokens mínimo/médio/mediano/máximo de
55/82,658/82/128. O experimental teve 48/86,768/92/128, 31 fallbacks de
frases longas e um fragmento inicial corrompido removido. São medições
técnicas, não validação clínica nem prova de qualidade do RAG.

## Verificações executadas

| Verificação | Comando resumido | Resultado reproduzido |
|---|---|---|
| Linha de base | `pytest backend/tests`; `pytest scripts/tests` antes das alterações | backend aprovado com `DEBUG=true`; scripts 164 aprovados |
| Backend final | `DEBUG=True python -m pytest -o addopts='' backend/tests -q --disable-warnings` | **201 aprovados**, 18 avisos de dependências, 0 falhas |
| Scripts final | `python -m pytest scripts/tests -q` | **185 aprovados**, 0 falhas |
| Chroma real temporário | `test_chroma_ingestion_integration.py` | 9 cenários reais aprovados com embedding determinístico |
| Dependências | `python -m pip check` | `No broken requirements found` |
| Compilação | `python -m compileall -q backend/app scripts` | aprovado |
| Diff | `git diff --check` | aprovado |
| Curated vazio | `ingest_documents --profile curated --stage-only` | código 2; diretório Chroma não criado |
| Legado real | `ingest_documents --profile legacy_rechunk --activate` | 7 documentos, 73 chunks, manifesto e hashes válidos |
| Experimental real | `ingest_documents --profile experimental --activate` | 8 documentos, 259 chunks, manifesto e hashes válidos |
| Rollback real | `ingest_documents --rollback` | coleção experimental retornou à candidata legada anterior |
| Consenso | manifesto + recibo + fingerprint + estado real | `status: consensus`, 73 chunks |
| Busca real | consulta de heatstroke na candidata experimental | top-5 de `canine_heatstroke`; todos com corpo limpo |
| JSON/YAML | leitura de JSON; PyYAML; `docker compose config --quiet` | aprovado |
| Docker build | `docker compose build backend frontend` | não concluído: Docker Desktop informou que não consegue iniciar |

Total reproduzido: **386 testes aprovados** (201 backend + 185 scripts).

A busca real teve scores 0,698586; 0,690476; 0,664504; 0,650005 e
0,649911. Nenhum chegou ao corte 0,70. Esse smoke confirma integração e corpo
limpo; não substitui a régua nem autoriza conclusão clínica.

## Correção do comparador

O compare agora preserva `fingerprint.json` por rodada e usa somente o
inventário daquela execução. Tópico novo é a diferença real entre inventários;
cobertura exige a espécie esperada; “encontrável” exige que o tópico apareça
num caso que o espera. Rodadas históricas sem inventário recebem fallback
conservador.

A antiga conclusão do B-55 não era demonstrada: o comparador lia sidecars do
checkout atual e contava tópicos retornados em casos que não os esperavam. Os
resultados brutos históricos não foram reescritos; a errata foi registrada no
backlog e na documentação da régua.

## Limitações e pendências

- O Docker Desktop desta máquina não iniciou; Compose foi validado, mas imagens
  e containers não puderam ser construídos/executados localmente.
- O workflow de CI foi criado, mas só poderá ser observado depois do push/PR.
- Não houve consenso entre as três máquinas do time; apenas consenso interno
  entre os quatro artefatos da execução temporária.
- A base curada continua vazia. Aprovação especialista, direitos, revisão do
  mapa/gabarito e a virada clínica permanecem ações humanas pendentes.
- B-35 continua aberto para as fusões lexicais residuais do PDF; não foi
  inventada correção sem evidência estrutural.
- A busca smoke não é uma rodada da régua e não deve ser citada como ganho de
  recuperação.
- O repositório segue sem decisão registrada sobre privacidade/licença do
  paper de terceiro já presente.

Os comandos, hashes e resultados estruturados estão no
[`JSON da rodada`](2026-09-13-04-endurecimento-da-ingestao-vetorial.json).
