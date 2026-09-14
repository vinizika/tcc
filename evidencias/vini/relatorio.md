# Relatório de recuperação — endurecimento da ingestão vetorial do projeto `vinizika/tcc`

> Documento destinado à reconstrução do trabalho perdido após o descarte do ambiente local.
>
> **Data de referência do trabalho:** 13/09/2026
> **Repositório:** `vinizika/tcc`
> **Commit-base utilizado:** `c3f09ec5c6a5608e2039a0651a0dec437d19479b`
> **Branch local que havia sido criada:** `codex/harden-vector-ingestion`
> **Estado da publicação:** a branch nunca chegou ao GitHub e nenhum PR foi aberto.

## 1. Aviso importante sobre a fidelidade deste relatório

Este relatório foi reconstruído a partir do histórico técnico preservado da sessão. Ele contém:

* A lista dos arquivos alterados e criados.
* A finalidade de cada alteração.
* As regras de negócio implementadas.
* A arquitetura definida para a ingestão vetorial.
* Os testes executados.
* As métricas exatas registradas.
* Os problemas encontrados e corrigidos durante a implementação.
* As pendências existentes quando o ambiente foi perdido.
* Um plano operacional para outra IA reconstruir tudo.
* Pseudocódigo dos elementos centrais.

Entretanto, o conteúdo literal completo dos arquivos não está mais disponível. Portanto:

* Os hashes, métricas e resultados registrados são reais, obtidos na execução perdida.
* Os nomes e caminhos dos arquivos são os registrados na sessão.
* O comportamento descrito corresponde ao que foi implementado.
* Os pseudocódigos abaixo não devem ser tratados como cópia literal do código perdido.
* Outra IA deverá reconstruir o código e executar novamente todos os testes.
* Os resultados antigos não devem ser apresentados como evidência de uma reconstrução nova até que sejam reproduzidos.

---

# 2. Objetivo geral do trabalho

O trabalho transformava a ingestão existente — que era relativamente simples, destrutiva e pouco auditável — em um processo:

* Reprodutível.
* Versionado.
* Auditável.
* Seguro contra substituição acidental da base ativa.
* Capaz de distinguir documentos curados, experimentais e legados.
* Capaz de gerar métricas e evidências.
* Compatível com comparação antes/depois da recuperação vetorial.
* Preparado para ingestão de novos documentos reais.
* Protegido contra documentos sem curadoria suficiente.
* Com modelo de embeddings e tokenizer fixados por revisão.
* Com testes unitários, de integração e uma execução real temporária com ChromaDB.

A principal mudança conceitual foi:

> Uma ingestão nova não deveria apagar ou substituir imediatamente a coleção ativa. Ela deveria gerar uma coleção candidata versionada, validá-la e somente depois ativá-la explicitamente.

---

# 3. Estado do repositório remoto

A última verificação realizada diretamente no GitHub confirmou:

* Não existe a branch remota `codex/harden-vector-ingestion`.
* Não existe PR relacionado ao trabalho.
* O commit mais recente no remoto permaneceu:

```text
c3f09ec5c6a5608e2039a0651a0dec437d19479b
```

Título:

```text
Monta persistencia de tutor/pet (Supabase) e historico de conversa (MongoDB)
```

Portanto, nenhuma das alterações descritas neste documento está garantidamente presente no GitHub.

---

# 4. Resumo do que havia sido implementado

## 4.1. Modelo de embeddings reprodutível

Foi criada uma configuração centralizada do modelo de embeddings.

Modelo/revisão registrada:

```text
revision = e8f8c211226b894fcb81acc59f3b34ba3efd5f42
```

O objetivo era impedir que duas máquinas instalassem revisões diferentes do mesmo modelo e produzissem embeddings incompatíveis.

A configuração deveria centralizar:

* Nome do modelo.
* Revisão/commit do modelo.
* Dimensão do embedding.
* Comprimento máximo do tokenizer.
* Identidade da receita de embedding.
* Dados utilizados na composição do texto vetorizado.

O tokenizer também passou a ser carregado com a mesma revisão fixada.

---

## 4.2. Separação entre conteúdo bruto e conteúdo enriquecido

A estrutura `DocumentChunk` ganhou o campo:

```python
body: str
```

Antes, havia risco de o mesmo campo ser utilizado simultaneamente como:

* Texto puro extraído do documento.
* Texto enriquecido com título e seção.
* Conteúdo apresentado ao modelo.
* Conteúdo persistido nos metadados.

A lógica implementada passou a separar:

* `body`: corpo limpo do trecho.
* Texto de embedding: título + seção + corpo.
* Conteúdo retornado pelo retrieval/prompt: corpo limpo.
* Metadados: título, seção, fonte, documento, página e demais informações.

Receita conceitual de embedding:

```python
embedding_text = "\n\n".join(
    part for part in [
        document_title,
        section_title,
        chunk_body,
    ]
    if part
)
```

Isso melhora a recuperação porque o título e a seção fornecem contexto sem contaminar o corpo exibido ao usuário ou enviado ao prompt.

---

## 4.3. Normalização textual

Foi ampliada a normalização utilizada para comparar títulos e seções.

Ela deveria:

* Converter para minúsculas.
* Remover espaços excedentes.
* Remover indentação.
* Normalizar Unicode.
* Remover marcas de acentuação para comparações estruturais.
* Evitar divergências como:

```text
Diagnóstico
diagnostico
 DIAGNÓSTICO
```

Pseudocódigo:

```python
import re
import unicodedata

def normalized_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(
        char for char in normalized
        if not unicodedata.combining(char)
    )
    collapsed = re.sub(r"\s+", " ", without_accents)
    return collapsed.strip().lower()
```

Essa normalização deveria ser usada nas regras de:

* `include_sections`
* `exclude_sections`
* identificação de headings
* validação de sidecar
* comparação de seções capturadas

Também foi suprimido o warning repetitivo do tokenizer para textos longos, pois o particionamento controlado já limitava os chunks.

---

# 5. Perfis de ingestão

Foram definidos três perfis distintos.

## 5.1. `curated`

Destinado à base de conhecimento que poderia ser candidata a produção.

Requisitos rígidos:

* Documento com sidecar válido.
* Status de curadoria aprovado.
* Campos humanos obrigatórios preenchidos.
* Espécies explicitamente declaradas.
* Fonte e URL identificadas.
* Integridade verificada.
* Documento não marcado como corrompido.
* Documento não marcado como experimental.
* Seções relevantes explicitamente controladas quando necessário.
* Nenhum fallback silencioso que mascarasse ausência de estrutura.
* Zero documento inelegível admitido.

Se nenhum documento estivesse completamente aprovado, a ingestão deveria falhar antes de criar qualquer banco ou coleção.

Resultado real observado:

```text
0 documentos elegíveis
exit code 2
nenhum diretório Chroma criado
```

Isso foi considerado comportamento correto: a ausência de curadoria não poderia gerar uma “base curada” vazia ou enganosa.

---

## 5.2. `experimental`

Destinado a experimentos, diagnósticos e análise de documentos ainda não aprovados.

Esse perfil aceitava:

* Documentos `experimental_only`.
* Documentos com warnings.
* Fallback de seção.
* Documento corrompido, desde que contabilizado e explicitamente sinalizado.
* Documentos com curadoria pendente.

O perfil não deveria ser ativado automaticamente como coleção oficial.

Resultado real:

```text
8 documentos
259 chunks
31 chunks/documentos em fallback conforme contabilização
1 documento corrompido sinalizado
63 warnings
```

Também foi detectada forte concentração temática:

```text
186 de 259 chunks relacionados a heatstroke
71,8% da coleção
```

Essa concentração deveria aparecer no relatório e impedir que a base fosse interpretada como equilibrada.

---

## 5.3. `legacy_rechunk`

Destinado a reprocessar os documentos legados com a nova receita de chunking, mantendo a rastreabilidade.

Esse perfil permitia comparar:

* Receita antiga.
* Receita nova.
* Distribuição de tokens.
* Quantidade de chunks.
* Resultado da régua de recuperação.

Resultado real:

```text
7 documentos
73 chunks
0 fallback
0 documentos corrompidos
56 warnings
```

Esse perfil não significava que os documentos estavam clinicamente aprovados; apenas permitia reconstruir o corpus legado com a nova pipeline.

---

# 6. Versionamento e ativação atômica no ChromaDB

## 6.1. Problema anterior

A ingestão anterior utilizava uma lógica equivalente a:

```text
apagar coleção atual
criar coleção
inserir documentos
```

Isso produzia riscos importantes:

* Uma falha no meio da ingestão podia deixar a base vazia.
* Um documento corrompido podia substituir uma coleção funcional.
* Não havia rollback.
* Não havia manifestação clara de qual coleção estava ativa.
* Não havia rastreabilidade da receita usada.
* Comparações antes/depois podiam perder o estado anterior.

---

## 6.2. Nova estratégia

Cada execução deveria criar uma coleção versionada/staged.

Exemplo conceitual:

```text
documents__20260913T123456Z__a1b2c3d4
```

Fluxo:

```text
documentos
    ↓
validação
    ↓
chunking
    ↓
coleção candidata versionada
    ↓
manifesto
    ↓
verificação de integridade
    ↓
ativação explícita
    ↓
ponteiro da coleção ativa
```

A coleção anterior deveria permanecer intacta até a ativação bem-sucedida da nova.

---

## 6.3. Ponteiro de coleção ativa

Foi implementado um mecanismo persistente indicando a coleção ativa.

O ponteiro deveria armazenar pelo menos:

```json
{
  "collection_name": "documents__20260913T123456Z__a1b2c3d4",
  "activated_at": "2026-09-13T...",
  "manifest_sha256": "...",
  "profile": "experimental"
}
```

O cliente de retrieval deveria:

1. Ler o ponteiro.
2. Localizar exatamente a coleção indicada.
3. Falhar explicitamente se a coleção não existir.
4. Nunca criar silenciosamente uma coleção vazia.

---

## 6.4. Bug encontrado e corrigido: ponteiro obsoleto

Durante os testes reais com ChromaDB, foi detectado um problema crítico:

* Se o ponteiro ativo mencionasse uma coleção inexistente, uma chamada semelhante a `get_or_create_collection()` poderia criar uma coleção nova vazia com aquele nome.
* Isso mascararia a corrupção do estado.
* A aplicação pareceria funcional, mas faria buscas em uma base vazia.

A correção implementada foi:

* Quando existe um ponteiro ativo, usar operação estrita de obtenção.
* Não usar `get_or_create_collection`.
* Se a coleção apontada não existir, lançar erro claro.
* Permitir criação apenas durante uma ingestão/staging deliberada.

Pseudocódigo:

```python
def get_active_collection():
    pointer = load_active_pointer()

    if pointer:
        collection_name = pointer["collection_name"]
        try:
            return chroma_client.get_collection(collection_name)
        except Exception as exc:
            raise ActiveCollectionUnavailableError(
                f"A coleção ativa {collection_name!r} não existe"
            ) from exc

    return get_legacy_collection_if_allowed()
```

Foi criado um teste real de integração para garantir que um ponteiro obsoleto não produzisse uma coleção vazia.

---

## 6.5. Compatibilidade com a coleção legada

Foi mantida uma exceção controlada para a coleção antiga:

* Uma coleção legada sem manifesto poderia ser lida para compatibilidade.
* Coleções novas/versionadas sem manifesto deveriam ser rejeitadas.
* A exceção deveria ser restrita ao nome-base legado.
* Não deveria se transformar em fallback geral.

Lógica:

```python
if is_versioned_collection(name) and not manifest_exists(name):
    raise MissingManifestError(name)

if name == legacy_base_collection and not manifest_exists(name):
    allow_legacy_read()
```

---

## 6.6. Rollback

O sistema passou a permitir:

* Listar coleções versionadas.
* Consultar seus manifestos.
* Ativar uma coleção candidata.
* Reativar uma coleção anterior.
* Impedir a exclusão da coleção ativa.

A operação de rollback deveria apenas trocar o ponteiro depois de validar a coleção e seu manifesto.

---

# 7. Manifesto de ingestão

Cada coleção candidata deveria possuir um manifesto contendo informações suficientes para reproduzir e auditar a ingestão.

Campos conceituais:

```json
{
  "schema_version": 1,
  "collection_name": "...",
  "created_at": "...",
  "profile": "experimental",
  "embedding": {
    "model": "...",
    "revision": "e8f8c211226b894fcb81acc59f3b34ba3efd5f42",
    "max_sequence_length": 128
  },
  "chunking": {
    "recipe_sha256": "...",
    "minimum_tokens": 48,
    "maximum_tokens": 128,
    "overlap": "..."
  },
  "sources": {
    "document_count": 8,
    "source_set_sha256": "..."
  },
  "chunks": {
    "count": 259,
    "ids_sha256": "...",
    "content_sha256": "..."
  },
  "quality": {
    "warning_count": 63,
    "fallback_count": 31,
    "corrupt_document_count": 1
  }
}
```

Antes de ativar uma coleção, o sistema deveria validar:

* Nome da coleção.
* Existência do manifesto.
* Hash do manifesto.
* Quantidade real de chunks.
* Hash dos IDs.
* Hash do conteúdo.
* Compatibilidade da receita.
* Compatibilidade do modelo/revisão.
* Perfil declarado.
* Ausência de corrupção não autorizada.

---

# 8. Fingerprints da base

O serviço de fingerprints foi ampliado para representar o estado real da coleção.

O fingerprint passou a considerar:

* Modelo de embeddings.
* Revisão exata do modelo.
* Receita de chunking.
* Conjunto de fontes.
* Identificadores de chunks.
* Conteúdo dos chunks.
* Quantidade por tópico.
* Quantidade por espécie.
* Quantidade por fonte.
* Quantidade por status de curadoria.
* Quantidade total de documentos.
* Quantidade total de chunks.

Estrutura conceitual:

```json
{
  "embedding_model": "...",
  "embedding_revision": "...",
  "chunk_recipe_sha256": "...",
  "source_set_sha256": "...",
  "chunk_ids_sha256": "...",
  "chunk_content_sha256": "...",
  "counts": {
    "documents": 8,
    "chunks": 259,
    "topics": {},
    "species": {},
    "sources": {},
    "curation_status": {}
  }
}
```

A finalidade era impedir comparações entre duas rodadas que pareciam diferentes, mas na verdade consultavam a mesma base — ou o oposto.

---

# 9. Correções no comparador de recuperação

Arquivo principal:

```text
scripts/retrieval_compare.py
```

## 9.1. Fingerprint por rodada

O comparador passou a ler o fingerprint armazenado junto de cada execução.

Isso evitava depender apenas do estado atual da base, que poderia ter mudado depois da coleta da rodada.

Comportamento esperado:

```python
before_fingerprint = load_run_fingerprint(before_run)
after_fingerprint = load_run_fingerprint(after_run)
```

Foi mantido fallback conservador para artefatos históricos que não possuíam o novo fingerprint.

O fallback não poderia inventar cobertura ou tratar ausência de informação como sucesso.

---

## 9.2. Correção do item B-55

O relatório histórico havia identificado que o único artigo real da base — sobre `canine_heatstroke` — não aparecia no top-5 de nenhum dos 18 casos da régua.

A lógica foi corrigida para distinguir:

* Documento indexado.
* Documento recuperável.
* Documento esperado para determinado caso.
* Documento que apareceu por acaso em caso não relacionado.

Um tópico/documento somente deveria ser classificado como “encontrável” quando:

* Existisse na base nova.
* Fosse esperado no caso avaliado.
* Aparecesse na recuperação dentro do limite definido.

---

## 9.3. Cobertura por espécie

O comparador passou a verificar cobertura de espécies.

Um resultado não deveria ser considerado adequado apenas porque recuperou um tema semanticamente parecido se:

* O documento era exclusivo de gatos e o caso era de cachorro.
* O documento era exclusivo de cães e o caso era felino.
* A espécie não estava declarada.

A regra deveria aceitar explicitamente categorias canônicas, por exemplo:

```text
dog
cat
dog_and_cat
```

Ou os valores canônicos já adotados pelo repositório, desde que consistentes.

---

## 9.4. Gabarito a atualizar

O comparador possuía um bloco para indicar possíveis casos cujo gabarito deveria ser atualizado após a adição de novos assuntos.

Foi corrigido um falso positivo:

* A primeira versão marcava assuntos que já existiam antes.
* O comportamento correto era considerar somente tópicos realmente novos na coleção posterior.
* Um tópico existente nas duas bases não deveria gerar recomendação.

Conceito:

```python
new_topics = after_topics - before_topics

for case in cases:
    recovered_new_topics = recovered_topics(case) & new_topics
    if recovered_new_topics:
        add_to_gabarito_review(case)
```

---

# 10. Orquestração completa de uma rodada

Foi criado:

```text
scripts/run_ingestion_cycle.py
```

O objetivo era empacotar o ciclo completo em um único comando controlado.

Fluxo esperado:

1. Registrar fingerprint da base atual.
2. Executar a régua antes da ingestão.
3. Validar documentos e sidecars.
4. Criar coleção staged/versionada.
5. Gerar manifesto e recibo.
6. Validar a coleção candidata.
7. Opcionalmente ativar a coleção.
8. Executar a régua depois da ativação.
9. Comparar antes/depois.
10. Gerar relatório.
11. Executar consenso/verificações adicionais.
12. Salvar todos os artefatos na pasta de evidências.

O script deveria interromper o processo se qualquer fase crítica falhasse.

Pseudocódigo:

```python
def run_cycle(config):
    before = capture_current_state()
    run_retrieval_eval(before)

    staged = ingest_to_staged_collection(
        profile=config.profile,
        documents_path=config.documents_path,
    )

    validate_manifest(staged)
    validate_collection_integrity(staged)

    if config.stage_only:
        return staged

    activate_collection(staged.name)

    after = capture_current_state()
    run_retrieval_eval(after)

    comparison = compare_runs(before.run, after.run)
    consensus = verify_consensus(staged, comparison)

    write_cycle_receipt(
        before=before,
        staged=staged,
        after=after,
        comparison=comparison,
        consensus=consensus,
    )
```

---

# 11. Verificação de consenso vetorial

Foram criados:

```text
scripts/verify_vector_consensus.py
scripts/tests/test_vector_consensus.py
```

O verificador tinha como objetivo checar se os diferentes artefatos produzidos na ingestão concordavam entre si.

Deveria cruzar:

* Manifesto.
* Fingerprint.
* Recibo da ingestão.
* Contagem real da coleção.
* Relatório de avaliação.
* Comparação antes/depois.

Exemplos de inconsistência que deveriam falhar:

* Manifesto diz 259 chunks, mas coleção contém 258.
* Hash de IDs não coincide.
* Recibo aponta uma coleção e fingerprint aponta outra.
* Modelo/revisão do manifesto difere do fingerprint.
* Perfil registrado difere do perfil executado.
* Relatório posterior foi produzido contra outra base.

---

# 12. Sidecars e curadoria documental

## 12.1. Documentos legados

Os oito sidecars legados foram revisados para:

* Declarar status experimental.
* Usar espécies canônicas.
* Diferenciar fonte e arquivo.
* Impedir promoção automática para `curated`.

Documentos envolvidos:

```text
backend/data/documents/convulsoes.json
backend/data/documents/dificuldade_respiratoria.json
backend/data/documents/intoxicacao_cebola_alho.json
backend/data/documents/intoxicacao_chocolate.json
backend/data/documents/obstrucao_urinaria_gatos.json
backend/data/documents/pathophysiology_heatstroke_dogs_2017.json
backend/data/documents/trauma_hemorragia.json
backend/data/documents/vomito_diarreia.json
```

Todos deveriam permanecer equivalentes a:

```json
{
  "experimental_only": true,
  "curation_status": "experimental"
}
```

Os valores exatos dos campos precisam ser conferidos com o schema reconstruído.

---

## 12.2. Cinco capturas candidatas

Cinco sidecars provenientes do processo de captura documental foram preparados como candidatos à curadoria.

Eles não foram automaticamente aprovados.

Os campos humanos continuaram pendentes, incluindo elementos como:

* Validação da fonte.
* Adequação clínica.
* Espécie.
* Tópico.
* Trechos incluídos.
* Trechos excluídos.
* Responsável pela revisão.
* Data da revisão.
* Justificativa de curadoria.
* Status final.

A reconstrução deve localizar os cinco JSONs modificados dentro de:

```text
data/curadoria/fontes/
```

O histórico preservado não contém os cinco nomes exatos. A IA responsável deverá comparar o conteúdo atual dessa pasta com o fluxo de captura e identificar os candidatos modificados, sem inventar aprovação clínica.

---

## 12.3. Regra essencial

Nenhum documento capturado deveria entrar na base `curated` apenas porque:

* Foi baixado corretamente.
* Possui conteúdo.
* Produziu chunks.
* Passou em testes técnicos.

A aprovação técnica não substitui a validação humana/especialista.

---

# 13. Configuração, dependências e Docker

## 13.1. Configuração padrão do Chroma

Foi ajustado:

```text
CHROMA_PATH=data/chroma
```

A coleção também passou a ser configurável por variável de ambiente.

Arquivos envolvidos:

```text
.env.example
backend/app/core/config.py
```

---

## 13.2. Dependências fixadas

Foram fixadas versões para reduzir variações entre máquinas.

Elementos registrados:

* Dependências do backend fixadas.
* Dependências de desenvolvimento fixadas.
* Dependências dos scripts fixadas.
* Dependências do frontend fixadas.
* Torch CPU separado.
* Ollama fixado em `0.33.3`.
* MongoDB fixado em `7.0.41`.

Foi criado:

```text
backend/requirements-torch-cpu.txt
```

O Dockerfile foi ajustado para instalar a versão CPU do PyTorch, evitando dependências CUDA desnecessárias.

---

## 13.3. Docker Compose

O `docker-compose.yml` foi atualizado para utilizar versões fixas.

Componente registrado:

```text
MongoDB 7.0.41
Ollama 0.33.3
```

A execução completa do Docker não foi realizada porque Docker não estava disponível no ambiente perdido.

Portanto:

* A configuração foi alterada.
* Testes Python passaram.
* A montagem do ambiente completo em Docker permaneceu pendente.

---

# 14. CI no GitHub Actions

Foi criado:

```text
.github/workflows/tests.yml
```

A intenção era executar automaticamente:

* Testes do backend.
* Testes dos scripts.
* Verificação de dependências.
* Compilação/importação.
* Possivelmente validação de arquivos JSON/YAML.

A workflow não chegou a ser publicada. Portanto nunca foi executada pelo GitHub Actions.

A reconstrução deve verificar:

* Versão do Python.
* Cache de dependências.
* Instalação de Torch CPU.
* Diretórios corretos para executar cada suíte.
* Variáveis de ambiente mínimas.
* Ausência de dependência em serviços externos reais.
* Ausência de download imprevisível do modelo, ou cache/configuração adequada.

---

# 15. Agente especializado de ingestão

Foram criados:

```text
.claude/agents/ingestao.md
agentes/ingestao.md
```

E atualizado:

```text
agentes/README.md
```

O agente deveria orientar futuras tarefas de ingestão segundo as novas regras:

* Não alterar a coleção ativa diretamente.
* Não considerar captura como curadoria.
* Executar avaliação antes da ingestão.
* Usar perfil explicitamente.
* Produzir coleção staged.
* Validar manifesto.
* Registrar fingerprints.
* Executar comparação antes/depois.
* Documentar métricas.
* Não inventar aprovação clínica.
* Não citar números sem apontar para artefato persistido.
* Não ativar coleção experimental como curada.
* Preservar rollback.
* Registrar concentração temática e lacunas de cobertura.

---

# 16. Arquivos modificados

Abaixo está o inventário preservado dos arquivos modificados.

## 16.1. Raiz e infraestrutura

```text
.env.example
README.md
docker-compose.yml
```

## 16.2. Agentes

```text
agentes/README.md
```

## 16.3. Backend — configuração, banco e retrieval

```text
backend/Dockerfile
backend/app/clients/retrieval_client.py
backend/app/core/config.py
backend/app/database/chroma_client.py
backend/app/database/document_processing.py
backend/app/database/embedding_config.py
backend/app/database/ingest_documents.py
backend/app/services/fingerprint_service.py
```

## 16.4. Documentação da base documental

```text
backend/data/documents/README.md
```

## 16.5. Sidecars documentais

```text
backend/data/documents/convulsoes.json
backend/data/documents/dificuldade_respiratoria.json
backend/data/documents/intoxicacao_cebola_alho.json
backend/data/documents/intoxicacao_chocolate.json
backend/data/documents/obstrucao_urinaria_gatos.json
backend/data/documents/pathophysiology_heatstroke_dogs_2017.json
backend/data/documents/trauma_hemorragia.json
backend/data/documents/vomito_diarreia.json
```

## 16.6. Dependências

```text
backend/requirements-dev.txt
backend/requirements.txt
frontend/requirements.txt
scripts/requirements.txt
```

## 16.7. Testes existentes modificados

```text
backend/tests/test_api_health.py
backend/tests/test_api_search.py
backend/tests/test_document_processing.py
backend/tests/test_pdf_layout_extraction.py
scripts/tests/test_capturar_fonte.py
scripts/tests/test_retrieval_compare.py
```

## 16.8. Curadoria

```text
data/curadoria/README.md
data/curadoria/fontes/README.md
data/curadoria/mapa-de-assuntos.csv
```

Além desses, cinco arquivos JSON dentro de:

```text
data/curadoria/fontes/
```

foram modificados. Os nomes exatos não sobreviveram ao descarte do ambiente e deverão ser identificados durante a reconstrução.

## 16.9. Retrieval e relatórios

```text
data/retrieval/README.md
```

Também foram modificados artefatos históricos de comparação em:

```text
data/retrieval/
```

Incluindo arquivos `.json` e `.md`. A reconstrução não deve sobrescrever resultados históricos sem compreender a função de cada um.

## 16.10. Documentação geral

```text
docs/CONTRATOS.md
docs/README.md
docs/ingestao-documental.md
docs/plano-base-e-prova.md
```

## 16.11. Evidências

```text
evidencias/backlog.md
evidencias/joao/2026-09-12-14-compare-da-regua.md
evidencias/joao/README.md
evidencias/vini/README.md
evidencias/vini/planejamento.md
```

## 16.12. Scripts

```text
scripts/README.md
scripts/capturar_fonte.py
scripts/retrieval_compare.py
scripts/retrieval_compare_report.py
```

---

# 17. Arquivos criados

Os seguintes arquivos eram novos e estavam sem rastreamento ou recém-criados:

```text
.claude/agents/ingestao.md
.github/workflows/tests.yml
agentes/ingestao.md
backend/requirements-torch-cpu.txt
backend/tests/test_chroma_ingestion_integration.py
backend/tests/test_ingestion_safety.py
docs/estado-atual.md
evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.md
evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.json
scripts/run_ingestion_cycle.py
scripts/tests/test_vector_consensus.py
scripts/verify_vector_consensus.py
```

---

# 18. Função esperada de cada arquivo central

| Arquivo                                | Responsabilidade reconstruída                                      |
| -------------------------------------- | ------------------------------------------------------------------ |
| `embedding_config.py`                  | Centralizar modelo, revisão, tokenizer e identidade da receita     |
| `document_processing.py`               | Extração, normalização, chunking e separação do `body`             |
| `ingest_documents.py`                  | CLI e pipeline de ingestão com perfis, staging, manifesto e recibo |
| `chroma_client.py`                     | Acesso lazy ao Chroma, coleção ativa, staging, ativação e rollback |
| `retrieval_client.py`                  | Consultar coleção ativa e devolver corpo limpo/metadados           |
| `fingerprint_service.py`               | Calcular identidade completa da base e contagens                   |
| `retrieval_compare.py`                 | Comparar rodadas com fingerprints e critérios corrigidos           |
| `retrieval_compare_report.py`          | Produzir relatório legível e auditável                             |
| `run_ingestion_cycle.py`               | Orquestrar ciclo antes/ingestão/depois/comparação                  |
| `verify_vector_consensus.py`           | Cruzar manifesto, coleção, fingerprint, recibo e avaliação         |
| `test_ingestion_safety.py`             | Garantir travas dos perfis e ausência de substituição insegura     |
| `test_chroma_ingestion_integration.py` | Testar comportamento real do Chroma temporário                     |
| `test_vector_consensus.py`             | Testar detecção de divergências entre artefatos                    |
| `docs/estado-atual.md`                 | Explicar estado verdadeiro, limitações e próximos passos           |
| Evidência MD/JSON                      | Registrar resultados reais da rodada técnica                       |

---

# 19. Resultados exatos da ingestão real temporária

## 19.1. `legacy_rechunk`

```text
documentos: 7
chunks: 73
tokens mínimos: 55
tokens médios: 82,658
mediana: 82
tokens máximos: 128
fallbacks: 0
documentos corrompidos: 0
warnings: 56
```

Hashes:

```text
source_set_sha256:
49f1ac47d28c58a64536dfec0b848ddac6428e94f34e245adaf1b5d5439f98dc

recipe_sha256:
64952a575f5ebf686ef83e595c4f30593f5461f198b15eee0c19a8397bf25c93

chunk_ids_sha256:
eefb077334cfc25ca9b0b4ef8d4791ad25fd07a79c47712db4483d7e05fcbaba

chunk_content_sha256:
59f8c4d2599dc9e21845e2b03475ae30adf177977d5374ec6fcda02d2e8e0e9b
```

---

## 19.2. `experimental`

```text
documentos: 8
chunks: 259
tokens mínimos: 48
tokens médios: 86,768
mediana: 92
tokens máximos: 128
fallbacks: 31
documentos corrompidos: 1
warnings: 63
```

Concentração:

```text
chunks relacionados a heatstroke: 186
percentual: 71,8%
```

Hashes:

```text
source_set_sha256:
d4609db6bd2e71bb6bec234de61574323f985c7edd95e08df49697cc2720be2a

recipe_sha256:
64952a575f5ebf686ef83e595c4f30593f5461f198b15eee0c19a8397bf25c93

chunk_ids_sha256:
0f0c383c3835e41dd9520c0444e66aea6dde544fb387bb04fa011ca2ceb2a6ed

chunk_content_sha256:
8b40b2bcb2e03ac865509722bdfcd6f9acbe8d039a7155c466d02880c1cd75e9
```

---

## 19.3. `curated`

```text
documentos elegíveis: 0
exit code: 2
coleção criada: não
diretório Chroma criado: não
```

Isso comprovou que a validação acontecia antes da inicialização/mutação do banco.

---

# 20. Smoke test real de recuperação

Foi realizada uma consulta na coleção experimental temporária.

Resultado:

```text
top-5: todos relacionados a heatstroke
```

Scores registrados:

```text
1. 0,6986
2. 0,6905
3. 0,6645
4. 0,6500
5. 0,6499
```

Observações:

* O corpo recuperado estava limpo.
* Título e seção não estavam indevidamente duplicados no `body`.
* Todos os resultados ficaram abaixo do limiar `0,7`.
* A recuperação evidenciou a concentração excessiva do corpus em heatstroke.
* A execução não provou qualidade clínica geral.
* O teste confirmou funcionamento técnico e revelou desbalanceamento documental.

---

# 21. Testes executados

Resultados finais registrados:

```text
backend: 197 testes aprovados
scripts: 176 testes aprovados
total: 373 testes aprovados
```

Dentro do backend estavam incluídos quatro testes com ChromaDB real temporário.

Verificações adicionais aprovadas antes da última atualização documental:

```text
pip check
git diff --check
compileall
parsing de JSON
parsing de YAML
```

A última alteração realizada foi uma atualização em documentação/evidências. Depois dessa última alteração, `git diff --check` e os demais validadores não chegaram a ser repetidos.

Portanto, a reconstrução deve executar tudo novamente.

---

# 22. Categorias de testes que precisam ser reconstruídas

## 22.1. Processamento documental

Testar:

* `DocumentChunk.body`.
* Separação entre corpo e texto de embedding.
* Título presente no embedding.
* Seção presente no embedding.
* Corpo preservado.
* Limite máximo de 128 tokens.
* Documentos sem headings.
* `include_sections`.
* `exclude_sections`.
* Normalização de acentos.
* Normalização de indentação/tabulação.
* Fragmentos muito pequenos.
* Fragmentos grandes.
* IDs determinísticos.
* Ordem determinística dos chunks.

## 22.2. Segurança da ingestão

Testar:

* Perfil `curated` rejeita documento pendente.
* Perfil `curated` rejeita `experimental_only`.
* Perfil `curated` rejeita documento corrompido.
* Perfil `curated` rejeita campo humano ausente.
* Validação ocorre antes da criação do Chroma.
* Ingestão com falha não altera ponteiro ativo.
* `stage-only` não ativa.
* Coleção ativa não pode ser excluída.
* Coleção versionada sem manifesto é rejeitada.
* Coleção legada sem manifesto segue compatível apenas na exceção prevista.
* Ativação valida contagem e hashes.
* Rollback reativa coleção válida.
* Rollback inválido preserva coleção atual.

## 22.3. Integração real com ChromaDB

Testar em diretório temporário:

* Criar staged collection.
* Persistir chunks.
* Reabrir cliente.
* Localizar coleção ativa.
* Ativar candidata.
* Ler após reabertura.
* Rollback.
* Ponteiro para coleção inexistente falha.
* Ponteiro obsoleto não cria coleção vazia.
* Metadados são aceitos pelo Chroma.
* Quantidade real coincide com manifesto.

## 22.4. Comparador

Testar:

* Mesmo caso, mesma base.
* Mesmo caso com base diferente.
* Fingerprint por rodada.
* Fallback de artefato histórico.
* Tópico realmente novo.
* Tópico já existente não aparece como novo.
* Documento recuperado em caso inesperado não conta como encontrável.
* Compatibilidade de espécie.
* Falha por alteração indevida do caso/gabarito.
* Interseção de IDs entre rodadas.
* Critério do IMA.
* Casos leves acima do corte.
* Casos que pioraram.
* Casos novos encontráveis.

## 22.5. Consenso

Testar:

* Contagens iguais.
* Contagem divergente.
* Hash de IDs divergente.
* Hash de conteúdo divergente.
* Modelo divergente.
* Revisão divergente.
* Coleção divergente.
* Perfil divergente.
* Recibo ausente.
* Manifesto ausente.
* Fingerprint ausente.

---

# 23. Documentação produzida

## 23.1. `docs/estado-atual.md`

Deveria registrar:

* Estado real da base.
* Documentos disponíveis.
* Diferença entre capturado, experimental e curado.
* Perfil recomendado para cada atividade.
* Limitações da base.
* Concentração em heatstroke.
* Ausência de documentos aprovados.
* Estado dos testes.
* Docker pendente.
* CI pendente.
* Próximas decisões.

## 23.2. `docs/ingestao-documental.md`

Deveria documentar:

* Como adicionar PDF.
* Como criar sidecar.
* Campos obrigatórios.
* Perfis.
* Chunking.
* Embedding.
* Staging.
* Manifesto.
* Ativação.
* Rollback.
* Avaliação antes/depois.
* Evidências.
* Comandos CLI.

## 23.3. `docs/CONTRATOS.md`

Deveria formalizar contratos como:

* Uma coleção ativa sempre aponta para coleção existente.
* Coleção versionada exige manifesto.
* Documento curado exige aprovação humana.
* Hash e contagem devem coincidir.
* Corpo e texto de embedding têm papéis diferentes.
* Comparações usam fingerprints da rodada.
* A ausência de informação histórica não pode virar resultado positivo.

## 23.4. Errata dos resultados históricos

Os documentos históricos de comparação receberam observações para explicar que:

* Resultados anteriores foram calculados com a lógica disponível naquele momento.
* O item B-55 precisava de interpretação corrigida.
* “Indexado” não significava “encontrável”.
* Novos relatórios deveriam usar fingerprints e cobertura por espécie.
* Números históricos não deveriam ser silenciosamente reescritos.

---

# 24. Evidência criada

Arquivos:

```text
evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.md
evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.json
```

A evidência deveria registrar:

* Commit-base.
* Escopo da alteração.
* Arquivos principais.
* Modelo/revisão.
* Perfis.
* Resultados das ingestões temporárias.
* Estatísticas de tokens.
* Hashes.
* Resultados dos testes.
* Smoke test.
* Problema de concentração temática.
* Curated com zero elegíveis.
* Docker não executado.
* CI não executada.
* Pendências humanas.
* Limitações do checklist anexado.

---

# 25. Relação com os anexos

Foram analisados dois anexos:

```text
Descrição-do-projeto-de-TCC.txt
Checklist.pdf
```

Conclusões registradas:

* A descrição do projeto possuía escopo mais amplo que a implementação atual.
* Ela citava elementos como especialidade, hospital, rota, Flutter, webhook, SaaS e “pré-diagnóstico”.
* Esses elementos não deveriam ser tratados como já implementados.
* O foco atual da ingestão era a base documental e a recuperação vetorial.
* O `Checklist.pdf` parecia relacionado a outro trabalho/atividade, envolvendo Databricks e rendimento escolar, não sendo evidência adequada do pipeline veterinário.
* A documentação deveria deixar essa divergência explícita, evitando misturar requisitos de contextos diferentes.

---

# 26. Avaliação técnica da estratégia de chunking

A técnica implementada era razoável e significativamente mais robusta que a anterior, mas não poderia ser considerada clinicamente “completa”.

Pontos positivos:

* Tokenização baseada no tokenizer real do modelo.
* Limite máximo coerente com `max_seq_length = 128`.
* Separação por headings quando disponíveis.
* Controle de seções incluídas e excluídas.
* IDs determinísticos.
* Título e seção incorporados ao embedding.
* Corpo limpo preservado.
* Métricas de distribuição registradas.
* Fallback contabilizado.
* Avisos e documentos corrompidos contabilizados.
* Receita identificada por hash.

Limitações:

* Documentos sem headings geram chunks menos semanticamente precisos.
* Um artigo de 16 páginas dominava 71,8% da coleção experimental.
* Quantidade de chunks não equivale a cobertura temática.
* O limite de 128 tokens pode fragmentar contexto clínico.
* Não havia validação clínica dos limites semânticos dos chunks.
* O overlap precisa ser reconstruído e documentado.
* A qualidade do OCR/extrator continua relevante.
* O corpus ainda era pequeno e desequilibrado.
* Não havia documentos aprovados no perfil `curated`.

A nova IA não deve alterar imediatamente tamanho e overlap. Primeiro deve reconstruir a receita que produziu o hash:

```text
64952a575f5ebf686ef83e595c4f30593f5461f198b15eee0c19a8397bf25c93
```

Se não for possível reproduzi-lo, deve registrar uma nova versão de receita e não fingir equivalência com a rodada perdida.

---

# 27. O que ainda faltava quando o trabalho foi interrompido

## 27.1. Repetir validações após a última edição

Executar novamente:

```bash
git diff --check
python -m compileall backend scripts
pip check
```

Também validar todos os JSONs e YAMLs.

## 27.2. Revisar o diff completo

Precisava ser verificado:

* Nenhum arquivo temporário incluído.
* Nenhum banco Chroma temporário incluído.
* Nenhum cache incluído.
* Nenhum modelo baixado incluído.
* Nenhuma credencial incluída.
* Nenhuma evidência com caminhos temporários.
* Nenhum resultado experimental descrito como produção.
* Consistência entre README, docs e CLI.
* Consistência dos números em MD e JSON.

## 27.3. Executar Docker

Pendente:

```bash
docker compose build
docker compose up
```

E posteriormente:

* Health check da API.
* Busca `/search/`.
* Persistência do Chroma.
* Compatibilidade com Mongo/Supabase.
* Reinício dos containers.
* Leitura da coleção ativa depois do reinício.

## 27.4. Executar CI

Somente seria possível depois da publicação da branch.

## 27.5. Publicar a branch

Operações que não ocorreram:

```bash
git add -A
git commit
git push -u origin codex/harden-vector-ingestion
```

## 27.6. Abrir PR

O PR deveria:

* Apontar para `main`.
* Explicar que não havia documentos curados.
* Incluir os 373 testes.
* Incluir hashes/métricas.
* Informar Docker e CI como pendências.
* Solicitar revisão cuidadosa de ingestão e documentação.
* Não prometer melhoria clínica ainda não comprovada.

---

# 28. Plano recomendado para reconstrução por outra IA

## Fase 1 — preservar o estado atual

1. Clonar o repositório.
2. Confirmar que o `HEAD` é `c3f09ec...` ou registrar o novo `HEAD`.
3. Criar branch:

```bash
git switch -c codex/harden-vector-ingestion-recovery
```

4. Executar testes atuais antes de editar.
5. Salvar baseline em evidência.
6. Não alterar `main` diretamente.
7. Não reescrever artefatos históricos.

## Fase 2 — reconstruir núcleo mínimo

Nesta ordem:

1. `embedding_config.py`
2. `document_processing.py`
3. `chroma_client.py`
4. `ingest_documents.py`
5. `retrieval_client.py`
6. `fingerprint_service.py`

Critério: todos os testes do backend devem passar antes de avançar.

## Fase 3 — segurança e versionamento

Implementar:

1. Perfis.
2. Validação prévia.
3. Staging.
4. Manifesto.
5. Ponteiro ativo.
6. Ativação.
7. Rollback.
8. Proteção da coleção ativa.
9. Rejeição de ponteiro obsoleto.
10. Compatibilidade legada restrita.

## Fase 4 — testes reais

Reconstruir:

```text
test_ingestion_safety.py
test_chroma_ingestion_integration.py
```

Usar apenas diretórios temporários.

## Fase 5 — comparador e consenso

Reconstruir:

```text
retrieval_compare.py
retrieval_compare_report.py
verify_vector_consensus.py
run_ingestion_cycle.py
```

Depois atualizar testes dos scripts.

## Fase 6 — sidecars

1. Padronizar espécies.
2. Marcar legados como experimentais.
3. Revisar cinco candidatos.
4. Não aprovar nada automaticamente.
5. Validar schema.

## Fase 7 — documentação

Atualizar todos os READMEs, contratos, estado atual, backlog e evidências.

## Fase 8 — reprodução das métricas

Executar novamente os três perfis.

Os números podem ser comparados aos resultados perdidos, mas os novos resultados devem ser considerados oficiais.

## Fase 9 — validação final

Executar:

```bash
pytest
pip check
git diff --check
python -m compileall backend scripts
```

Além de validação de JSON/YAML e Docker.

## Fase 10 — publicação

Somente depois de tudo aprovado:

```bash
git add -A
git commit -m "Endurece ingestão vetorial, versionamento e evidências"
git push -u origin codex/harden-vector-ingestion-recovery
```

Abrir PR contra `main`.

---

# 29. Critérios de aceite da reconstrução

A reconstrução somente pode ser considerada concluída se:

* [ ] Ingestão `curated` falhar antes de tocar no Chroma quando não houver elegíveis.
* [ ] Ingestão experimental criar coleção staged.
* [ ] Coleção staged não substituir automaticamente a ativa.
* [ ] Manifesto registrar modelo, revisão, receita, fontes e chunks.
* [ ] Hashes forem verificados antes da ativação.
* [ ] Ponteiro ativo persistir.
* [ ] Ponteiro inválido falhar explicitamente.
* [ ] Ponteiro inválido não criar coleção vazia.
* [ ] Rollback funcionar.
* [ ] Coleção ativa não puder ser apagada.
* [ ] Coleções versionadas sem manifesto forem rejeitadas.
* [ ] Coleção legada tiver exceção restrita e documentada.
* [ ] `DocumentChunk.body` estiver separado do texto de embedding.
* [ ] Embedding usar título + seção + corpo.
* [ ] Retrieval retornar corpo limpo.
* [ ] Modelo e tokenizer usarem revisão fixa.
* [ ] Fingerprint for armazenado por rodada.
* [ ] Comparador tratar apenas tópicos realmente novos.
* [ ] Cobertura por espécie for validada.
* [ ] “Indexado” e “encontrável” forem conceitos distintos.
* [ ] Manifesto, fingerprint, recibo e coleção concordarem.
* [ ] Sidecars legados permanecerem experimentais.
* [ ] Documentos pendentes não entrarem em `curated`.
* [ ] Testes de backend e scripts passarem.
* [ ] Docker for testado ou marcado explicitamente como pendente.
* [ ] CI for executada.
* [ ] Métricas forem persistidas em JSON e explicadas em Markdown.
* [ ] Nenhum número antigo for apresentado como reprodução nova.

---

# 30. Prompt pronto para entregar a outra IA

```text
Você deve reconstruir uma alteração perdida do repositório
https://github.com/vinizika/tcc.

Leia integralmente o relatório de recuperação fornecido antes de editar.

Regras obrigatórias:

1. Não trabalhe diretamente na main.
2. Registre o HEAD inicial.
3. Execute e registre os testes antes de alterar o código.
4. Inspecione todos os arquivos atuais antes de reconstruí-los.
5. Preserve compatibilidade com as APIs existentes.
6. Não aprove documentos clinicamente.
7. Não trate documentos capturados como curados.
8. Não substitua a coleção ativa durante staging.
9. Não use get_or_create_collection ao resolver um ponteiro ativo.
10. Uma coleção versionada deve exigir manifesto válido.
11. Valide contagem e hashes antes da ativação.
12. Preserve rollback.
13. Separe corpo limpo do texto usado para embedding.
14. Fixe modelo e tokenizer na revisão
    e8f8c211226b894fcb81acc59f3b34ba3efd5f42.
15. Implemente os perfis curated, experimental e legacy_rechunk.
16. O perfil curated deve falhar antes de criar o Chroma quando não houver
    documentos elegíveis.
17. Armazene fingerprint por rodada.
18. Corrija o comparador para considerar apenas tópicos realmente novos,
    cobertura por espécie e documentos encontráveis nos casos esperados.
19. Reconstrua testes unitários e testes reais com Chroma temporário.
20. Não escreva no repositório resultados não reproduzidos.
21. Use os números históricos apenas como referência para comparação.
22. Após cada grupo de alterações, execute testes.
23. Ao final, execute backend, scripts, pip check, compileall,
    git diff --check, validação JSON/YAML e Docker.
24. Gere uma evidência Markdown e JSON com comandos, resultados, hashes,
    limitações e pendências.
25. Revise o diff completo antes do commit.
26. Publique uma branch e abra um PR contra main.

Reconstrua primeiro o núcleo:
embedding_config.py, document_processing.py, chroma_client.py,
ingest_documents.py, retrieval_client.py e fingerprint_service.py.

Depois reconstrua:
retrieval_compare.py, retrieval_compare_report.py,
run_ingestion_cycle.py e verify_vector_consensus.py.

Por fim, atualize testes, sidecars, dependências, documentação, CI,
agentes e evidências.

Não tente obter o mesmo hash alterando resultados manualmente.
Se a receita reconstruída não reproduzir os hashes históricos, crie uma
nova versão de receita e documente a diferença.
```

---

# 31. Conclusão

O trabalho perdido não era apenas a adição de documentos. Ele endurecia todo o ciclo de vida da base vetorial:

* entrada documental;
* validação;
* chunking;
* embedding;
* staging;
* integridade;
* ativação;
* rollback;
* avaliação;
* comparação;
* evidência;
* reprodutibilidade.

O núcleo técnico havia atingido um estado forte nos testes locais, com **373 testes aprovados**, mas ainda faltavam:

* revisão final do diff;
* repetição das validações depois da última atualização documental;
* teste completo em Docker;
* execução da CI;
* commit;
* push;
* PR;
* validação humana dos documentos candidatos.

A conclusão mais importante deve ser preservada:

> O pipeline estava tecnicamente preparado para receber mais documentos, mas a base curada ainda não estava pronta, pois não havia nenhum documento completamente aprovado. A próxima evolução deveria priorizar curadoria e equilíbrio temático, não somente aumento da quantidade de chunks.
