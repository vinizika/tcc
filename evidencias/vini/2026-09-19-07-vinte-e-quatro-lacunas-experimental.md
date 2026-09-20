# Sétimo lote — 24 lacunas em coleção experimental

**Data:** 19/09/2026
**Branch:** `codex/lote-06-dez-lacunas`
**HEAD inicial:** `fb4040d01224ae9bcd93a2d6ba9c0dc7eba54830`
**Estado:** staging concluído; não ativado; aguardando ASAVET

## Resultado

As 24 linhas que estavam como `sem_documento` agora têm uma fonte capturada,
sidecar, hash, licença, dossiê e caso de recuperação. No mapa, elas ficaram
como `fonte_encontrada` e `rascunho`; nos sidecars, como
`pending_specialist` e `experimental_only`. Isso registra cobertura documental
sem declarar aprovação clínica.

O mapa ficou com **zero** linhas `sem_documento`. Isso não significa que o
conteúdo esteja pronto para produção: todas as 24 fontes deste lote ainda
dependem da ASAVET, e várias têm limitações de espécie ou de escopo.

## Fontes e inspeção individual

Cada arquivo foi aberto e lido antes da aceitação, teve seu direito de
redistribuição conferido e foi inspecionado com:

```bash
docker compose exec -T backend python -m app.database.ingest_documents \
  --inspect --file <arquivo>
```

As inspeções não escreveram no ChromaDB.

| Caso | Tópico | Referência | Chunks | Resultado da busca |
|---|---|---|---:|---|
| b40 | `tremors_without_seizure` | R73 · Frontiers 2024 · CC BY | 127 | posição 4 · 0,645 |
| b41 | `normal_estrus` | R74 · Animals 2021 · CC BY | 53 | fora do top 5 · 0,611 |
| b42 | `collapse_and_pale_gums` | R75 · Frontiers 2021 · CC BY | 85 | fora do top 5 · 0,553 |
| b43 | `ocular_emergency` | R76 · Frontiers 2024 · CC BY | 94 | posição 1 · 0,566 |
| b44 | `airway_foreign_body_choking` | R77 · Ciência Animal Brasileira 2010 · CC BY | 33 | fora do top 5 · 0,500 |
| b45 | `snake_and_scorpion_envenomation` | R78 · Toxins 2024 · CC BY | 105 | posição 1 · 0,570 |
| b46 | `tick_borne_disease_anemia` | R79 · Veterinary Sciences 2023 · CC BY | 80 | fora do top 5 · 0,694 |
| b47 | `hypoglycemia_toy_puppy` | R80 · Frontiers 2024 · CC BY | 129 | posição 1 · 0,553 |
| b48 | `vestibular_syndrome_otitis_interna` | R81 · Frontiers 2023 · CC BY | 112 | fora do top 5 · 0,552 |
| b49 | `high_rise_syndrome_cats` | R82 · Animals 2026 · CC BY | 77 | posição 2 · 0,461 |
| b50 | `burns_and_electrical_injury` | R83 · BMC 2024 · CC BY | 47 | posição 1 · 0,543 |
| b51 | `eclampsia` | R84 · IJVSAH 2025 · CC BY-NC-SA | 6 | fora do top 5 · 0,645 |
| b52 | `grape_xylitol_toxicosis` | R85 · Frontiers 2016 · CC BY | 156 | posição 1 · 0,640 |
| b53 | `normal_whelping` | R86 · Frontiers 2023 · CC BY | 235 | fora do top 5 · 0,571 |
| b54 | `insect_sting_local_reaction` | R87 · Animals 2024 · CC BY | 71 | fora do top 5 · 0,539 |
| b55 | `kennel_cough_mild` | R88 · PLOS ONE 2019 · CC BY | 56 | posição 3 · 0,615 |
| b56 | `polyuria_polydipsia_investigate` | R89 · Frontiers 2025 · CC BY | 51 | fora do top 5 · 0,587 |
| b57 | `otitis_externa_mild` | R90 · Microorganisms 2023 · CC BY | 107 | posição 1 · 0,584 |
| b58 | `minor_wound` | R91 · Veterinary Sciences 2026 · CC BY | 76 | fora do top 5 · 0,593 |
| b59 | `periodontal_disease_mild` | R92 · Antibiotics 2022 · CC BY | 73 | fora do top 5 · 0,596 |
| b60 | `slow_growing_lump` | R93 · Cells 2022 · CC BY | 131 | posição 5 · 0,575 |
| b61 | `exertional_panting_mild` | R94 · Frontiers 2018 · CC BY | 87 | posição 3 · 0,563 |
| b62 | `rabies_exposure_wild_animal_bite` | R95 · Viruses 2024 · CC BY | 43 | posição 1 · 0,551 |
| b63 | `ticks_found_no_signs` | R96 · Veterinary Sciences 2024 · CC BY | 182 | posição 2 · 0,575 |

Os 24 recortes somam **2.216 chunks**. O detalhamento de autoria, URL, DOI,
licença, espécie e limitação está nos sidecars e nos dossiês em
`data/curadoria/fontes/`.

## Ressalvas de conteúdo

- R75 já havia sido rejeitada em 16/09 por não traduzir diretamente a fala do
  tutor. Foi preservada agora somente como candidata experimental e essa
  mudança está registrada no dossiê; a ASAVET deve decidir.
- R78 é europeia e não substitui casuística brasileira de escorpionismo ou
  araneísmo.
- R80 cobre neonatos, não toda a faixa de filhotes toy descrita no mapa.
- R82 inclui apenas gatos traumatizados já em choque.
- R83 cobre eletrocussão canina, não queimaduras térmicas e químicas.
- R86 cobre cadelas, não gatas.
- R87, R90, R92 e R93 são fontes de uma única espécie para linhas mais amplas.
- R96 mostra positividade em cães assintomáticos; não autoriza considerar um
  carrapato encontrado como inofensivo.

Essas ressalvas também aparecem individualmente na mesa
`data/curadoria/fontes/PARA-VALIDAR.md`.

## Staging

Comando:

```bash
docker compose exec -T backend python -m app.database.ingest_documents \
  --profile experimental --stage-only
```

Resultado:

- coleção: `veterinary_documents__20260919T223447338940Z__2b248783`;
- perfil: `experimental`;
- documentos: 45;
- chunks: 3.065;
- novos chunks pendentes: 2.216;
- hash do conjunto de fontes:
  `2b248783b00c421c75d4341254fc9f8a8f29278ecd0f101f582c3444d9acc022`;
- hash dos ids:
  `99fd25eeb23136cc811953ad8f4bfff6ec11f58342062b6f9044d71c6995ccfe`;
- hash do conteúdo:
  `e62964ac779e3981bf4b0c331795f1e3be41af795dee2544c473764325254a3f`;
- hash do manifesto:
  `d9f2121137d2b905f5ad2ce04c2e8e98719ada06ccf02a021afba73ed020aa75`;
- consenso entre coleção, manifesto, fingerprint e recibo: aprovado;
- `activated: false`;
- ponteiro ativo antes e depois: ausente (`null`).

Não foram executados `--activate`, ingestão `curated` ou alteração manual do
ponteiro.

## Recuperação

A busca foi executada diretamente contra a coleção de staging por abertura
estrita do nome versionado, sem criar ou alterar ponteiro ativo, usando o mesmo
`RetrievalClient` do backend.

- 13/24 tópicos apareceram no top 5;
- 7/24 apareceram em primeiro lugar;
- 0/24 atingiram o corte provisório de 0,70.

O acervo documental aumentou, mas a recuperação não está pronta para produção.
Os principais candidatos a ajuste são os 11 tópicos ausentes do top 5 e os
recortes muito extensos de parto normal, carrapatos sem sinais e toxicidade por
uva/xilitol. A coleção não deve ser ativada.

## Comandos e verificações

| Comando / verificação | Resultado |
|---|---|
| `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| `docker compose exec -T backend pytest -q` | 210 aprovados |
| `.venv/bin/python -m pip check` | nenhuma dependência quebrada |
| `.venv/bin/python -m compileall -q backend/app scripts` | aprovado |
| validação JSON | 244 arquivos válidos, incluindo esta evidência |
| validação YAML genérico | workflow válido |
| `docker compose config --quiet` | aprovado |
| Compose com `docker-compose.gpu.yml` | aprovado |
| `GET /health/` | `{"status":"ok"}` |
| consenso de artefatos | aprovado |
| `git diff --check` | aprovado após remover linhas excedentes |

## Pendências antes do PR

1. A ASAVET precisa revisar as 24 fontes e registrar `sim`, `não` ou `com
   ressalva` na mesa de validação.
2. Depois da resposta, atualizar sidecars, mapa e staging, preservando os
   rejeitados apenas na área de capturas quando necessário.
3. Ajustar recuperação e repetir a régua; nenhum caso passou de 0,70.
4. Revisar o diff completo com o usuário antes de commit, push e PR.
