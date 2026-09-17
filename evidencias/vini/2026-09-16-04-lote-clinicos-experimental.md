# Lote 4 — seis capturas clínicas em staging experimental

**Data:** 16/09/2026
**Branch:** `codex/lote-04-pares-clinicos`
**HEAD inicial:** `6932dd8a74dd4e102c9590ff744deb2d35683f72`
**Estado:** publicado no PR [#8](https://github.com/vinizika/tcc/pull/8), pronto para merge; coleção não ativada

## Escopo e estado inicial

Foram escolhidos seis tópicos de prioridade A e etapa 1 que estavam
`sem_documento`: `dietary_indiscretion_mild`,
`mild_upper_respiratory_signs`, `mild_lameness`,
`inappropriate_urination_or_cystitis`, `collapse_and_pale_gums` e
`mild_conjunctivitis`.

Antes de pesquisar, os casos existentes `b05`, `b10`, `b11` e `b18` foram
associados aos tópicos correspondentes e os casos `b25`, `b26` e `b27` foram
escritos. A linha de base dos scripts tinha **186 testes aprovados**.

## Resultado da pesquisa

Seis fontes revisadas por pares e abertas foram capturadas. Todas foram
aprovadas pela ASAVET em 17/09/2026 e continuam `experimental_only`.

| Tópico | Fonte | Espécie | Recorte | Chunks | SHA-256 |
|---|---|---|---|---:|---|
| `dietary_indiscretion_mild` | PLOS One 2025, DOI `10.1371/journal.pone.0324203` | cão | extração literal de `Results` e `Conclusions` | 7 | `ce97800e37515ea85569cf6dc33d63532ae6691a2dc3397285906e1146cbbdbc` |
| `mild_upper_respiratory_signs` | Veterinary Sciences 2024, DOI `10.3390/vetsci11060232` | gato | `Introduction` | 35 | `6cf203b171a0a924df188870f85a876876050d63c6e9f476d53989c1e0757e45` |
| `mild_lameness` | BMC Veterinary Research 2018, DOI `10.1186/s12917-018-1484-2` | cão | `Abstract` | 11 | `a57615f1c26e03687c1fd5b344628110a180ebfa6376c5c26fd92ed221f0b4e4` |
| `inappropriate_urination_or_cystitis` | Frontiers 2022, DOI `10.3389/fvets.2022.900847` | gato | `Introduction` | 18 | `e6f245d441f57c413d1f91b5a61beda0f78afc816d67ac4e327331971e7b3665` |
| `mild_conjunctivitis` | BMC Veterinary Research 2023, DOI `10.1186/s12917-022-03561-5` | cão | `Abstract` | 17 | `a2fda2fdfefbbfa2e66b98725bb1bb8b18ff26c8fd0169875d778382cc7abed8` |
| `mild_conjunctivitis` | Open Veterinary Journal 2024, DOI `10.5455/OVJ.2024.v14.i12.13` | gato | extração literal de `Introduction` | 3 | `2bda92787ba47fac3d6a84dcc07af30a161c7162893f2288c9e0e59b4b9cce0f` |

Nenhuma fonte em português com licença inequívoca para redistribuição foi
localizada dentro deste ciclo. Páginas institucionais sem licença clara foram
mantidas apenas como referências, sem cópia integral.

### Fonte rejeitada

O artigo de Hall e Drobatz sobre choque hemorrágico, DOI
`10.3389/fvets.2021.638104`, foi aberto e inspecionado, mas não conecta
diretamente os dois sinais leigos do tópico `collapse_and_pale_gums`. A captura
foi retirada do repositório e o tópico continua `sem_documento`.

## Inspeção individual

Comando aplicado a cada arquivo, inclusive à nova captura felina:

```bash
docker compose exec -T backend python -m app.database.ingest_documents \
  --inspect --file <arquivo>
```

O primeiro texto de diarreia gerava 309 chunks e foi substituído por uma
extração literal de 7 chunks. Os PDFs foram limitados às seções acima. A
extração de cistite e conjuntivite registrou 2 fallbacks cada; os demais
recortes não registraram fallback. A extração felina produziu 3 chunks de
76–86 tokens sem fallback. Métodos, referências e tratamento foram excluídos.

## Staging experimental

Comando:

```bash
docker compose exec -T backend python -m app.database.ingest_documents \
  --profile experimental --stage-only
```

- Coleção final: `veterinary_documents__20260917T033016639440Z__1c0fa630`
- Perfil: `experimental`
- Documentos totais: 14
- Chunks totais: 350
- Chunks dos seis documentos novos: 91
- `source_set_sha256`: `1c0fa63051388b4cf961f8e883f79f9bee01d1daf1d73a9a314fb274316b9f2a`
- `ids_sha256`: `7496cacfed1824a4e6a7c1e82302873ff1393ac2e154e3944e57618a29e83261`
- `content_sha256`: `14cd275df01ba8d4e4a75ef09935af2584384a1ee375cd72615a29ffdccc97e9`
- `manifest_sha256`: `99bf5271fc9bad2533ce1dafd7b6471bf62ef1eb02c57e9ca2cd74922844b900`
- Chunks aprovados pela ASAVET: 91
- Ativada: **não**
- Ponteiro ativo antes e depois: **ausente**

A coleção contém também os oito documentos já presentes em
`backend/data/documents`; as seis fontes do lote foram copiadas apenas durante
a inspeção/staging e removidas dessa pasta depois.

Os stagings anteriores deste lote foram substituídos e removidos. A coleção
final acima reflete as seis fichas aprovadas.

## Correção da busca

A consulta ao Chroma agora pede até `TOP_K × 10` candidatos internamente e
prioriza uma ocorrência por arquivo de origem antes de preencher vagas com
trechos repetidos. A resposta pública continua limitada ao mesmo `TOP_K` e
mantém os mesmos campos. Isso evita que cinco pedaços do artigo de obstrução
ocupem toda a lista e escondam a fonte de cistite, que estava na posição 8.

## Recuperação dos casos do lote

A candidata foi consultada diretamente pelo nome, sem criar ou mudar ponteiro.

| Caso | Esperado | Melhor posição | Nota máxima |
|---|---|---:|---:|
| `b05` | `mild_upper_respiratory_signs` | 1 | 0,5569 |
| `b10` | `mild_lameness` | 1 | 0,6049 |
| `b11` | `mild_conjunctivitis` | 1 | 0,5116 |
| `b18` | `mild_upper_respiratory_signs` | 1 | 0,6063 |
| `b25` | `dietary_indiscretion_mild` | 1 | 0,5526 |
| `b26` | `inappropriate_urination_or_cystitis` | 2 | 0,5369, de obstrução uretral; tópico esperado 0,4514 |
| `b27` | `collapse_and_pale_gums` | sem documento | 0,4997, de outro tópico |

Os cinco tópicos novos que possuem documento ficaram encontráveis no caso
esperado: **100%**. A cobertura passou a porta de 70%, mas nenhum caso chegou
ao corte provisório de score 0,70. Por esse motivo, a candidata não foi
ativada.

## Testes e verificações

| Momento | Comando | Resultado |
|---|---|---|
| Linha de base | `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| Após casos da régua | `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| Após curadoria | `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| Após correção da busca | `docker compose exec -T backend pytest tests -q` | 205 aprovados |
| Verificação final dos scripts | `.venv/bin/python -m pytest scripts/tests -q` | 186 aprovados |
| Teste direto da candidata | `RetrievalClient.retrieve` nos casos `b05`, `b10`, `b11`, `b18`, `b25`, `b26`, `b27` | 5/5 tópicos documentados encontráveis |
| Dependências | `.venv/bin/pip check` | nenhuma dependência quebrada |
| Compilação | `.venv/bin/python -m compileall -q backend/app scripts` | aprovado |
| Formatação do diff | `git diff --check` | aprovado |
| JSON | `python3 -m json.tool <arquivo>` | evidência, sidecar, manifesto e recibo válidos |
| Docker | `docker compose config --quiet` | configuração válida |
| Integridade do staging | `ChromaDBClient.validate_collection_integrity(...)` | 350 chunks, hashes válidos, ponteiro ausente |

A tentativa inicial de executar o teste do backend diretamente no ambiente
local foi interrompida antes da coleta porque o `.env` local contém
`DEBUG=release`, valor que não é booleano. A suíte foi então executada no
contêiner configurado do backend, onde os 205 testes passaram. O utilitário
`jq` não está instalado; a validação JSON foi repetida com o parser padrão do
Python.

## Limitações e pendências

- As seis fontes têm aprovação clínica da ASAVET registrada.
- Os recortes cobrem uma espécie por tópico; o mapa de quatro tópicos declara
  ambos.
- A fonte respiratória é concentrada em abrigos; claudicação é experimental;
  conjuntivite é apenas alérgica; diarreia não prova segurança de ingestão
  desconhecida; cistite não reduz a cautela diante de esforço urinário.
- `b11` e `b26` agora encontram o tópico esperado, mas continuam abaixo de
  0,70; esse limiar precisa ser calibrado com a régua, não alterado à mão.
- `collapse_and_pale_gums` continua sem documento armazenável adequado.
- Próxima decisão: calibrar a régua de score com casos representativos, sem
  alterar resultados manualmente. Esta coleção não foi ativada.

## Publicação

- Branch: `codex/lote-04-pares-clinicos`
- Commit inicial do lote: `eca77b2`
- Pull request: [#8 — Amplia curadoria clínica e diversifica recuperação](https://github.com/vinizika/tcc/pull/8)
- Base: `main`
