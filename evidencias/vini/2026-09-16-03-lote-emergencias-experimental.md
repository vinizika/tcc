# Terceiro lote experimental — emergências

**Data local:** 16/09/2026  
**Branch:** `codex/lote-03-emergencias`  
**HEAD inicial:** `c77bcf711f8e5376cf9b1f33346125c36669612a`  
**Base inicial:** topo do lote 2; depois atualizada por fast-forward para a
`main` no merge `6f852ba8624964417c7c48a8ce073f9577063057`

## Escopo e garantias

O lote trabalhou somente nos tópicos `fading_neonate`,
`acute_hindlimb_paralysis` e `anaphylaxis_facial_swelling`, todos confirmados
como `sem_documento` antes da pesquisa. Em 16/09/2026, o responsável informou
que a ASAVET — Primeiro Grupo de Anestesia e Veterinaria Universitaria do
Brasil aprovou coletivamente as quatro capturas. As fichas passaram para
`approved_by_specialist`, sem registrar revisor individual ou CRMV, e
permanecem `experimental_only`.

Não houve ingestão `curated`, ativação, rollback ou mudança do ponteiro ativo.
O ponteiro `chroma_db/active_collection.json` não existia antes nem depois do
staging. A coleção-base usada pelo backend permaneceu com zero chunks.

## Fontes aceitas e direitos

| Tópico | Fonte | Idioma / espécie | Direito | Recorte literal | SHA-256 | Inspeção |
|---|---|---|---|---|---|---|
| `fading_neonate` | Pereira et al., Animals 2024, DOI `10.3390/ani14233417` | en · cão e gato | CC BY 4.0 | tríade neonatal e papel do tutor | `6ec82e32eaba49122030888892daef854252b7dcae394c9dd40fef53d3e60782` | 5 seções; 49 chunks; 52–96 tokens; 1 fallback |
| `acute_hindlimb_paralysis` | Guillaumin, JFMS 2024, DOI `10.1177/1098612X241257878` | en · gato | CC BY-NC 4.0 | `Introduction` e `Clinical presentation` | `724453ba336b20390ef226b12949ace7290625c940e35420f5a941c8e5d8f494` | 2 seções; 11 chunks; 46–122 tokens; 1 fallback |
| `acute_hindlimb_paralysis` | Ripplinger et al., PVB 2017, DOI `10.1590/S0100-736X2017000900012` | pt · cão | CC BY-NC 4.0 | `RESUMO` | `41c0284eb7c0b1aa7b41e5262af190796e45492762d2c347aaf879c7ddbb0eb4` | 1 seção; 7 chunks; 66–96 tokens; sem fallback |
| `anaphylaxis_facial_swelling` | Nagy et al., Toxins 2024, DOI `10.3390/toxins16010048` | en · cão e gato | CC BY 4.0 | `Bees and Wasps` | `2120b88919a5fbfd1cfd2e1261c6350deae5cc16b8b93a1ac4ffe7500f7e27a5` | 1 seção; 32 chunks; 48–127 tokens; sem fallback |

Os textos armazenados são trechos literais das publicações, sem tradução,
resumo clínico ou reescrita. Para os artigos disponíveis no PMC, a distribuição
de arquivos mudou em agosto de 2026 e os links de PDF bloquearam o capturador.
Os recortes foram extraídos do XML integral oficial disponibilizado para
reutilização e receberam hash próprio. O capturador normal foi usado para
validar os PDFs antes do recorte; essa limitação operacional está registrada
porque o script atual ainda não aceita JATS XML.

## Fontes rejeitadas ou bloqueadas

- Turner et al., Frontiers 2022, anafilaxia canina após picada, CC BY 4.0:
  rejeitada após inspeção do PDF. Produziu 225 chunks, títulos falsos vindos
  de tabelas e conteúdo laboratorial fora do objetivo. A captura foi removida.
- Os PDFs completos de Animals e Toxins produziram, respectivamente, 143 e
  44 chunks com conteúdo fora do recorte. Foram substituídos por extrações
  literais das seções e removidos.
- VCA e University of Illinois sobre síndrome do neonato: referência apenas;
  não havia licença inequívoca para redistribuir o texto integral.
- *Basic triage in dogs and cats: Part II* e VCA sobre anafilaxia: referência
  apenas, por direito de redistribuição não confirmado.
- Não foi encontrada fonte em português, diretamente aplicável e com licença
  inequívoca para neonato ou anafilaxia neste lote.

## Manifesto e integridade da candidata final

- coleção: `veterinary_documents__20260916T035025760102Z__43f4e229`;
- perfil: `experimental`;
- documentos: 4;
- chunks: 99;
- modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`;
- revisão: `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`;
- receita: `1a93e1e7db9a5b5a7766ca11b54162cb74cb76bb4d4c2c02b2dc0d5c4319682b`;
- conjunto de fontes: `43f4e229de8ccfb8b3ecc73f247ec1b8d4f716ae7eda611438e2a5e8618d3dba`;
- IDs dos chunks: `f58264d16755034b56c0f86023979e1886bf7175f76ba018fa787141e0f0a0ed`;
- conteúdo: `5613734846377472b4ab4de9edea6822d719c959fa63f0b8ddcc393282b8b4bf`;
- manifesto canônico: `cd514c9cd903b30918c20bfd3feb01ce3877cadda1c21ae6596848414ac8231b`;
- bytes do manifesto: `919a24d8f7d0c52afe7659adef6d406e64391b79e3b854215cc8debc1e5a9eea`;
- bytes do recibo: `4c95bb096713271bcd6d327e2c03d692535652736bb1ac4c214feb69dce2abe3`.

`validate_collection_integrity` confirmou contagem, IDs e conteúdo. Os 6
warnings são esperados: quatro documentos restritos ao perfil experimental e
dois fallbacks lexicais. Os 99 chunks registram
`validation_status=approved_by_specialist`. Não houve fragmento marcado como
corrompido.

Uma candidata intermediária de 92 chunks foi criada para diagnosticar a falta
de cobertura canina no caso b17. Ela nunca foi ativada e foi excluída antes da
entrega, junto com manifesto, recibo e segmento órfão. Só a candidata final
permanece no repositório.

A primeira candidata completa, com 99 chunks e sidecars ainda marcados como
`pending_specialist`, também foi descartada sem ativação depois que a aprovação
da ASAVET foi informada. A candidata final acima foi reconstruída para que o
manifesto, os hashes e os metadados dos chunks reflitam o estado aprovado.

## Encontrabilidade no staging

As consultas foram feitas diretamente à candidata final, sem resolver ou
alterar a coleção ativa.

| Caso | Tópico esperado | Melhor posição | Melhor score | Passou 0,70? |
|---|---|---:|---:|---|
| b14 | `fading_neonate` | 1 | 0,617052 | não |
| b16 | `anaphylaxis_facial_swelling` | 1 | 0,504331 | não |
| b17 | `acute_hindlimb_paralysis` | 1 | 0,553069 | não |

Os três tópicos foram encontrados no primeiro resultado e ocuparam todo o
top-5 de seus casos. Nenhum atingiu o limiar provisório de 0,70. Isso sugere
que os documentos estão relacionados corretamente, mas ainda há diferença de
idioma e de linguagem entre os relatos dos tutores e os artigos acadêmicos.
A candidata não deve ser ativada.

## Comandos e resultados reproduzidos

| Comando | Resultado |
|---|---|
| `.venv/bin/python -m pytest scripts/tests -q` antes das alterações | 186 passaram |
| `.venv/bin/python -m pytest scripts/tests -q` após cada grupo e no final | 186 passaram em cada execução |
| quatro inspeções finais com `ingest_documents --inspect --file` | 49, 11, 7 e 32 chunks; nenhuma escrita no Chroma |
| `docker compose exec -T backend python -m pytest -q` | 203 passaram; 13 avisos de depreciação |
| `docker compose exec -T backend python -m pip check` | `No broken requirements found` |
| `.venv/bin/python -m compileall -q scripts backend/app` | código 0 |
| `docker compose config -q` | código 0 |
| validação JSON/YAML/CSV | 69 JSON, 3 YAML e 2 CSV válidos |
| `git diff --check` | código 0 |
| `validate_collection_integrity` | 99 chunks; hashes conferidos |

## Pendências

1. Encontrar fonte em português com licença clara para neonato e anafilaxia.
2. Cobrir outras causas de paralisia aguda, especialmente doença de disco.
3. Melhorar a recuperação dos três casos e repetir a régua; os scores ainda
   estão abaixo de 0,70.
4. Não ativar a candidata atual nem executar ingestão `curated` antes da
   revisão dos resultados e de uma decisão separada sobre o escopo.

Não houve commit, push ou abertura de PR nesta etapa. O diff foi preparado
para revisão do usuário.
