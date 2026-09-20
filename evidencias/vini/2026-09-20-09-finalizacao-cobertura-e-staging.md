# Finalização da cobertura real e staging experimental

**Data:** 20/09/2026
**Branch:** `codex/lote-06-dez-lacunas`
**HEAD inicial:** `fb4040d01224ae9bcd93a2d6ba9c0dc7eba54830`

## Resultado

- O mapa contém 61 assuntos: 59 com `fonte_aprovada` e 2 com
  `fonte_encontrada`.
- Não restou protocolo sintético em `backend/data/documents`.
- A ASAVET validou em 20/09/2026 os oito arquivos reais que substituíram os
  últimos protocolos sintéticos.
- Os dois assuntos antes bloqueados por direito de redistribuição receberam
  fontes alternativas em acesso aberto. As fontes antigas com licença incerta
  permanecem apenas como referências e não foram liberadas para ingestão.
- Os dois novos arquivos de acesso aberto ainda aguardam validação da ASAVET do
  arquivo exato e, por isso, permanecem `pending_specialist` e
  `experimental_only`.

## Novas fontes abertas dos dois assuntos restantes

| Assunto | Fonte ingerida | Direito | SHA-256 | Chunks |
|---|---|---|---|---:|
| `gastric_dilatation_volvulus` | Olimpo et al., *Animals* 2025, DOI `10.3390/ani15040579` | CC BY 4.0 | `3b4fd87a3b964e6d7a4989f6407cc81a838cc73386f18b4dc93ca11dde8f2424` | 11 |
| `single_vomiting_or_mild_diarrhea` | Holzmann et al., *Frontiers in Veterinary Science* 2023, DOI `10.3389/fvets.2023.1063080` | CC BY 4.0 | `482a69011e47d209b75bd3d38dc5e0ef7332faf73690edaed0a3c7e2e0a15008` | 12 |

## Coleção experimental final

- Coleção: `veterinary_documents__20260920T134907150949Z__7f927242`
- Perfil: `experimental`
- Ativada: não
- Ponteiro ativo: ausente
- Documentos: 66
- Chunks: 3.481
- Assuntos representados: 61 de 61
- Chunks aprovados por especialista: 3.458
- Chunks pendentes: 23
- `source_set_sha256`: `7f927242d94ef7756dfd973d4977edddd1ccc320821554f8d5d138aee0c60daa`
- `chunk_ids_sha256`: `c3cf64e9cbbb23612a755acdcaa3b4a771dc1a5251401401f9ab12d558f630ba`
- `content_sha256`: `1f6ac800b23921693822ea4ebd7137d91c9ed8e365a6d42f37f9c255dcba5485`
- `manifest_sha256`: `5104a711c1e7a17cfd37ce7c029f941af5552be48731d2e3444452883b5773dd`
- Consenso entre manifesto, recibo e conteúdo real: aprovado.

As cinco coleções intermediárias desta rodada foram removidas após a
validação. Foram preservadas as coleções históricas e a candidata final.

## Recuperação direcionada

Foram consultados quatro casos diretamente na candidata, com diversificação
por documento:

- `b12`, dilatação/torção gástrica: o assunto esperado não apareceu no top 5.
- `b64`, vômito isolado em cão ativo: assunto esperado em 1º.
- `b65`, bola de pelo em gato: assunto esperado não apareceu no top 5.
- `b66`, fezes moles isoladas em cão ativo: assunto esperado em 1º.

Isso demonstra cobertura documental, mas não comprova qualidade suficiente da
recuperação. Em especial, a busca de dilatação/torção gástrica precisa ser
melhorada antes de qualquer ativação. Os números históricos do benchmark
permanecem registrados na evidência 08 e não foram reescritos.

## Comandos e verificações finais

| Verificação | Resultado |
|---|---|
| `python -m pytest scripts/tests -q` | 186 aprovados |
| `pytest -q` no backend | 210 aprovados; 13 avisos de depreciação |
| `pip check` no backend | sem dependências quebradas |
| `python -m compileall -q app tests` | aprovado |
| validação JSON | 282 arquivos válidos |
| validação de sintaxe YAML | 10 arquivos válidos |
| `docker compose config --quiet` | aprovado |
| `git diff --check` | aprovado |
| saúde do backend após compactação | saudável |
| ponteiro ativo | ausente |

## Estado do localhost

Sem `active_collection.json`, o backend resolve a coleção legada
`veterinary_documents`. O fingerprint consultado em 20/09/2026 informou zero
chunks nessa coleção. Assim, o aplicativo local continua conversando com a
LLM, mas não recebe contexto útil desta nova base; a candidata de 3.481 chunks
só foi aberta explicitamente nos testes.

## Pendências antes de produção

1. ASAVET validar os dois novos arquivos exatos de GDV e vômito não complicado.
2. Melhorar e repetir a régua de recuperação, sobretudo `b12` e `b65`.
3. Definir critérios mínimos de promoção e executar uma rodada curated.
4. Validar manifesto, contagem e hashes e somente então ativar a candidata.
5. Rodar avaliação completa de respostas e plano de rollback no ambiente de
   destino.
