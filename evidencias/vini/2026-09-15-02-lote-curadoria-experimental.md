# Lote 02 — curadoria e staging experimental

**Data local:** 15/09/2026 (staging concluído em 16/09/2026 UTC)

**Branch:** `codex/lote-02-curadoria`

**HEAD inicial:** `c276580f7d3468c4bd7a59022f5b7733457ca5c8`

**Escopo:** `anticoagulant_rodenticide_poisoning`,
`parvovirus_panleukopenia` e `pyometra`

## Resultado

Os três tópicos foram confirmados como `sem_documento` antes da pesquisa e
agora estão como `fonte_encontrada`, mantendo `validacao=rascunho`. Quatro
fontes originais foram preservadas com licença explícita e fichas
`pending_specialist` / `experimental_only`. Nenhuma aprovação clínica foi
declarada.

Uma coleção experimental foi criada somente em staging:

- coleção: `veterinary_documents__20260916T023515657332Z__ba6c6368`;
- documentos: 4;
- chunks: 49;
- ativada: **não**;
- ponteiro ativo depois do staging: inexistente;
- coleção usada pela API: `veterinary_documents`, vazia, com 0 chunks.

## Fontes aceitas para captura experimental

| Tópico | Fonte | Idioma / espécie | Direito | SHA-256 | Sidecar SHA-256 | Chunks |
|---|---|---|---|---|---|---:|
| raticida anticoagulante | [Stroope et al., Frontiers 2022](https://doi.org/10.3389/fvets.2022.879179) | en · cão | CC BY 4.0 | `c8c9ed5eae1ab33d7e918beb45f98aa63649073ffc4e7af9fbce6bfdd6e29f01` | `34f5a5fa0096e03f7062775d072208990d1e2bdac704724d8955ffc2291adb81` | 19 |
| parvovirose | [Zhou et al., Microorganisms 2025](https://doi.org/10.3390/microorganisms13010047) | en · cão | CC BY 4.0 | `16dcc62d5b4f980ea5f2c536795250ac929289dfc4a1a5660b568a58f9e3e920` | `d4017306dd08afeec4c7bc6bbaf644893fe38c9bf749a9109d38d6c051ba160f` | 9 |
| piometra | [Xavier et al., Animals 2023](https://doi.org/10.3390/ani13213310) | en · cão | CC BY 4.0 | `c8e169d07f3aea9e0ca2b063c257301a56e0b9305f83aa1a3d7258e3fc50d35b` | `c314929b3a356ba66ca55b011f1d9d5bcfe405aebbc85caa84136e93ee5bcc58` | 7 |
| piometra | [Silveira et al., ABMVZ 2013](https://www.scielo.br/j/abmvz/a/s8WXqc8QPnRq33ZqdyGDnvq/?lang=pt) | pt · cão e gato | CC BY-NC 4.0; uso não comercial autorizado pelo responsável do projeto | `bd8ee6a25991db66eac086333b0b0c85179c19a4ff649c60215ffec5b9401687` | `600e60a41fd7e37533fe58fd670dea8c0dbf2ebea64a8978953f790117403a2a` | 14 |

As licenças foram verificadas nas páginas e nos próprios artigos. O
responsável autorizou a captura das fontes CC BY/CC BY-NC em 15/09/2026. Essa
autorização de armazenamento não foi tratada como validação clínica.

## Fontes rejeitadas após inspeção

- Melo, Oliveira e Lago, CRMV-SP/UFMG, 2002: embora redistribuível em CC BY,
  a extração reuniu diferentes pesticidas, doses e tratamentos em 221 chunks;
  a seção de raticidas não pôde ser isolada. Captura removida.
- Castro et al., PVB/UFRGS, 2014: CC BY-NC e pertinente à panleucopenia
  felina, mas o layout em colunas embaralhou figuras e sinais. Mesmo limitado
  à página 4, gerou 11 chunks parcialmente corrompidos. Captura removida.

## Fontes bloqueadas ou mantidas apenas como referência

- MSD Veterinary Manual (raticida e panleucopenia): direitos reservados.
- Dissertação da Universidade de Lisboa (raticida): ficha do repositório e
  aviso interno do PDF divergem sobre a permissão de reprodução.
- Elsevier 2020, *Update on Canine Parvoviral Enteritis*: direitos reservados.
- Cornell, *Pyometra*: sem licença inequívoca para redistribuir texto integral.
- Viruses 2022 sobre panleucopenia felina: CC BY e elegível, mas não capturada
  nesta rodada; fica como alternativa à extração brasileira rejeitada.

## Inspeção documental final

Todos os PDFs armazenados foram copiados temporariamente para
`backend/data/documents`, inspecionados individualmente com
`ingest_documents --inspect --file` e removidos depois do staging.

| Documento | Recorte | Resultado |
|---|---|---|
| Frontiers 2022 | `Introduction`, `Conclusions` | 19 chunks, 64–109 tokens, sem fallback |
| Microorganisms 2025 | página 1 de `Introduction` | 9 chunks, 51–94 tokens, 1 fallback lexical |
| Animals 2023 | `Clinical presentation` | 7 chunks, 62–92 tokens, sem fallback |
| ABMVZ 2013 | somente página 4 | 14 chunks, 57–113 tokens, 1 fallback lexical e seção neutra `Document` |

Tratamento, doses, métodos e referências não fazem parte dos recortes. O PDF
brasileiro de piometra menciona intervenção emergencial, mas não fornece dose
ou instrução terapêutica doméstica.

## Manifesto e integridade

- perfil: `experimental`;
- modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`;
- revisão: `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`;
- receita: `1a93e1e7db9a5b5a7766ca11b54162cb74cb76bb4d4c2c02b2dc0d5c4319682b`;
- conjunto de fontes: `ba6c6368cafc01994dacec7c47c086b1c5b4a2ca18727ef70ac769f0602469ee`;
- IDs dos chunks: `98fdac416595cd60513a92c945413e2e845b7fda9ec641c4c578e3300b678fdb`;
- conteúdo dos chunks: `d82fffaa98938b0caa0409e22d683fdc7b47465497178d564e8bb85d29f5709d`;
- hash canônico do manifesto no recibo:
  `543525e1a2da0a4fd4ddd83ab6cad58438d82a0a28ff3206d1107ce086446165`;
- SHA-256 dos bytes JSON formatados do manifesto:
  `01e7144f7cef5cf3a449501167aef2dc72db1018a484845bbce466363aaabb1a`;
- SHA-256 dos bytes JSON formatados do recibo:
  `f38c997739083bb68769fce79b80518d2feb3b8229d6338d35baca3ffdb828c9`.

`validate_collection_integrity` confirmou contagem 49, IDs e conteúdo. Os 11
warnings são esperados no perfil experimental: quatro documentos sem
aprovação clínica, quatro restritos ao uso experimental, dois fallbacks
lexicais e um fallback de estrutura. Não houve fragmento corrompido marcado
pelo processador.

## Encontrabilidade no staging

A consulta foi feita diretamente à candidata, sem alterar o ponteiro.

| Caso | Tópico esperado | Melhor posição | Melhor score | Passou 0,70? |
|---|---|---:|---:|---|
| b22 | `anticoagulant_rodenticide_poisoning` | 1 | 0,541824 | não |
| b23 | `parvovirus_panleukopenia` | 1 | 0,422639 | não |
| b24 | `pyometra` | 1 | 0,573632 | não |

O tópico esperado apareceu no top-5 em 3/3 casos e em primeiro lugar nos
três, mas nenhum resultado atingiu o limiar provisório de 0,70. A candidata
não deve ser ativada. O caso b23 é felino e a captura aceita é canina, logo a
boa posição não resolve a lacuna de espécie.

## Comandos e resultados reproduzidos

| Comando | Resultado |
|---|---|
| `.venv/bin/python -m pytest -q scripts/tests` antes das alterações | 186 passaram |
| `.venv/bin/python -m pytest -q scripts/tests` após os grupos e no final | 186 passaram em cada execução |
| `docker compose exec -T backend python -m pytest -q` | 203 passaram; apenas avisos de depreciação |
| `docker compose exec -T backend python -m pip check` | `No broken requirements found` |
| `.venv/bin/python -m compileall -q scripts backend/app` | código 0 |
| `docker compose config -q` | código 0 |
| validação JSON/YAML/CSV | 53 JSON, 3 YAML e 2 CSV válidos |
| `git diff --check` | código 0 |
| `validate_collection_integrity` | 49 chunks; hashes conferidos |

Uma tentativa de inspecionar seis PDFs em paralelo excedeu a memória do
Docker: dois processos terminaram com código 137 e os demais não produziram
relatório completo. Todas as inspeções foram refeitas sequencialmente. Os
URLs `/pdf` da MDPI também responderam 403; a captura foi repetida pelos URLs
estáticos oficiais `mdpi-res.com`. Por fim, uma primeira validação genérica de
YAML falhou porque `yaml.safe_load` não reconhece a tag válida `!override` do
Compose; `docker compose config` e a validação sintática por `yaml.compose`
passaram.

## Pendências

1. Especialista deve avaliar as quatro capturas; nenhuma está aprovada.
2. Encontrar fonte felina de panleucopenia com extração limpa.
3. Encontrar fonte redistribuível em português sobre raticida anticoagulante.
4. Melhorar a cobertura/escore dos três casos e repetir a régua.
5. Não ativar a candidata atual: todos os scores ficaram abaixo de 0,70.

Não houve commit, push, PR, ingestão `curated` ou mudança da coleção ativa.
