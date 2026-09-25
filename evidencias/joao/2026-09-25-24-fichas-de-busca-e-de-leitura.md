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

_(preenchido ao fechar a rodada)_

## O que mudou no repositório

_(preenchido ao fechar a rodada)_

## Observações

_(preenchido ao fechar a rodada)_

## Deixado para depois

_(preenchido ao fechar a rodada)_

## Próximo passo

_(preenchido ao fechar a rodada)_
