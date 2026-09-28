# As fichas de busca e de leitura, geradas por script

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, olhando o sistema inteiro
(os títulos e as âncoras são da curadoria do trilho A) · **Rodada:** 23 ·
**Commits:** este

> Primeira rodada de código da implementação. Leva ao repositório as **duas
> camadas de ficha** da [rodada 19](2026-09-24-20-fichas-em-duas-camadas.md):
> a ficha de busca (escrita por IA, para casar com o jeito do tutor) e a ficha
> de leitura (a do mapa, com a conduta fixa). Nenhuma frase de ficha é
> reescrita: o script remonta, a partir dos arquivos versionados, **o mesmo
> texto** que a autópsia mediu.

## O que foi feito

1. **`scripts/sync_fichas.py`**, no molde do `sync_retrieval_terms.py`: lê o
   mapa, os 61 rascunhos de `data/curadoria/fichas/` e as fichas dos
   documentos aprovados, e gera `backend/data/fichas.json`, o arquivo que o
   backend lê (o backend roda numa imagem que só tem `backend/`). Por tópico:
   - o **texto de busca** (a regra de montagem da autópsia, a mesma do
     `fichas_claude_montar.py`);
   - o **texto de leitura** e o seu título (a regra da ficha do mapa, a mesma do
     `exp_setup.py`);
   - o título para mostrar ao tutor, a espécie, a urgência, a etapa;
   - as **referências**: os documentos aprovados do tópico, com título real,
     periódico, ano e DOI;
   - o hash de cada texto.
   
   `--check` no CI, como o do vocabulário.
2. **Uma coluna nova no mapa, `por_que_importa`, vazia.** Hoje a ficha de
   leitura tira o "por que importa" do `motivo`, que é nota de curadoria, e
   11 fichas mostram ao atendente texto interno mesmo depois do filtro ("Caso
   b14", "não encontrei artigo primário"). A coluna é o lugar para os
   especialistas escreverem o texto limpo; vazia, o gerador continua usando o
   `motivo` filtrado, e o texto de leitura não muda.
3. **Títulos reais** nas fichas dos documentos da base
   (`backend/data/documents/*.json`), num campo novo, `full_title`, com o DOI
   quando houver.
4. **As âncoras saem** dos 6 sidecars que as tinham
   ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)).
5. O `backend/data/documents/README.md` corrigido onde contradiz os arquivos.

A coleção acadêmica **não é reindexada**: `…388f518d` continua como está, e é
o braço "hoje" da réplica.

## Por quê

- **O número da arquitetura nova depende do texto das fichas**, e até aqui
  esse texto só existia fora do repositório. Sem um gerador versionado, a
  réplica não teria como provar que o sistema lê o mesmo texto que a autópsia
  mediu, e cada mudança futura numa ficha não teria de onde partir.
- **A citação ao tutor usa o título do documento**, e 28 dos títulos gravados
  são rótulos inventados ("Feline abscess case"). A
  [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md#6-os-títulos-genéricos)
  mostrou que o título quase não pesa na busca; o defeito dele é aparecer ao
  tutor como fonte.
- **As âncoras escondiam a obstrução uretral** quando o tutor não dizia
  "xixi" ([rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md)); na busca
  por fichas elas não existem.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| O script reimplementa as duas regras de montagem, e o portão é **igualdade byte a byte** com os textos da autópsia | É a condição de paridade da réplica: "texto das fichas não muda esta noite" |
| Item de documento **sem trecho** fica fora do texto de busca; a conferência do trecho contra o documento fica no `conferencia.json` (curadoria) e não no script | É a regra da autópsia (1 item saiu assim). Conferir trecho contra PDF no CI exigiria extrair os 66 documentos a cada commit |
| Os sinais do mapa que o autor não cobriu entram como estão no mapa (2 casos) | Regra da autópsia: a frase validada do mapa entra sempre |
| Duas grafias de propósito: a ficha de busca tem acento ("Isto é uma emergência"), a de leitura não ("Isto e uma emergencia") | É o texto medido. Unificar é uma mudança de texto, e mudança de texto é rodada medida |
| `por_que_importa` no fim do mapa, vazia | Acrescentar coluna no fim é seguro para quem lê por nome; o texto de leitura só muda quando alguém a preencher |
| **`full_title` novo**, e o `title` fica como está (desvio do plano da noite, que trocava o `title` e criava um `label`) | O `title` entra no começo de todo trecho indexado; trocá-lo mudaria a coleção acadêmica numa reindexação, e o script de captura limita o `title` a 6 palavras. Com um campo novo, a ingestão e a captura (trilho A) não mudam |
| Referências = só documentos com `validation_status` de aprovação | A citação diz "documento aprovado por trás da ficha" |
| Hash dos arquivos com quebras de linha normalizadas | [B-71](../backlog.md#b-71): o hash de bytes falha num clone no Windows |

## Resultado esperado

_Escrito antes de rodar._

- **Os 61 textos de busca** iguais, byte a byte, aos de
  `_trabalho/fichas_cl.json` (o arquivo que a autópsia indexou), e **os 61
  textos de leitura** iguais aos de `artefatos_rodada2/fichas.json` (o que o
  atendente leu), com os mesmos títulos de leitura.
- **Tamanho:** nenhum texto de busca passa de 485 tokens do bge-m3 (o limite
  da coleção nova será 512).
- `sync_fichas.py --check` e `sync_retrieval_terms.py --check` limpos; suíte
  verde (backend 242, scripts 201 + os testes novos).
- **Títulos:** os 28 genéricos e os 5 abreviados ganham título real
  conferido pelo DOI ou pela página.

## Resultado obtido

**As duas camadas saem iguais, byte a byte, ao que a autópsia mediu.**

| Checagem | Resultado |
|---|---|
| 61 textos de busca × `_trabalho/fichas_cl.json` (o que a autópsia indexou) | **61 de 61 iguais** |
| 61 textos de leitura × `artefatos_rodada2/fichas.json` (o que o atendente leu) | **61 de 61 iguais** |
| 61 títulos de leitura × o mesmo arquivo | **61 de 61 iguais** |
| Tokens do bge-m3 (revisão `5617a9f6…`, com os especiais) no texto de busca | máximo **485** (`tremors_without_seizure`), mediana 315; nenhum acima de 485 |
| Tokens do texto de leitura | máximo 190 |
| Referências aprovadas | 66, em 61 de 61 tópicos (o documento `vomiting_and_diarrhea__ovj_2026_teletriage`, `published_not_locally_validated`, fica de fora) |
| `sync_fichas.py --check` e `sync_retrieval_terms.py --check` | limpos, depois de cada commit |
| Suíte | backend 242 → 242; scripts 201 → **209** (8 testes do gerador) |

A conferência é o script `rodada_noturna/scripts/n2_conferir.py` do diário
da noite (fora do repositório, porque lê os arquivos da autópsia).

**Os títulos.** Conferidos um a um por um agente de IA, pelo DOI no Crossref
(66 documentos, com o assunto e o ano batendo com o arquivo capturado) e pela
API do GOV.UK (a cartilha da permetrina, a única sem DOI):

| O `title` gravado era | Documentos |
|---|---|
| o título real | 32 |
| um rótulo inventado ("Feline abscess case", "Hemorrhage in Dogs and Cats") | 27 |
| um pedaço do título real | 8 |
| de outro documento | 0 |

Os 21 sidecars sem DOI ganharam o DOI confirmado. Nenhum DOI gravado apontava
para outro documento.

**O título real mostra que 6 documentos aprovados tratam de outra coisa** que
não o quadro em que estão:
- `cat_bite_abscess` é um relato de abscessos em linfonodos dentro do abdômen,
  não de mordida;
- a revisão felina de `flea_dermatitis_pruritus` trata da dermatite **não**
  causada por pulga;
- o SciELO 2013 de `pyometra` é um estudo de castração, em que a piometra é o
  achado mais comum;
- o de `osteoarthritis_stiffness` é um consenso de tratamento, não de sinais;
- o de `vomiting_and_diarrhea` (Frontiers 2023) é sobre prescrição de
  antimicrobiano;
- o de `single_vomiting_or_mild_diarrhea` é sobre exames em cães atendidos na
  emergência.

Os autores das próprias fichas de busca já tinham anotado o primeiro
([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)). Vai ao
[B-72](../backlog.md#b-72).

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/sync_fichas.py` | **novo**: gera `backend/data/fichas.json` do mapa, dos rascunhos e dos sidecars; `--check` |
| `scripts/tests/test_sync_fichas.py` | **novo**, 8 testes: as duas regras de montagem, a coluna nova, a gêmea múltipla, as referências, o hash com CRLF |
| `backend/data/fichas.json` | **novo**: 61 fichas (texto de busca, texto e título de leitura, título para o tutor, espécie, classe, urgência, etapa, referências, hashes) |
| `data/curadoria/mapa-de-assuntos.csv` | coluna `por_que_importa` no fim, vazia |
| `data/curadoria/README.md` | a coluna nova e o gerador |
| `scripts/tests/test_mapa_de_assuntos.py` | `COLUNAS` com a coluna nova |
| `backend/data/retrieval_terms.json` | regenerado (só o hash do mapa muda) |
| `.github/workflows/tests.yml` | passo `sync_fichas.py --check` |
| `backend/data/documents/*.json` (67) | `full_title` em todos; `doi` em 21; as âncoras saem de 6 |
| `backend/data/documents/README.md` | o exemplo de âncora que não existia sai; âncoras e `full_title` documentados |
| `evidencias/backlog.md` | [B-72](../backlog.md#b-72); [B-71](../backlog.md#b-71) atualizado |

Commits: `56048b0` (abre a rodada: gerador, coluna, CI), `d510b7b` (âncoras,
trilho A), `a1c72df` (títulos reais, trilho A) e este.

## Observações

**1. O gerador reproduz até as irregularidades do texto medido**, de
propósito: a ficha de busca tem acento e a de leitura não ("Isto é uma
emergência" × "Isto e uma emergencia"); o discriminador ganha um ponto depois
da interrogação ("Há esforço para respirar?."); a linha com mais de uma gêmea
não ganha a frase "Pode ser confundido com". Cada uma dessas é uma mudança de
texto a medir, não um conserto a fazer em silêncio.

**2. No Windows, o `sync_retrieval_terms.py` grava o JSON com CRLF.** O
`write_text` em modo texto converte as quebras de linha; o arquivo regenerado
aparece inteiro como mudado no Git. Foi normalizado para LF antes do commit.
Acrescentado ao [B-71](../backlog.md#b-71). O `sync_fichas.py` já grava com
`newline="\n"`.

**3. A ficha de leitura continua mostrando nota interna ao atendente** em 11
tópicos ("Caso b14", "não encontrei artigo primário"). A coluna
`por_que_importa` é onde os especialistas escrevem o texto limpo; quando
preencherem, é rodada medida ([B-61](../backlog.md#b-61)).

**4. Autores errados em 6 sidecars** (a cinomose tem a autoria inteira errada;
cinco têm um primeiro nome errado) e o `source` do GDV mistura periódico e
afiliação. Não mexi: não é o que a resposta mostra, e é curadoria do trilho A
([B-72](../backlog.md#b-72)).

## Deixado para depois

- **Os 6 documentos aprovados que tratam de outro assunto** e os metadados de
  autoria ([B-72](../backlog.md#b-72)).
- **Preencher `por_que_importa`** com os especialistas
  ([B-61](../backlog.md#b-61)); cada preenchimento é uma rodada medida.
- **Conferir o trecho de cada item de documento no CI**, e não só na
  curadoria: exigiria extrair os 66 documentos a cada commit. Fica o
  `conferencia.json`.

## Próximo passo

A [rodada 24](2026-09-25-25-busca-por-fichas-com-bge-m3.md): a coleção das
fichas no bge-m3 e a busca vetorial pura.

```
python -m app.database.ingest_documents --profile fichas --activate
```
