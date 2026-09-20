# Substituicao das fontes sinteticas e benchmark da base vetorial

**Data:** 20/09/2026
**Branch:** `codex/lote-06-dez-lacunas`
**HEAD inicial:** `fb4040d01224ae9bcd93a2d6ba9c0dc7eba54830`
**Resultado:** colecao experimental criada somente em staging; nenhuma colecao foi ativada.

## Escopo e salvaguardas

- Os sete assuntos que ainda usavam `synthetic_protocol` foram confirmados e os 14 arquivos antigos (sete PDFs e sete sidecars JSON) foram removidos de `backend/data/documents/`.
- Os sete documentos sinteticos somavam 73 chunks.
- Nenhum texto sintetico foi mantido no diretorio de ingestao.
- As novas fontes foram capturadas sem traducao, resumo ou reescrita do conteudo ingerido.
- O perfil permaneceu `experimental` e `ingestion_scope` permaneceu `experimental_only`.
- O ponteiro `backend/chroma_db/active_collection.json` nao existia antes nem foi criado durante o trabalho.
- A aprovacao ASAVET informada pelo responsavel foi registrada nos documentos que ja existiam antes desta captura. As oito novas capturas continuam `pending_specialist`, pois a aprovacao clinica precisa identificar os arquivos e hashes exatos que foram avaliados.

## Fontes que substituem os sete conteudos sinteticos

| Assunto | Fonte | Ano | Especie | Licenca/direito | SHA-256 da captura | Chunks | Estado clinico |
|---|---|---:|---|---|---|---:|---|
| `chocolate_toxicosis` | Cortinovis e Caloni, *Chocolate Toxicity in Dogs and Cats*, Frontiers, DOI 10.3389/fvets.2016.00026 | 2016 | cao e gato | CC BY 4.0, permitido com atribuicao | `6bb19e877af496167579a562f3f536e4642d27f77d2b38532a8c3cd0e01b1b71` | 24 | pendente |
| `allium_toxicosis` | Cortinovis e Caloni, *Allium Toxicity in Dogs and Cats*, Frontiers, DOI 10.3389/fvets.2016.00026 | 2016 | cao e gato | CC BY 4.0, permitido com atribuicao | `6bb19e877af496167579a562f3f536e4642d27f77d2b38532a8c3cd0e01b1b71` | 20 | pendente |
| `respiratory_distress` | Bittenecker et al., *Respiratory Distress in Dogs and Cats*, Frontiers, DOI 10.3389/fvets.2026.1790755 | 2026 | cao e gato | CC BY 4.0, permitido com atribuicao | `7c7bac93cb436424aa7e6d749044bf3788cd3de8c4f372ab7bccb45337f26a80` | 21 | pendente |
| `seizures` | Munguia et al., *Acute Seizures in Dogs and Cats*, Veterinary Sciences, DOI 10.3390/vetsci11060277 | 2024 | cao e gato | CC BY 4.0, permitido com atribuicao | `60847c73b3139bcd94bcf5e7a1f33555ce5d17b8aeca8435db92c3288b1c0db0` | 31 | pendente |
| `trauma_and_bleeding` | Hall e Drobatz, *Hemorrhage in Dogs and Cats*, Frontiers, DOI 10.3389/fvets.2021.638104 | 2021 | cao e gato | CC BY 4.0, permitido com atribuicao | `4b6b2c2c1157d4e72ab1c6849c6f21c345d0852439ee03f60423720adbcae274` | 14 | pendente |
| `urethral_obstruction` | Taylor, Boysen, Buffington et al., *Feline Lower Urinary Tract Guidelines*, iCatCare/JSFM, DOI 10.1177/1098612X241309176 | 2025 | gato | CC BY-NC 4.0, permitido para uso nao comercial com atribuicao | `2cc8bb64898e983ccc16c749f94e1079fe2f722296e715cc3716a602b9e4d3ab` | 25 | pendente |
| `urethral_obstruction` | Er, Fick e Mays, *Canine Mechanical Urethral Obstruction*, Frontiers, DOI 10.3389/fvets.2023.1200406 | 2023 | cao | CC BY 4.0, permitido com atribuicao | `4fc8ec005be8e7537ac6c261d31bf6b79fe6466d9e19c214bf3599d57dd6ab36` | 35 | pendente |
| `vomiting_and_diarrhea` | Fins, Singleton, Radford et al., *Gastrointestinal Presentations in Dogs and Cats*, Frontiers, DOI 10.3389/fvets.2023.1166114 | 2023 | cao e gato | CC BY 4.0, permitido com atribuicao | `31cd34a71f1441e2b4ea83157e6f1e30307d556da32e7960ac49a5119a19e8d8` | 13 | pendente |

As oito capturas totalizam 183 chunks. Cada uma foi inspecionada individualmente com `ingest_documents --inspect --file`.

### Limites observados na inspecao

- Chocolate e Allium usam secoes exatas do mesmo artigo e ainda incluem alguns paragrafos de tratamento.
- A fonte respiratoria e focada em desconforto respiratorio, mas a secao `Discussion` configurada nao foi encontrada pelo extrator.
- A fonte de trauma e uma tabela clinica tecnica, pouco proxima da linguagem cotidiana de tutores.
- A fonte canina de obstrucao uretral possui detalhes de procedimento e medicamentos.
- A fonte gastrointestinal tambem discute resistencia antimicrobiana, criando ruido para consultas simples.

## Aprovacao ASAVET e documentos recuperados para a ingestao

A declaracao do responsavel de que os documentos anteriores foram validados pela ASAVET foi registrada em 30 fontes preexistentes. Foram atualizados 55 sidecars entre `data/curadoria/fontes/capturas/` e `backend/data/documents/`, sem alterar o escopo experimental.

A auditoria mostrou que 17 assuntos presentes no mapa ainda nao estavam no diretorio efetivamente ingerido. Para 15 deles, os direitos permitiam armazenamento e 18 pares documento/sidecar foram copiados para `backend/data/documents/`. Dois assuntos continuaram fora da colecao:

- `gastric_dilatation_volvulus`: clinicamente aprovado, mas com direito de redistribuicao ainda em revisao.
- `single_vomiting_or_mild_diarrhea`: clinicamente aprovado, mas com direito de redistribuicao ainda em revisao.

O mapa final possui 61 assuntos: 52 com `fonte_aprovada` e 9 com `fonte_encontrada`. A colecao experimental cobre 59 assuntos.

## Colecao experimental final

- Nome: `veterinary_documents__20260920T045641179741Z__885cecf4`
- Perfil: `experimental`
- Documentos: 64
- Chunks: 3458
- Assuntos: 59
- Chunks de fontes aprovadas: 3275
- Chunks das oito novas fontes pendentes: 183
- Especies: cao 2000; gato 512; cao e gato 946
- Hash do conjunto de fontes: `885cecf478dee6567015887c95a712a62b364708a0f43da86b6184be824217b2`
- Hash dos IDs dos chunks: `53dc12dfee2fa1d8072ef9b7bd1921bff57dc0a1e96c255b01f81d592ec5a8cb`
- Hash do conteudo dos chunks: `b51b2e6bff884a524f7b8ef4c3effdb7a14525ba9faad8584c95102f90121553`
- Hash do manifesto: `e36836d6e050d5bae28a8c50856d2454184f3d1ed892eb39ffcb7964c310e4ef`
- Consenso entre manifesto, recibo e colecao real: aprovado
- Ativada: nao
- Ponteiro ativo: ausente
- Avisos de extracao: 116; fallbacks: 152; documento legado marcado como corrompido: 1

## Comparacao de recuperacao

Foi usado o mesmo conjunto de 63 casos, dos quais 61 possuem rotulo suficiente para pontuacao. A comparacao foi direta contra duas colecoes no mesmo Chroma, sem trocar o ponteiro ativo.

| Medida | Antes: 3065 chunks | Depois: 3458 chunks | Diferenca |
|---|---:|---:|---:|
| Acerto no primeiro resultado (P@1) | 10/61 = 16,39% | 12/61 = 19,67% | +2 casos; +3,28 pontos percentuais |
| Posicao media ponderada (MRR) | 0,2484 | 0,2822 | +0,0338; +13,6% relativo |
| Assunto esperado entre os 5 primeiros (Recall@5) | 25/61 = 40,98% | 27/61 = 44,26% | +2 casos; +3,28 pontos percentuais |
| Casos com similaridade >= 0,70 | 1 | 1 | sem mudanca |
| Maior similaridade media | 0,5944 | 0,5974 | +0,0030 |
| Latencia media observada | 0,0484 s | 0,1195 s | +147% |
| Latencia p95 observada | 0,0820 s | 0,1457 s | +77,7% |

O resultado geral melhorou discretamente, principalmente porque 15 assuntos aprovados que estavam fora da pasta de ingestao passaram a participar da busca. Houve 8 casos melhores, 7 piores e 48 sem mudanca. A medicao de tempo nao foi controlada por ordem aleatoria, aquecimento e repeticoes, portanto serve como alerta, nao como benchmark conclusivo de latencia.

### Casos que melhoraram

`b05`, `b10`, `b14`, `b17`, `b18`, `b24`, `b25` e `b26`.

### Casos que pioraram

`b03`, `b04`, `b06`, `b08`, `b31`, `b36` e `b49`.

Entre os sete assuntos substituidos, respiracao (`b03`), convulsao (`b04`), trauma (`b06`) e Allium (`b08`) perderam o assunto esperado do top 5. Chocolate permaneceu em segundo, obstrucao uretral permaneceu em segundo e vomito/diarreia aumentou a similaridade, mas ainda nao entrou no top 5. Por esse motivo, a candidata nao deve ser ativada ainda.

## Testes encontrados nas evidencias do Ryu

O arquivo `backend/app/database/measure_query_techniques.py` compara cinco formas de consulta: busca direta, reescrita, multiplas consultas, fusao e fluxo completo com HyDE. O teste e aplicavel a expansao da base e foi iniciado contra a candidata nova.

No ambiente local, o Ollama produziu aproximadamente 1 token por segundo. A primeira rodada de HyDE demorou varios minutos e nem o primeiro dos nove casos terminou; a execucao foi interrompida sem produzir resultado parcial para evitar uma medicao incompleta apresentada como valida. O benchmark completo e viavel com GPU ou depois de impor limite/timeout de geracao.

O benchmark de transcricao (WER) encontrado nas evidencias do Ryu nao mede a base vetorial. A calibracao da classificacao pode ser repetida no modo RAG somente depois de haver uma colecao candidata aprovada e explicitamente selecionada para o teste.

## Comandos e resultados principais

```text
pytest scripts/tests -q
186 passed

docker compose exec -T backend pytest -q
210 passed

python -m app.database.ingest_documents --profile experimental --stage-only
64 documentos; 3458 chunks; colecao criada sem ativacao

python -m app.database.verify_vector_consensus --collection veterinary_documents__20260920T045641179741Z__885cecf4
consenso aprovado: manifesto, recibo e conteudo real coincidem

rg 'synthetic_protocol' backend/data/documents
0 ocorrencias
```

Os comandos finais de validacao, seus resultados e eventuais limitacoes adicionais tambem estao registrados no JSON pareado desta evidencia.

## Pendencias antes de producao

1. Obter a decisao da ASAVET para os oito novos arquivos, referenciando seus hashes.
2. Resolver os direitos dos dois assuntos bloqueados ou substitui-los por fontes com licenca clara.
3. Melhorar as fontes/recortes ou a recuperacao dos casos que regrediram, principalmente respiracao, convulsao, trauma e Allium.
4. Fixar explicitamente `CHROMA_PATH` em producao. Esta rodada usou `backend/chroma_db`, enquanto o valor padrao do codigo e do `.env.example` aponta para `backend/data/chroma`; o `.env` local atual ja aponta para `./chroma_db`.
5. Revisar o documento legado de insolacao marcado como corrompido e completar sua informacao de direitos.
6. Produzir uma colecao `curated` apenas com fontes clinicamente e juridicamente aprovadas, validar contagem e hashes e repetir a regressao completa.
7. Executar testes de ponta a ponta, carga, seguranca, backup, monitoramento e rollback.
8. Somente depois dessas etapas, ativar explicitamente a colecao aprovada. Esta rodada nao realizou ativacao.

## Validacao final do workspace

- `.venv/bin/python -m pytest scripts/tests -q`: 186 aprovados.
- `docker compose exec -T backend pytest -q`: 210 aprovados; apenas avisos de depreciacao conhecidos.
- `pip check`, dentro e fora do contêiner: nenhuma dependencia quebrada.
- `compileall` de `scripts` e `backend/app`: aprovado.
- Todos os JSON e YAML do projeto: sintaxe valida.
- `docker compose config --quiet`: aprovado.
- `git diff --check`: aprovado.
- `docker compose ps`: backend saudavel; frontend, MongoDB e Ollama em execucao.
- `GET /health/`: `{"status":"ok"}`.

Uma primeira chamada acidental a `pytest` pelo Python global do macOS falhou em
26 testes por ausencia de `trafilatura`. A repeticao pelo `.venv`, que e o
ambiente reproduzivel do projeto, aprovou os 186 testes; portanto essa falha foi
classificada como erro de selecao do ambiente, e nao como regressao do codigo.
