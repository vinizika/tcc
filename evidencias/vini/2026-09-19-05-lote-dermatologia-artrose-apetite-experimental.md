# Lote 5 — dermatologia, artrose e apetite em staging experimental

**Data:** 19/09/2026  
**Branch:** `codex/lote-05-mapa-assuntos`  
**HEAD inicial:** `382c8203b1efc5752aeecdb993318ff28841ad78`  
**Estado:** fontes validadas pela ASAVET e staging refeito; sem commit, publicação ou ativação

## Atualização e leitura do trabalho do Ryu

A branch nasceu da `origin/main` já sincronizada. Foram lidos integralmente os
oito registros de `evidencias/ryu`, além das instruções dos três agentes e da
documentação da ingestão.

Os achados que orientaram este lote foram:

- HyDE não melhorou a recuperação e piorou um dos lotes; continua desabilitado
  na configuração atual.
- Reescrita e multi-query foram corrigidas para fusão e remoção de duplicatas,
  mas ainda precisam ser medidas por caso.
- Transformar a consulta não compensa um documento genérico: os novos recortes
  devem ser diretamente ligados à linguagem do tutor e ao tópico do mapa.
- Os snapshots experimentais anteriores estão em `backend/chroma_db`; no
  contêiner atual, `CHROMA_PATH=./chroma_db` resolve para `/app/chroma_db`.
- A medição limpa de latência do item B-07 continua pendente no trilho do Ryu.

## Estado inicial e escolha dos tópicos

Antes das alterações, o mapa tinha 61 tópicos: 37 `sem_documento`, 14 com
`fonte_aprovada`, 3 com `fonte_encontrada` e 7 sintéticos. Foram escolhidos três
tópicos de prioridade A e etapa 1:

- `osteoarthritis_stiffness`;
- `flea_dermatitis_pruritus`;
- `reduced_appetite_no_other_signs`.

O caso existente `b09` foi ligado à dermatite, e `b28` e `b29` foram escritos
antes da pesquisa. A linha de base tinha **186 testes de scripts aprovados**.

Após a validação da ASAVET, o mapa permanece com 61 tópicos: 34
`sem_documento`, 16 com `fonte_aprovada`, 4 com `fonte_encontrada` e 7
sintéticos. Ainda existem quatro
tópicos da etapa 1 sem documento.

## Fontes capturadas e direitos

Cinco artigos revisados por pares foram lidos, tiveram a licença conferida e
foram capturados literalmente, sem tradução, resumo ou reescrita. Todos foram
aprovados pela **ASAVET — Primeiro Grupo de Anestesia e Veterinaria
Universitaria do Brasil** em 19/09/2026. Permanecem `experimental_only`:
aprovação clínica não equivale à ativação da coleção.

| Tópico | Fonte | Espécie | Idioma | Direito | SHA-256 | Destino |
|---|---|---|---|---|---|---|
| `osteoarthritis_stiffness` | Mosley et al., Frontiers 2022, DOI `10.3389/fvets.2022.830098` | cão | EN | CC BY 4.0 | `7d19fc33d0827be1d5e98a90039bb7b6679f29bebd5bdaf99a8276c9818285fa` | staging |
| `osteoarthritis_stiffness` | Matsubara et al., ABMVZ 2019, DOI `10.1590/1678-4162-9892` | cão | PT | CC BY | `33158f748b3cb4568fbe5fb64bf119639946e9f93f6f0afd80f681eec705f18f` | somente captura |
| `flea_dermatitis_pruritus` | Diesel, Veterinary Sciences 2017, DOI `10.3390/vetsci4020025` | gato | EN | CC BY 4.0 | `8388d1f1950363bc581b7acb3e3ebde5d68145a63e2fcd7e9594ad150af9c8b4` | staging |
| `flea_dermatitis_pruritus` | Vasconcelos et al., PVB 2017, DOI `10.1590/S0100-736X2017000300008` | cão | PT | CC BY 4.0 | `3a51cdd56446e388ca5b94c99284d80c51f9269a21cf308fe888d5d2011f534b` | staging |
| `reduced_appetite_no_other_signs` | Carvalho et al., Animals 2025, DOI `10.3390/ani15203054` | gato | EN | CC BY 4.0 | `429e4227a3595cd9f67b259064b1e6f64731c915477230b425bbd19186150a4b` | somente captura |

URLs, autores, instituições, ano, espécie, recortes e bases de licença estão
nos sidecars e nos dossiês em `data/curadoria/fontes/`.

### Fontes lidas e não armazenadas

| Fonte | URL | Decisão |
|---|---|---|
| ISFM 2022, gato inapetente hospitalizado | `https://doi.org/10.1177/1098612X221106353` | O repositório do RVC registra CC BY, mas a população hospitalizada não sustenta o prazo do tópico domiciliar |
| NC State Veterinary Hospital, *Picky Eaters* | `https://hospital.cvm.ncsu.edu/services/small-animals/nutrition/picky-eaters/` | Conteúdo útil, porém todos os direitos reservados; referência apenas |
| Tufts, *Reduced or Altered Appetite* | `https://vet.tufts.edu/foster-hospital-small-animals/specialty-services/cardiology/heartsmart/heart-disease-symptoms/reduced-or-altered-appetitie` | Sem licença aberta identificada e limitado a cardiopatas; referência apenas |

## Inspeção individual

Cada captura foi inspecionada com:

```bash
docker compose exec -T backend python -m app.database.ingest_documents \
  --inspect --file <arquivo>
```

| Fonte | Chunks | Faixa de tokens | Fallback | Decisão |
|---|---:|---:|---:|---|
| Frontiers, artrose canina | 13 | 55–94 | 0 | selecionada; sinais iniciais diretamente úteis |
| ABMVZ, artrose canina | 51 | 46–121 | 1 | fora do staging; mistura sinais, métodos e fármacos |
| Veterinary Sciences, DAPP felina | 23 | 60–96 | 0 | selecionada; quatro chunks finais iniciam a seção seguinte sobre insetos |
| PVB, dermatite alérgica canina | 17 | 36–109 | 1 | selecionada |
| Animals, inapetência felina | 20 | 50–99 | 0 | fora do staging; foco predominante em mirtazapina e sem apoio ao prazo de triagem |

## Staging experimental

Somente os três recortes adequados foram copiados para
`backend/data/documents`. A ingestão usou o perfil `experimental` e criou uma
coleção candidata sem ativá-la:

- Coleção: `veterinary_documents__20260919T172103063002Z__70a774a4`
- Documentos: 11
- Chunks: 312
- Novos chunks: 53 — 40 de dermatite por pulgas e 13 de artrose
- `source_set_sha256`: `70a774a4c13f9a2cc5d5de16494ece17cbdfa7ef1071e9d5b9a5944ae6638533`
- `ids_sha256`: `b1246ebbb969dfd617daccd66fb8ca7576d8ef7930ddcce37893253941a196be`
- `content_sha256`: `c25966b64a58202e22a333f1bc40d653326e308c094fdd34cd429f41756b93af`
- `manifest_sha256`: `711421fc81cbb379f107caa95f96dfb1626a899a5e32a5935c69025f66693e93`
- Receita: `1a93e1e7db9a5b5a7766ca11b54162cb74cb76bb4d4c2c02b2dc0d5c4319682b`
- Modelo/tokenizer fixado na revisão `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`
- Ativada: **não**
- Ponteiro ativo antes e depois: **ausente**

A candidata também contém oito documentos que já estavam na pasta do backend.
Por isso, o manifesto registra 32 fallbacks, 22 avisos e um documento legado
marcado como corrompido; os 53 chunks novos estão
`approved_by_specialist`. A coleção anterior à validação,
`veterinary_documents__20260919T154008538116Z__a45ef7e8`, foi preservada como
registro de auditoria, continua inativa e foi substituída pela candidata acima.

## Recuperação dos casos

A candidata anterior à validação foi consultada diretamente pelo nome. O corpo,
o título, as seções, os ids e os embeddings não mudaram na nova candidata;
somente os metadados de validação e seus hashes mudaram. Por isso, a medição de
recuperação não foi repetida. O ponteiro ativo não foi criado ou alterado.

| Caso | Resultado sem transformação | Resultado com transformações |
|---|---|---|
| `b09`, dermatite por pulgas | tópico correto em 1º, score `0,628713` | correto em todos os cinco lugares; máximo `0,768328` |
| `b28`, rigidez de artrose | tópico correto em 3º, score `0,419550` | reescrita, multi-query e HyDE perderam o tópico; heatstroke dominou o resultado |
| `b29`, apetite reduzido | sem documento esperado, como planejado; máximo `0,478829` de outro tópico | a reescrita inventou ingestão de material não digerível e retornou obstrução urinária com `0,703904` |

O resultado de dermatite passou 0,70 após transformação, mas artrose ainda não
é encontrável de forma confiável e o caso de apetite demonstrou distorção da
consulta. A coleção não satisfaz uma condição segura de ativação.

## Testes e verificações

| Momento | Comando | Resultado |
|---|---|---|
| Linha de base | `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| Após curadoria | `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| Após validação ASAVET | `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| Backend | `docker compose exec -T backend pytest tests -q` | 210 aprovados |
| Dependências | `.venv/bin/pip check` | nenhuma dependência quebrada |
| Compilação | `.venv/bin/python -m compileall -q backend/app scripts` | aprovada |
| JSON | `python3 -m json.tool` em todos os arquivos | válido |
| YAML | `Ruby Psych.safe_load` nos três YAML do repositório | válido |
| Docker | `docker compose config --quiet` e `docker compose ps` | configuração válida; quatro serviços em execução; backend saudável |
| Saúde | `GET http://localhost:8000/health/` | HTTP 200, `{"status":"ok"}` |
| Integridade | `ChromaDBClient.validate_collection_integrity(...)` | 312 chunks; hashes de ids e conteúdo válidos |
| Diff | `git diff --check` | aprovado |

`jq` não está instalado; o JSON foi validado com o parser padrão do Python. A
validação YAML usou o Psych incluído no Ruby local.

## Limitações e pendências

- As cinco fontes foram aprovadas pela ASAVET em 19/09/2026.
- Artrose cobre cães, não gatos, e o recorte em português ficou fora do staging.
- O artigo felino de dermatite contém quatro chunks da seção seguinte na mesma
  página; isso deve ser avaliado antes de qualquer promoção.
- O tópico de apetite ainda não possui documento adequado para ingestão.
- A reescrita de `b29` e as transformações de `b28` introduziram erros que
  precisam ser corrigidos no trilho de consulta antes de ativação.
- A divergência histórica entre caminhos do Chroma deve continuar explícita;
  este lote usou o caminho real do contêiner `/app/chroma_db`.
- Próximo passo: melhoria do recorte de artrose e correção/guarda das
  transformações de consulta.

Não houve commit, push, PR, ativação ou mudança na coleção ativa.
