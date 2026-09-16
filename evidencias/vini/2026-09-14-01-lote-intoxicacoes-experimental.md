# Lote 01 — intoxicações, staging experimental

**Data:** 14/09/2026

**Branch:** `codex/lote-01-intoxicacoes`

**HEAD inicial:** `ad9b55ff5754370a60ab63bc78fcd8773de77359`

**Escopo:** `human_medication_poisoning`,
`carbamate_organophosphate_poisoning` e `permethrin_toxicosis_cats`

## Resultado

Foram capturadas três fontes originais com licença de reutilização explícita.
Em 14/09/2026, o responsável do projeto informou a aprovação coletiva das
três fontes pela ASAVET — Primeiro Grupo de Anestesia e Veterinaria
Universitaria do Brasil. Não foi informado avaliador individual nem CRMV, e
essa limitação de proveniência fica registrada. As fontes continuam
`experimental_only`: nenhuma foi copiada definitivamente para
`backend/data/documents` ou ingerida pelo perfil `curated`.

Uma coleção experimental foi criada somente em staging:

- coleção: `veterinary_documents__20260914T154159080566Z__9106a62e`;
- documentos: 3;
- chunks: 24;
- ativada: **não**;
- ponteiro ativo depois do staging: inexistente;
- coleção usada pela API: `veterinary_documents`, vazia, com 0 chunks.

## Fontes aceitas para captura experimental

| Tópico | Fonte | Idioma / espécie | Direito | SHA-256 | Chunks |
|---|---|---|---|---|---:|
| medicamento humano | [Riboldi, Lima e Dallegrave, ABMVZ 2012](https://www.scielo.br/j/abmvz/a/ysbs3yBFpPWrYBgtv3hNn3F/?format=html&lang=pt) | pt · cão e gato | CC BY-NC 4.0; uso não comercial autorizado pelo responsável do projeto | `ed59061397a41e9560fde046c87e81d45f7d1eda5a2731282a377f9687be0030` | 7 |
| carbamato/organofosforado | [Jardim et al., ABMVZ 2021](https://www.scielo.br/j/abmvz/a/YZMjLkrv5SsSLqLw3qSXHKG/?lang=en) | en · gato | CC BY | `6094639a2a3700bbe048822761a8d46ceb1212687ed7ce14fe491192829e2c74` | 7 |
| permetrina | [Veterinary Medicines Directorate, 2014](https://www.gov.uk/government/publications/permethrin-dont-put-your-cat-at-risk) | en · gato | Open Government Licence v3.0 | `d4c156306be9da1593f0f89a757cacc4718a4495a95033049ff542b9fa9712e5` | 10 |

## Fontes bloqueadas por direitos

- VCA, PDSA, Cornell e University of Illinois: boas referências clínicas,
  mas sem autorização adequada para redistribuir o texto; a PDSA limita a
  cópia a uso pessoal e a VCA proíbe redistribuição sem permissão escrita.
- Centro Paula Souza: o repositório declara `all rights reserved`.
- Ciência Rural 2007 sobre aldicarb: artigo lido e mantido como referência,
  mas sem licença inequivocamente aplicável ao exemplar de 2007.

## Fonte rejeitada por adequação

- Di Pietro et al., Toxics 2022: CC BY, porém sinais e exposição aparecem
  misturados a doses e tratamento na mesma seção; não entrou na captura.

## Inspeção documental

Os arquivos foram copiados temporariamente para `backend/data/documents`,
inspecionados um a um com `ingest_documents --inspect --file` e removidos
depois. As capturas originais permanecem em
`data/curadoria/fontes/capturas/`.

- Medicamentos: o HTML repetia o resumo e gerou 13 chunks. Essa captura foi
  descartada e substituída pelo PDF original: 10 seções detectadas, somente
  `RESUMO` indexada, 7 chunks, 61–88 tokens.
- Organofosforados: 8 seções detectadas, somente `ABSTRACT` indexada,
  7 chunks, 55–116 tokens.
- Permetrina: a primeira inspeção integral gerou 50 chunks e fallback. Após
  selecionar headings e páginas, foram detectadas 7 seções, 3 indexadas,
  10 chunks, 60–99 tokens e nenhum fallback.

## Manifesto e integridade

- perfil: `experimental`;
- modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`;
- revisão: `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`;
- receita: `1a93e1e7db9a5b5a7766ca11b54162cb74cb76bb4d4c2c02b2dc0d5c4319682b`;
- conjunto de fontes: `9106a62e074b28e0992c2515daba38ac503427c06496dec27c0819f71efb8a07`;
- IDs dos chunks: `5f0325d0b61712e070424f2c41d50e12e190cada1bffa80dbf00b171be4890e5`;
- conteúdo dos chunks: `349b6f10bb1f4a3311d6483149a76e9e317a1e9ebf100f1dc37fee6421413555`;
- hash canônico do manifesto no recibo:
  `dfd5db438e0558b2915a7d83edf69e9f4862ff96c5d1acbfade37aa0163491f9`;
- SHA-256 dos bytes JSON formatados do manifesto:
  `288d05ac8da71e1fcc4304ace7d3451b3667d49aeffc3ddef2041b293fc0cd21`.

`validate_collection_integrity` confirmou contagem 24, IDs e conteúdo.
Os 6 warnings foram deliberados no momento do staging: cada fonte ainda
gerava aviso por não ter aprovação clínica registrada e por estar restrita ao
perfil experimental. A aprovação da ASAVET foi informada depois da criação da
coleção; a coleção histórica não foi alterada retroativamente.

## Encontrabilidade no staging

Foi feita consulta direta à candidata, sem alterar o ponteiro. Resultado:

| Caso | Tópico esperado | Melhor posição do tópico | Melhor score do tópico |
|---|---|---:|---:|
| b19 | `human_medication_poisoning` | não apareceu no top-5 | — |
| b20 | `carbamate_organophosphate_poisoning` | 5 | 0,320158 |
| b21 | `permethrin_toxicosis_cats` | 2 | 0,387049 |

Cobertura observada no top-5: **2/3 (66,7%)**, abaixo da porta de 70%.
Nenhum resultado atingiu o limiar provisório de 0,70. A coleção não deve ser
ativada. Em especial, a fonte de medicamento humano é geral demais e a de
organofosforado não cobre o relato canino de forma suficiente.

## Comandos e resultados reproduzidos

| Comando | Resultado |
|---|---|
| `python3 -m pytest -q scripts/tests` antes das alterações | 160 passaram, 25 falharam porque o Python do sistema não tinha `trafilatura` |
| `.venv/bin/python -m pytest -q scripts/tests/test_capturar_fonte.py scripts/tests/test_mapa_de_assuntos.py` | 50 passaram |
| `.venv/bin/python -m pytest -q scripts/tests` final | 186 passaram |
| `docker compose exec -T backend python -m pytest -q` | 201 passaram; apenas avisos de depreciação |
| `docker compose exec -T backend python -m pip check` | `No broken requirements found` |
| `.venv/bin/python -m compileall -q scripts` | código 0 |
| `docker compose config -q` | código 0 |
| `git diff --check` | código 0 |
| `validate_collection_integrity` | 24 chunks; hashes conferidos |

Uma tentativa de validação chamou `read_manifest`, método inexistente, e
falhou com `AttributeError`. A verificação foi repetida com o método correto,
`load_manifest`, e passou. A falha está registrada para não transformar uma
tentativa malsucedida em resultado positivo.

## Pendências

1. Encontrar fonte mais específica para paracetamol/medicamentos humanos.
2. Encontrar material que cubra organofosforados em cães e sinais observáveis.
3. Encontrar fonte em português, redistribuível, sobre permetrina em gatos.
4. Repetir o staging e a régua após melhorar as fontes; não ativar esta
   candidata com cobertura de 66,7%.

Na execução de 14/09 não houve commit, push, PR, ingestão `curated` ou mudança
da coleção ativa. Em 15/09, os dados e artigos foram publicados no commit
`744d220` e o snapshot do Chroma no commit `02c0fef`, sem ativar a candidata.
