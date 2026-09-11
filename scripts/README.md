# scripts/

Ferramentas que rodam **fora do Docker**, direto na sua máquina: preparação
dos dados e avaliação do sistema. As de avaliação falam com a API pela porta
8000, então o compose precisa estar de pé.

## Ambiente

Python 3.12 no host. As dependências são poucas:

```bash
pip install -r scripts/requirements.txt
```

(`pandas`, `numpy`, `requests`, `pytest`.) Pode ser num ambiente virtual na
raiz do projeto ou no Python do sistema.

**No Windows**, prefixe os comandos com `$env:PYTHONUTF8=1;` no PowerShell (ou
`set PYTHONUTF8=1` no cmd). Sem isso o Python lê os arquivos em codificação
ANSI e os acentos quebram. Os exemplos abaixo omitem o prefixo.

Todos os comandos são executados **da raiz do repositório**.

## Os scripts

### Preparação dos dados

Rodam nesta ordem; cada um lê a saída do anterior. O que cada arquivo gerado
significa está em [`data/README.md`](../data/README.md).

| Script | O que faz | Precisa de |
|---|---|---|
| `clean_datasets.py` | Limpa e normaliza os dois datasets de origem; extrai o vocabulário de sintomas do dataset 2 | — |
| `list_dataset2_symptoms.py` | Imprime os sintomas do dataset 2 para cão e gato | `clean_datasets.py` |
| `create_allowed_symptoms.py` | Grava a lista dos 5 sintomas leves usados na geração sintética | — |
| `data_augmentation_dataset_1_nao_emergencia.py` | Gera as combinações sintéticas de não emergência e as anexa ao dataset limpo | os dois acima |
| `validate_synthetic_no_with_llm.py` | Pede a um modelo local que revise cada linha sintética e rejeite as potencialmente urgentes | Ollama no ar; lê `OLLAMA_HOST` e `LLM_MODEL` do ambiente (padrões: `localhost:11434`, `llama3.2:3b`) |

```bash
python scripts/clean_datasets.py
python scripts/create_allowed_symptoms.py
python scripts/data_augmentation_dataset_1_nao_emergencia.py
python scripts/validate_synthetic_no_with_llm.py
```

Esses arquivos já estão gerados e versionados em `data/processed/`; só
precisa rodar de novo se os dados de origem ou as regras mudarem.

### Avaliação

| Arquivo | O que é |
|---|---|
| `run_evaluation.py` | Roda o conjunto de avaliação contra a API e grava uma rodada |
| `report_evaluation.py` | `report` regera métricas e relatório; `compare` compara duas rodadas com teste estatístico; `cite` promove uma rodada citada por uma evidência |
| `evaluation_metrics.py` | Módulo puro com os cálculos; não se roda diretamente |
| `presets.json` | As configurações nomeadas dos braços de avaliação (`llm_only`, `naive_rag`, `rag_query`, `legacy`) |

O passo a passo completo — subir a API, rodar, comparar, citar — está em
[`data/evaluation/README.md`](../data/evaluation/README.md). O essencial:

```bash
python scripts/run_evaluation.py --preset naive_rag --subset full --name minha_rodada
python scripts/report_evaluation.py compare data/evaluation/runs/<A> data/evaluation/runs/<B>
python scripts/report_evaluation.py cite data/evaluation/runs/<A>
```

### Restaurar um retrato da base vetorial

`restore_base_snapshot.py` devolve ao ChromaDB uma base versionada em
`data/evaluation/cited/`. Existe porque a receita de chunking mudou em 07/09 e
a base de 18 trechos, que sustenta as rodadas citadas até 05/09, **não pode
mais ser gerada a partir do código** ([B-37](../evidencias/backlog.md#b-37)).

É o único script daqui que fala com o banco em vez da API, então roda dentro
do container, com as pastas de fora montadas. O passo a passo está no
[README do retrato](../data/evaluation/cited/base-2026-09-04-18-chunks/README.md).
Sem `--force`, ele recusa escrever sobre uma coleção que já tem conteúdo.

### Benchmark de transcrição de voz (WER)

Mede o WER do Whisper sobre fala sintética (edge-tts, vozes PT-BR), a partir
de `scripts/voice_benchmark/references.csv`. É um limite otimista — áudio
limpo, não um tutor real ([B-13](../evidencias/backlog.md#b-13)).

| Arquivo | O que é |
|---|---|
| `voice_benchmark/references.csv` | 18 relatos de tutor em PT-BR com texto de referência, voz e ritmo |
| `voice_benchmark/audio/*.mp3` | os áudios gerados, versionados |
| `generate_voice_benchmark.py` | `references.csv` → `audio/*.mp3`. Roda uma vez, precisa de rede e de `pip install edge-tts` |
| `run_voice_benchmark.py` | envia os áudios a `POST /voice/`, compara com a referência, grava `data/voice_benchmark/` |
| `wer_metrics.py` | módulo puro de WER/CER; não se roda diretamente |

```bash
docker compose up -d
python scripts/run_voice_benchmark.py
```

## Testes

```bash
python -m pytest scripts/tests -q
```

57 testes, sem API nem modelo — o HTTP fica atrás de um dublê. Dois deles
sustentam a comparabilidade com a medição histórica de 04/05: o **teste
dourado** (as 98 respostas daquele dia reproduzem exatamente os números do
diário) e a **regressão dos relatos** (o texto enviado ao modelo é idêntico
ao de então, linha a linha). Se você mudar como o relato é montado, o segundo
falha de propósito.

## Scripts antigos

`evaluate_accuracy.py` e `evaluate_confusion_matrix.py` produziram a medição
de 04/05 e foram substituídos pelos de avaliação acima. Os arquivos que eles
geraram continuam em `data/evaluation/` como artefato histórico e fixture do
teste dourado.
