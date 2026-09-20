# Sexto lote — dez lacunas em coleção experimental

**Data:** 19/09/2026
**Branch:** `codex/lote-06-dez-lacunas`
**HEAD inicial:** `fb4040d01224ae9bcd93a2d6ba9c0dc7eba54830`
**Estado:** staging concluído; não ativado; fontes validadas pela ASAVET

## Escopo

Foram escolhidos dez dos 34 tópicos que estavam como `sem_documento`:

1. `gastrointestinal_foreign_body`
2. `cat_bite_abscess`
3. `congestive_heart_failure`
4. `diabetic_ketoacidosis`
5. `distemper_neurological`
6. `dystocia`
7. `feline_aortic_thromboembolism`
8. `leptospirosis_acute`
9. `lily_toxicosis_cats`
10. `toad_bufotoxin_poisoning`

Os casos `b30`–`b39` foram escritos antes da pesquisa. O mapa ficou com
24 linhas `sem_documento`, uma redução de dez. Após a revisão do lote, a
ASAVET validou as dez fontes em 19/09/2026. As linhas passaram para
`fonte_aprovada` e `validada:asavet:19/09`.

## Teste anterior às alterações

| Comando | Resultado |
|---|---|
| `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| `docker compose exec -T backend pytest -q` | 210 aprovados |

## Fontes selecionadas

| Tópico | Fonte / direito | SHA-256 | Inspeção |
|---|---|---|---|
| Corpo estranho GI | Frontiers 2025, DOI `10.3389/fvets.2025.1562792`, CC BY 4.0 | `8ca9de24e96f8fdb8549f3e0f2f970937e0c86491f0eb9f2eb5f911b16adf518` | 56 chunks, 46–96 tokens |
| Abscesso felino | Frontiers 2025, DOI `10.3389/fvets.2025.1654990`, CC BY 4.0 | `996c364f63c5f28ab8e5cd7edb5ea30c3768a26583be4604e26f3fe2f8b4a4af` | 44 chunks, 40–95 tokens |
| Insuficiência cardíaca | Frontiers 2020, DOI `10.3389/fvets.2019.00513`, CC BY 4.0 | `9fc525f2ebfd6e0ebc9cfe6c932cc8649a21ca4ef06bcf6975dda849daa9d881` | 80 chunks, 52–115 tokens |
| Cetoacidose diabética | ARSHI 2025, DOI `10.29244/avl.9.3.81-82`, CC BY-SA 4.0 | `f5236d534acd52289aae31dcf29c8c650ac85f3dd84c4c814d5d0c9756766002` | 46 chunks, 48–110 tokens |
| Cinomose neurológica | Viruses 2022, DOI `10.3390/v14071520`, CC BY 4.0 | `243b8581f721719db97f8fd95b8db4aa7fc31774f340502fea2ea35ed42f969d` | 16 chunks, 69–93 tokens |
| Distocia | Acta Vet Scand 2025, DOI `10.1186/s13028-025-00805-w`, CC BY 4.0 | `eb4483eefd264440f4a56f9a22a1b80028ce5301cb73eb3c94b73533122fb596` | 68 chunks, 52–96 tokens |
| Tromboembolismo aórtico felino | JFMS 2024, DOI `10.1177/1098612X241257878`, CC BY-NC 4.0 | `1d319d26e1796bf06cce656d727bafa5e9fa2faa06bd73e59f6ac9bba46b836c` | 41 chunks, 40–119 tokens |
| Leptospirose | consenso ACVIM 2023, DOI `10.1111/jvim.16903`, CC BY-NC-ND 4.0 | `6de65211a73cc5a7cb667755526626494b5d967c3df7e3b142bac465250df6eb` | 127 chunks, 39–118 tokens |
| Lírio em gatos | Frontiers 2023, DOI `10.3389/fvets.2023.1195743`, CC BY 4.0 | `b327e3ef0d57f1d858b302999b628910b6c6d8134c5ff7b7832d31ff8cf9298b` | 41 chunks, 48–98 tokens |
| Veneno de sapo | PUBVET 2024, DOI `10.31533/pubvet.v18n06e1609`, CC BY 4.0 | `897ce472dff59a2b540291a4428f4d8df43a995df89d337ff994010a0aac2f0a` | 18 chunks, 61–118 tokens |

Todos os sidecars usam `approved_by_specialist`, registram o veredito da
ASAVET e preservam `ingestion_scope: experimental_only`.

## Fonte rejeitada e ressalvas

- O artigo PVB de 2009 sobre bufotoxina foi preservado em
  `data/curadoria/fontes/capturas/`, mas retirado de
  `backend/data/documents/`: a inspeção indexava essencialmente metodologia.
- A fonte de `cat_bite_abscess` cobre abscesso felino intra-abdominal, não
  mordida. Ela é um candidato fraco, explicitamente marcado para substituição
  ou validação com ressalva.
- A cópia do artigo de tromboembolismo veio de um espelho, porque o servidor
  oficial recusou o download automatizado. DOI e licença foram conferidos.
- O consenso de leptospirose usa CC BY-NC-ND; o PDF original foi preservado
  sem alteração e o uso experimental é não comercial.
- Não foi localizado um segundo documento armazenável, com licença clara,
  para cada tópico no tempo deste lote. As referências bloqueadas ou sem
  direito claro não foram copiadas.

## Staging

Comando:

```bash
docker compose exec -T backend python -m app.database.ingest_documents \
  --profile experimental --stage-only
```

Resultado:

- coleção final após validação:
  `veterinary_documents__20260919T213831239313Z__4953d00c`;
- documentos: 21 (dez novos e onze experimentais já existentes);
- chunks: 849;
- hash do conjunto de fontes:
  `4953d00cba14e9d7da338c6c0b790a02cff310340aa13f0048f0bfa77db95465`;
- hash dos ids:
  `9ebdae42d47cc31da0464cbf9b33544922b63aabba44e844be2797da12020e25`;
- hash do conteúdo:
  `be9ba546aca3decf92318ec4d1752c90f37f1b3edcc66f1c978f0628f3afb36b`;
- hash do manifesto:
  `b8c9fd7b15c4ced107393287d27565a503e5f51cfd15080462a971ddec349347`;
- status de validação: 590 chunks `approved_by_specialist`, incluindo os
  537 chunks das dez fontes deste lote;
- `activated: false`;
- `active_pointer: null`.

Não foi executado `--activate`, ingestão `curated` ou alteração manual do
ponteiro. A ausência de ponteiro ativo já existia antes desta rodada.

## Busca direta na candidata

A avaliação usou o mesmo `RetrievalClient` do backend, apontado somente
dentro de um processo temporário para a candidata anterior à anotação da
aprovação. A candidata final preservou os mesmos PDFs, recortes, 849 chunks e
o mesmo hash de IDs; apenas os metadados de validação e seus hashes mudaram.
Não houve alteração da coleção ativa. A medição completa com reescrita,
Multi-Query e HyDE foi interrompida porque o Ollama local demorava cerca de
um minuto por etapa; os processos temporários foram encerrados.

| Caso | Esperado | Posição no top 5 | Melhor nota |
|---|---|---:|---:|
| b30 | corpo estranho GI | não apareceu | 0,601 |
| b31 | abscesso felino | 3 | 0,565 |
| b32 | insuficiência cardíaca | 1 | 0,709 |
| b33 | cetoacidose diabética | 5 | 0,604 |
| b34 | cinomose neurológica | 4 | 0,662 |
| b35 | distocia | não apareceu | 0,514 |
| b36 | tromboembolismo aórtico | 3 | 0,557 |
| b37 | leptospirose | 3 | 0,582 |
| b38 | lírio | 1 | 0,626 |
| b39 | veneno de sapo | 3 | 0,638 |

Resumo: 8/10 tópicos encontráveis no top 5, 2/10 em primeiro lugar e somente
o caso b32 ultrapassou o corte de 0,70. O backend devolveu os cinco mais
próximos nos demais casos pelo fallback já existente. A candidata não deve
ser ativada.

## Verificações finais

| Verificação | Resultado |
|---|---|
| scripts | 186 aprovados |
| backend | 210 aprovados |
| `pip check` | nenhuma dependência quebrada |
| `compileall` | aprovado |
| JSON | aprovado |
| YAML | aprovado |
| `docker compose config --quiet` | aprovado |
| saúde do backend | saudável |
| `git diff --check` | aprovado |

## Pendências

1. Substituir a fonte de abscesso por uma que trate especificamente ferida de
   mordida e tenha direito de redistribuição claro.
2. Melhorar corpo estranho e distocia, que não apareceram no top 5.
3. Reavaliar recortes extensos, especialmente leptospirose e insuficiência
   cardíaca, antes de qualquer ativação.
4. Rodar a comparação completa de estratégias quando o Ollama estiver mais
   rápido.
