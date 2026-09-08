# Whisper único e benchmark de WER (B-13)

**Data:** 08/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 3

> As seções "Decisões" e "Resultado esperado" foram escritas **antes** de
> rodar o benchmark, como manda o padrão destas evidências.

## O que foi feito

Duas coisas, que juntas fecham o [B-13](../backlog.md#b-13).

**1. Uma implementação só de Whisper.** As duas órfãs foram apagadas:

| Removido | O que era |
|---|---|
| `app/ai/whisper/model.py`, `app/ai/whisper/transcriber.py` | `WhisperTranscriber`, modelo `base`, carregado no import; sem importadores |
| `app/models/whisper_model.py`, `app/clients/whisper_client.py` | `WhisperClient`, modelo `base`, carregado no import |
| `app/core/models.py` | instanciava `WhisperClient()` no import |

Sobrou o `VoiceService` (o que a API sempre usou), agora com o tamanho do
modelo em setting — `WHISPER_MODEL_SIZE`, padrão `small` — para ficar
registrado junto de qualquer medição. 3 testes novos em
`backend/tests/test_voice_service.py`.

**2. Benchmark de WER.** Um harness em `scripts/`, no mesmo desenho do runner
de avaliação (fala com a API por HTTP):

| Arquivo | O que é |
|---|---|
| `scripts/voice_benchmark/references.csv` | 18 relatos de tutor em PT-BR, com texto de referência, voz e ritmo |
| `scripts/voice_benchmark/audio/*.mp3` | os áudios, versionados (700 KB no total) |
| `scripts/generate_voice_benchmark.py` | `references.csv` → `audio/`, via edge-tts (roda uma vez, precisa de rede) |
| `scripts/run_voice_benchmark.py` | envia os áudios a `POST /voice/`, compara com a referência, grava `data/voice_benchmark/` |
| `scripts/wer_metrics.py` | módulo puro de WER/CER (Levenshtein por palavra e por caractere), com 9 testes |

## Por quê

O Vinicius (A) registrou o problema no [diagnóstico da divisão](../../docs/divisao-de-trabalho.md)
e ele virou o [B-13](../backlog.md#b-13): três caminhos de código de Whisper,
dois tamanhos de modelo, e ninguém sabia qual rodava — enquanto o artigo cita
~97,5% de acerto na transcrição sem que exista uma medição. Num time de três,
é onde alguém conserta o arquivo errado.

O time **não quis gravar áudios** para o benchmark. A alternativa foi fala
sintética: escrevo os relatos de referência e um TTS os converte em áudio. O
texto de referência é exato — é o que alimentou o TTS.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Manter `VoiceService`, apagar as outras duas | É a única plugada na API; as órfãs carregavam `base` no import, custando memória à toa |
| `WHISPER_MODEL_SIZE` como setting (padrão `small`) | O WER depende do tamanho do modelo; sem isso registrado, o número não é reproduzível |
| TTS: **edge-tts** (vozes neurais PT-BR da Microsoft) | 3 vozes (Francisca, Antônio, Thalita) + variação de ritmo dão alguma variância de "locutor"; multiplataforma; melhor que a voz única do SAPI do Windows |
| Áudios versionados no repo | Medir o WER de novo não depende de rede nem de o TTS ser reproduzível bit a bit |
| WER agregado = Σ erros ÷ Σ palavras de referência | Não a média das taxas por frase — uma frase curta com um erro pesaria igual a uma longa sem nenhum |
| Acentos preservados na normalização | Em português distinguem palavras, e o Whisper os produz; só caixa e pontuação são neutralizadas |
| 18 relatos, com rótulo de emergência/não emergência | Servem também como semente de relatos PT-BR reais, que faltam ao projeto (ver [B-15](../backlog.md#b-15)) — mas isto aqui **não** é o conjunto de avaliação |

## Resultado esperado

*(escrito antes de rodar)*

WER agregado abaixo de 10% — é fala sintética limpa, sem ruído, sem sotaque
forte, sem estresse. Os erros devem se concentrar em ligações de palavras
("há uns"/"a uns"), termos clínicos menos comuns ("inchaço", "ofegante") e
grafias de números. O idioma detectado deve ser `pt` em 100% dos áudios.

**A ressalva que já vale registrar:** este número é um **limite otimista**.
Um tutor real, ao telefone, em pânico, num ambiente com ruído, terá WER
maior. O benchmark serve como linha de partida versionada e como teste de
não-regressão quando o modelo ou o pré-processamento mudarem — não como a
medição de campo que o artigo, no fim, precisa.

## Resultado obtido

### Números

| Métrica | Valor |
|---|---:|
| **WER agregado** | **0,052** (5,2%) |
| CER agregado | 0,018 (1,8%) |
| Áudios | 18 |
| Palavras de referência | 345 |
| Substituições / remoções / inserções | 13 / 3 / 2 |
| Tempo mediano por requisição | 4,5 s |
| Idioma ≠ `pt` | 0 |

Rodada com o modelo `small`, commit `b6f567f`. Relatório completo e previsões
linha a linha em [`data/voice_benchmark/`](../../data/voice_benchmark/report.md).

### O que o Whisper errou

- **`b04`** — "fez xixi no chão" virou "fechou no chão". É o único erro que
  apaga um sinal clínico: micção durante a convulsão é informação de triagem.
- **`b05`** — "minha gata" virou "Unyagata" na abertura (voz do Antônio);
  "mas" virou "mais". Foi o pior item, WER 0,19.
- **`b11`** — "inchaço" → "chasso", "há uns dois dias" → "a uns dois dias".
- **`b16`** — "abelha" → "belha", "inchando" → "enchendo".
- **`b17`** — "ofegante" → "o fegante" (palavra partida).
- **`b13`** — "dez minutos" → "10 minutos": conta como substituição porque a
  normalização não unifica número por extenso e dígito. Limitação conhecida
  do `wer_metrics.py`, 1 ocorrência.

Nove dos 18 áudios tiveram WER zero. Os erros restantes são de grafia
(minúscula/ligação) ou de termos clínicos menos frequentes — nenhum inverteu
o sentido do relato, com a ressalva do `b04`.

### Comparação com o artigo

O artigo cita ~97,5% de acerto na transcrição. Aqui deu **94,8%** de acerto
por palavra (100% − WER), com o modelo `small` sobre fala sintética. Como
condição real é pior que sintética, a expectativa realista para o texto do
TCC é **abaixo** dos 97,5% — o número citado provavelmente vem de inglês ou
de um modelo maior, e isso precisa ser dito.

### Testes

| Suíte | Antes | Depois |
|---|---:|---:|
| Backend (container) | 99 | **102** |
| Scripts (host) | 48 | **57** |

`docker run ... tcc-backend:latest python -m pytest -q` → 102 passaram.
`python -m pytest scripts/tests -q` → 57 passaram.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/ai/`, `backend/app/models/whisper_model.py`, `backend/app/clients/whisper_client.py`, `backend/app/core/models.py` | **apagados** — Whispers órfãos |
| `backend/app/services/voice_service.py` | única implementação; tamanho do modelo via setting; docstring explicando a consolidação |
| `backend/app/core/config.py` | nova setting `WHISPER_MODEL_SIZE` |
| `backend/tests/test_voice_service.py` | **novo** — 3 testes (tamanho das settings, carga única, junção de segmentos) |
| `scripts/wer_metrics.py` | **novo** — módulo puro de WER/CER |
| `scripts/generate_voice_benchmark.py`, `scripts/run_voice_benchmark.py` | **novos** — geração e medição |
| `scripts/voice_benchmark/references.csv` + `audio/*.mp3` | **novos** — 18 relatos e áudios versionados |
| `scripts/tests/test_wer_metrics.py` | **novo** — 9 testes |
| `data/voice_benchmark/` | **novo** — `report.md`, `predictions.csv`, `summary.json` da rodada inaugural |
| `scripts/requirements.txt`, `scripts/README.md`, `README.md` | edge-tts opcional documentado; contagens de teste; seção do benchmark |
| `evidencias/backlog.md`, `evidencias/ryu/*` | B-13 fechado, B-18 em andamento; rodada, README e planejamento |

## Observações

1. **O número é otimista de propósito.** Fala sintética limpa. A segunda
   rodada, com áudio real gravado pelo time, fica registrada como pendência
   no [B-13](../backlog.md#b-13); até lá, 5,2% é a linha de base.
2. **As vozes não são iguais.** O item pior (`b05`) foi da voz do Antônio; a
   Thalita e a Francisca erraram menos. Uma amostra maior diria se é padrão.
3. **`wer_metrics.py` não unifica número por extenso e dígito.** Custou 1
   erro nesta rodada; se virar recorrente, entra no módulo com teste.
4. **Os 18 relatos são PT-BR e rotulados.** Não são o conjunto de avaliação
   (que é em inglês, [B-15](../backlog.md#b-15)), mas podem servir de semente
   quando o time montar o conjunto de relatos leigos reais.

## Próximo passo

**B-10**: em `_build_queries` (`chat_pipeline.py`), montar `[reescrita] +
variações` sem duplicatas quando o multi-query estiver ligado — hoje a
reescrita não vai ao índice nesse caso, e os dois braços da ablação diferem
em natureza, não em grau. É o ponto único já preparado pelo B2
(`docs/CONTRATOS.md`, item 1) e não depende da régua do trilho A.
