# Benchmark SBERT / LangChain — 02/10/2026

Produto-base: commit `454bdcf95b1fd3d2ae92a1c3c8862cb47aab7489`.
Protocolo em [protocolo.md](protocolo.md), insumos congelados e hashes em
[inputs.json](inputs.json), execução em [benchmark.py](benchmark.py).
Resultados por chamada: `bge/queries.jsonl` e `minilm/queries.jsonl`.
Cada linha inclui conjunto, caso, repetição, braço, tempo, 50 tópicos/IDs/notas
e hash das mensagens. `metadata.json` por modelo registra recursos e versões.
Agregados reconstruídos por `summarize.py` em `summary.json`.
`paired-quality.json` registra ganhos/perdas no top 3; `token-lengths.json`
registra tokens por relato (gerado por `token_lengths.py` após as medições).
`environment.json` lista Python e pacotes, `manifest.json` fixa o código-base
e `checksums.json` permite conferir a integridade dos artefatos.

## Reprodução

Ambiente utilizado: Docker Desktop Linux aarch64, oito CPUs visíveis,
4.106.604.544 bytes de RAM da VM; quatro threads Torch e uma interop.
Backend, frontend, Mongo e Ollama continuaram ligados; não houve carga de
usuários gerada durante o teste. Não é servidor dedicado nem teste concorrente.
Modelos executados sequencialmente, MiniLM primeiro, após download separado.
Carga mede cache local, não download nem importação inicial das bibliotecas.

Criar um venv separado dentro do backend e instalar apenas nele:

```sh
docker compose exec -T backend python -m venv --system-site-packages /tmp/vetia-embedding-langchain-bench
docker compose exec -T backend /tmp/vetia-embedding-langchain-bench/bin/pip install langchain-core==1.6.6 langchain-chroma==1.1.0
docker compose cp evidencias/vini/2026-10-02-sbert-langchain backend:/tmp/vetia-comparison
```

As revisões dos modelos de `inputs.json` precisam existir no cache HF.
Para cada modelo, usar diretório de saída NOVO, pois o runner cria a coleção:

```sh
docker compose exec -T -e PYTHONPATH=/app backend /tmp/vetia-embedding-langchain-bench/bin/python /tmp/vetia-comparison/benchmark.py /tmp/vetia-comparison/inputs.json minilm /tmp/new-minilm
docker compose exec -T -e PYTHONPATH=/app backend /tmp/vetia-embedding-langchain-bench/bin/python /tmp/vetia-comparison/benchmark.py /tmp/vetia-comparison/inputs.json bge /tmp/new-bge
```

Copiar apenas `queries.jsonl` e `metadata.json` de cada diretório de saída
para uma nova pasta de evidências e executar `summarize.py`. Não sobrescrever
os resultados desta rodada. Os índices Chroma descartáveis não são versionados.

## Decisões de implementação e limites

- Ambos os modelos usam SentenceTransformer.encode, sem normalização explícita,
  como o adaptador atual do Chroma. Não há treinamento ou ajuste em gabaritos.
- Índice cosseno novo por modelo; acesso direto e LangChain compartilham esse
  mesmo índice e embedder. A classe adaptadora só conecta as duas interfaces.
- Busca nativa chama RetrievalClient real. LangChain usa Chroma real e dois
  RunnableLambda para busca/conversão e montagem das mensagens. Metadados são
  convertidos para RetrievedDocument antes do mesmo build_triage_messages.
- Retornam 50 candidatos e montam contexto com os três primeiros. Configuração
  efetiva registrada: vector, context_min_score=0, sem reescrita/HyDE/CoT.
  O montador conserva seu teto de caracteres; hit@3 avalia o ranking, não a
  presença integral de todo o texto das três fichas no prompt.
- Logger de recuperação desativado e tracing desligado nos dois braços.
  Nenhum texto de teste foi enviado a um LLM remoto. Download de pesos é separado.
- Não usamos LangGraph, agentes ou uma chain pronta que mudasse o prompt; isto
  mede uma integração equivalente, não todas as arquiteturas LangChain possíveis.
- RSS é pico do processo inteiro, com ambos os caminhos importados; não isola
  memória do framework. Bytes de vetores são payload float32 teórico, não tamanho
  total do banco. Carga/indexação têm uma execução por modelo, sem intervalo.
  A ordem entre modelos não foi aleatorizada, e o host não foi isolado de outros
  processos. Os braços direto/LangChain alternaram a ordem em cada par.
- Três repetições medem variação temporal; qualidade tem 251 casos, não 753
  amostras independentes. Gabaritos existentes não substituem validação veterinária.
- O warning de tokens aparece ao contar fichas sem truncamento; encode efetivo
  aplica o teto nativo normalmente. Avisos de depreciação do adaptador/dimensão
  não interromperam o teste. Não atribuir causalidade exclusiva ao truncamento:
  pesos, arquitetura e objetivo de treinamento também diferem.
- O arquivo oficial completo tem hash registrado por rastreabilidade, mas apenas
  split dev foi incluído nos insumos de teste. Nenhum caso split teste ou prova2.

Documentação primária: [Sentence Transformers](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html),
[modelos multilíngues](https://www.sbert.net/examples/sentence_transformer/training/multilingual/README.html),
[integrações de embeddings LangChain](https://docs.langchain.com/oss/python/integrations/embeddings),
[Chroma no LangChain](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma)
e [otimização de inferência](https://www.sbert.net/docs/sentence_transformer/usage/efficiency.html).
Documentação consultada em 02/10/2026; as versões efetivamente testadas estão nos metadados.
