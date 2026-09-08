# Endurecimento do upload de voz (B-32)

**Data:** 08/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 2

## O que foi feito

A rota `POST /voice/` foi reescrita para tratar o arquivo enviado pelo tutor
como entrada não confiável:

- **Nome gerado no servidor.** O arquivo é gravado em
  `uploads/<uuid4>.<ext>`. O nome do cliente nunca entra no caminho de
  escrita; dele só se lê `Path(...).suffix`, que é inofensivo mesmo com
  componentes de diretório (`Path("../../x.wav").suffix == ".wav"`).
- **Validação de tipo.** Uma allowlist de extensões de áudio
  (`.wav`, `.ogg`, `.mp3`, `.m4a`, `.webm`, `.flac`, …). A extensão vem do
  sufixo do nome ou, na falta dele, do `content-type` declarado. O que não
  casa é recusado com **415** antes de qualquer escrita.
- **Limite de tamanho.** A gravação é feita em blocos de 1 MB, abortando com
  **413** ao passar de `MAX_AUDIO_UPLOAD_MB` (nova setting, padrão 25). Áudio
  vazio é recusado com **422**.
- **Remoção garantida.** O arquivo temporário é apagado num `finally`, tanto
  em sucesso quanto em erro (incluindo falha da transcrição).

Novos arquivos: `backend/app/exceptions/voice_exception.py` (três exceções
`BaseAppException`) e `backend/tests/test_api_voice.py` (7 testes).
`VoiceService` não mudou — continua recebendo um `Path`.

## Por quê

O Vinicius (A) registrou em [B-32](../backlog.md#b-32), na auditoria cruzada,
que a rota concatenava `audio.filename` direto em `uploads/` e abria esse
caminho para escrita: sem nome do servidor, sem limite de tamanho/tipo, sem
remoção depois. Um nome com `../` podia sobrescrever arquivos fora de
`uploads/` sob as permissões do backend — e, como o Compose monta
`./backend:/app`, a sobrescrita alcançaria o próprio repositório. Uploads
grandes ou repetidos encheriam o disco. Era o item de prioridade Alta mais
isolado do meu trilho e não dependia da régua do trilho A.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Manter a gravação em disco (nome do servidor) em vez de transcrever de um buffer em memória | `VoiceService.transcribe(Path)` é o contrato atual e o `faster-whisper` já espera um caminho; trocar para buffer seria uma segunda mudança na mesma rodada. Fica anotado como opção para a consolidação do Whisper ([B-13](../backlog.md#b-13)) |
| Teto como setting (`MAX_AUDIO_UPLOAD_MB`, padrão 25) | Mesmo desenho das outras configs do projeto; 25 MB cobrem com folga um relato real e limitam o abuso |
| Allowlist de extensões como constante no módulo, não em setting | Não é algo que se ajuste por máquina; um `set` em `BaseSettings` ainda complica o parsing por env |
| 415 / 413 / 422 como exceções `BaseAppException` dedicadas | Segue o padrão do time (`RetrievalException` 503, `LLMException` 502, `UnsupportedOptionException` 400) e reaproveita o handler já registrado |
| Testar com dublê de `VoiceService.transcribe` e `UPLOAD_FOLDER` em `tmp_path` | Padrão do `conftest.py` (dublês, sem estado externo); nenhum modelo Whisper é carregado no pytest |

## Resultado esperado

*(escrito antes de rodar)*

Os 92 testes do backend continuam passando e os 7 novos passam. Nenhum
arquivo com o nome do cliente é criado; nenhum arquivo temporário sobra em
`uploads/` após a resposta, mesmo quando o limite é excedido ou a
transcrição falha. O frontend (`voice_client.py` envia
`("audio.wav", bytes, "audio/wav")`) continua compatível sem mudança.

## Resultado obtido

**Confirmado no container.** `docker run --rm -v .../backend://app -w //app
tcc-backend:latest python -m pytest -q` → **99 passaram** (92 anteriores + 7
novos). `tests/test_api_voice.py` isolado: 7/7.

Os 7 testes cobrem:

| Teste | Garante |
|---|---|
| `test_transcreve_e_remove_o_arquivo_temporario` | Caminho feliz: nome sob `uploads/`, sufixo `.wav`, sem o nome do cliente, arquivo removido |
| `test_nome_do_cliente_nunca_entra_no_caminho_de_escrita` | Enviar `../../escrita_indevida.wav` não cria nada fora de `uploads/` |
| `test_extensao_vem_do_tipo_quando_o_nome_nao_ajuda` | Nome `blob` + `audio/ogg` → arquivo `.ogg` |
| `test_audio_acima_do_limite_e_recusado` | 2 MB com teto de 1 MB → 413, sem transcrever, sem sobra |
| `test_arquivo_que_nao_e_audio_e_recusado` | `notas.txt` + `text/plain` → 415, sem transcrever |
| `test_audio_vazio_e_recusado` | Corpo vazio → 422, sem sobra |
| `test_falha_na_transcricao_ainda_remove_o_arquivo` | Erro na transcrição → 500 e arquivo removido mesmo assim |

Critério do backlog atendido: o nome do cliente nunca participa do caminho de
escrita e nenhum arquivo temporário permanece após sucesso ou erro.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/api/voice.py` | reescrita: `_resolve_extension`, `_save_within_limit`, nome `uuid4`, teto de bytes, remoção em `finally` |
| `backend/app/exceptions/voice_exception.py` | **novo** — `UnsupportedAudioException` (415), `AudioTooLargeException` (413), `EmptyAudioException` (422) |
| `backend/app/core/config.py` | nova setting `MAX_AUDIO_UPLOAD_MB` (padrão 25) |
| `backend/tests/test_api_voice.py` | **novo** — 7 testes |
| `.env.example` | documenta `MAX_AUDIO_UPLOAD_MB` |
| `docs/CONTRATOS.md` | linha do `POST /voice/` descreve os limites |
| `README.md` | contagem da suíte do backend 92 → 99 |
| `evidencias/backlog.md`, `evidencias/ryu/*` | B-32 fechado; rodada, README e planejamento |

## Observações

1. `faster-whisper`/PyAV identificam o formato pelo conteúdo, não pela
   extensão — a allowlist serve para recusar cedo o que claramente não é
   áudio, não para garantir decodificação.
2. O frontend não precisou mudar, mas ele tem a URL `http://backend:8000`
   fixa no código ([B-23](../backlog.md#b-23)); rodar a interface fora do
   Compose ainda não alcança a rota.
3. O Whisper continua com três implementações e sem benchmark de WER
   ([B-13](../backlog.md#b-13)) — próximo item do trilho.

## Próximo passo

**B-13**: consolidar as três implementações de Whisper numa só e medir o WER
com 15–20 áudios gravados pelo time. É o número que o artigo cita (~97,5%)
sem que exista medição, e não depende da régua do trilho A.
