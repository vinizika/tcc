# Fontes para as frases sem fonte das fichas de busca

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, na curadoria do time ·
**Rodada:** 27 · **Commits:** este

> Rodada de **curadoria**, feita em paralelo com as rodadas 23 a 26 por quatro
> agentes de IA pesquisadores, num worktree separado. Nenhum texto de ficha
> muda: a rodada procura, para as frases que os autores das fichas de busca
> marcaram como conhecimento geral, uma fonte que as sustente. Quem aprova
> cada fonte são os especialistas.

## O que foi feito

1. **As 53 frases `geral`** das fichas de busca
   ([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)), em 27 fichas,
   quase todas da etapa 2. São frases sem trecho de documento, que hoje só a
   certificação dos especialistas sustenta
   ([`CERTIFICACAO.md`](../../data/curadoria/fichas/CERTIFICACAO.md)).
2. **Quatro agentes pesquisadores**, com o roteiro do time
   ([`agentes/pesquisador.md`](../../agentes/pesquisador.md)), um grupo de
   tópicos cada. Por tópico, procuram fonte de autoridade alta ou média, de
   preferência escrita para tutor, abrem, julgam pela régua de aptidão (com
   citação literal) e capturam com o script do time
   ([`scripts/capturar_fonte.py`](../../scripts/capturar_fonte.py)), no máximo
   duas por tópico.
3. **Por frase**, o trecho literal da captura que a sustenta, ou "não
   encontrado" com as buscas feitas.
4. **A integração:** as capturas e os sidecars em
   `data/curadoria/fontes/capturas/`, uma seção nova no dossiê de cada tópico,
   uma linha por fonte em `PARA-VALIDAR.md` e, nas fichas, a frase que ganhou
   trecho deixa de ser `geral`.

## Por quê

- **O atendente não lê a ficha de busca, mas a busca depende dela.** As
  frases `geral` ajudam a achar a ficha certa (são o jeito do tutor contar), e
  nenhuma delas tem documento por trás. A certificação dos especialistas fica
  mais curta e mais segura quando cada frase já chega com o trecho que a
  sustenta.
- **A etapa 2 é onde falta fonte.** 48 dos 53 itens são da etapa 2, e cinco
  tópicos somam 22 deles (mordida de gato 7, corpo estranho 6, insuficiência
  cardíaca 3, tosse dos canis 3, cobra 3). São justamente os quadros em que o
  mapa ainda não tem sinais nem discriminador.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| **A frase não muda**, mesmo quando a fonte diz um pouco diferente | O número da réplica (rodadas 24 e 26) depende do texto das fichas. Divergência entre frase e fonte fica anotada para o especialista, que decide |
| A frase que ganhou trecho vira `origem: documento`, com `fonte` apontando a captura em `data/curadoria/fontes/capturas/` e `aprovacao: pendente` | Distingue, sem mudar o formato, o trecho de documento aprovado do trecho de fonte que ainda espera o especialista |
| A coluna `cobertura` do mapa **não** muda | Os 27 tópicos já estão `fonte_aprovada`; `fonte_encontrada` seria rebaixar. A fonte nova nasce `pending_specialist` no sidecar e aparece em `PARA-VALIDAR.md` |
| Nada é copiado para `backend/data/documents/` e nada é reindexado | Indexar é o passo do agente de ingestão, depois do aval |
| O `--inspect` da ingestão (passo 7 do roteiro) não roda | As fontes sustentam frases de ficha; não vão virar trechos da coleção acadêmica agora. Se um dia forem indexadas, o passo roda antes |
| Direitos autorais não bloqueiam; o sidecar registra o que o site declara | Combinado com o João (as capturas ficam na curadoria, fora da base) |

## Resultado esperado

_Escrito antes de os agentes começarem._

- **Pelo menos 60% dos 53 itens** com trecho literal de fonte de autoridade
  alta ou média. Menos nos itens de "como o tutor conta" (o jeito do tutor
  falar raramente está numa fonte autoritativa) do que nos sinais de alarme.
- **No máximo 2 fontes por tópico**, todas abertas e capturadas pelo script.
- **Nenhuma frase de ficha muda**: o `sync_fichas.py --check` da
  [rodada 23](2026-09-25-24-fichas-de-busca-e-de-leitura.md) continua limpo, e
  o texto de busca das 61 fichas fica idêntico.

## Resultado obtido

**Das 53 frases, 36 ganharam um trecho literal de fonte que as sustenta (68%)**,
16 têm fonte que sustenta parte, e 1 ficou sem fonte. Nenhuma divergente.
Passa no esperado (≥ 60%).

| Frases `geral` | 53 |
|---|---|
| sustentadas por trecho literal (viraram `documento`, a aprovar) | **36** |
| sustentadas em parte (continuam `geral`; o trecho vai à folha de certificação) | 16 |
| sem fonte (`cat_bite_abscess`: "Sangra muito ou a ferida é funda") | 1 |
| trechos conferidos por programa no arquivo capturado (texto normalizado; PDF pelo `pymupdf`) | **52 de 52** |
| fontes capturadas pelo script do time | **45** (1 descartada: a página da Cruz Vermelha saiu só com o banner) |
| autoridade alta · média | 35 · 10 |
| em inglês · em português | 39 · 6 |
| para tutor · clínico · acadêmico | 39 · 4 · 2 |

Por tópico:

| Tópico | Frases | Sustentadas | Parciais | Sem fonte |
|---|---|---|---|---|
| `airway_foreign_body_choking` | 1 | 1 | 0 | 0 |
| `burns_and_electrical_injury` | 1 | 1 | 0 | 0 |
| `cat_bite_abscess` | 7 | 5 | 1 | 1 |
| `congestive_heart_failure` | 3 | 3 | 0 | 0 |
| `diabetic_ketoacidosis` | 1 | 1 | 0 | 0 |
| `distemper_neurological` | 2 | 2 | 0 | 0 |
| `exertional_panting_mild` | 2 | 1 | 1 | 0 |
| `fading_neonate` | 1 | 1 | 0 | 0 |
| `gastrointestinal_foreign_body` | 6 | 3 | 3 | 0 |
| `high_rise_syndrome_cats` | 1 | 0 | 1 | 0 |
| `human_medication_poisoning` | 1 | 1 | 0 | 0 |
| `hypoglycemia_toy_puppy` | 2 | 1 | 1 | 0 |
| `kennel_cough_mild` | 3 | 2 | 1 | 0 |
| `lily_toxicosis_cats` | 1 | 1 | 0 | 0 |
| `mild_upper_respiratory_signs` | 1 | 1 | 0 | 0 |
| `minor_wound` | 2 | 0 | 2 | 0 |
| `normal_whelping` | 1 | 0 | 1 | 0 |
| `otitis_externa_mild` | 1 | 1 | 0 | 0 |
| `periodontal_disease_mild` | 2 | 1 | 1 | 0 |
| `polyuria_polydipsia_investigate` | 2 | 1 | 1 | 0 |
| `rabies_exposure_wild_animal_bite` | 1 | 1 | 0 | 0 |
| `respiratory_distress` | 1 | 1 | 0 | 0 |
| `snake_and_scorpion_envenomation` | 3 | 2 | 1 | 0 |
| `tick_borne_disease_anemia` | 2 | 1 | 1 | 0 |
| `ticks_found_no_signs` | 2 | 1 | 1 | 0 |
| `trauma_and_bleeding` | 1 | 1 | 0 | 0 |
| `vestibular_syndrome_otitis_interna` | 2 | 2 | 0 | 0 |

**Nenhum texto de ficha mudou.** `sync_fichas.py --check` limpo; os 61 textos
de busca e de leitura continuam iguais aos da autópsia (`n2_conferir.py`); e
reindexar as fichas daria **o mesmo conteúdo** da coleção versionada
(`9274aff4…`, conferido pela ingestão sem gravar). Só o hash do arquivo
`fichas.json` muda, porque ele registra o hash dos rascunhos.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/curadoria/fontes/capturas/` | 45 capturas novas (`.txt`/`.pdf` + sidecar), 7,9 MB; os sidecars com `full_title`, `rights` (o que o site declara, `pending`) e uma nota de curadoria |
| `data/curadoria/fontes/<topic>.md` (27) | seção "Fontes para as frases gerais da ficha de busca (25/09, rodada 27)", com a régua de aptidão de cada fonte e as citações |
| `data/curadoria/fontes/PARA-VALIDAR.md` | uma linha por fonte nova, com o que o site declara de direitos |
| `data/curadoria/fichas/<topic>.json` (24) | as 36 frases sustentadas passam a `origem: documento`, com `trecho`, `fonte: capturas/…`, `aprovacao: pendente` |
| `data/curadoria/fichas/CERTIFICACAO.md` | os 36 itens marcados como "documento (fonte nova, a aprovar)" e os 16 parciais com o trecho |
| `backend/data/fichas.json` | regenerado (só o hash dos rascunhos muda) |

Commits: `0873bfa` (abre a rodada) e este.

## Observações

**1. A VCA proíbe redistribuir e reescrever por IA.** Cinco capturas são da
VCA (conteúdo da LifeLearn), cujo rodapé proíbe "cópia, impressão ou
redistribuição sem consentimento escrito" e o uso de IA para reescrever ou
republicar. Nada foi reescrito (a captura é literal e fica na curadoria), mas
o arquivo capturado está num repositório público. Registrado no sidecar e em
`PARA-VALIDAR.md`; a decisão de manter é do time. MSD e AKC: "todos os
direitos reservados"; Tufts, Cornell e PDSA: só o copyright.

**2. Fonte em português, com autoridade e para tutor, praticamente não
existe** para estas frases — o mesmo achado do piloto do pesquisador
([rodada 12](2026-09-12-13-pesquisador.md)). Das 6 fontes em português, 2 são
diretrizes clínicas (TroCCAP), 2 são TCCs e 1 é o Caderno Técnico da UFMG.

**3. A busca na web acabou no meio** (limite de 200 buscas por sessão, dividido
com os autores da prova 2 que rodavam ao mesmo tempo). Depois disso os
pesquisadores só abriram endereços de sites conhecidos (MSD, PDSA, Cornell,
índice dos Cadernos Técnicos). Hipoglicemia e recém-nascido ficaram com uma
fonte de autoridade média.

**4. Alguns trechos confirmam a frase e discordam do rótulo leve.** A
BluePearl, sobre tártaro, diz que o animal normal esconde doença e pede exame
anual; o MSD e a Cornell dizem que a tosse dos canis pode vir com apetite
menor e letargia. Anotado na folha para o especialista.

**5. Dois cuidados técnicos da captura**: no arquivo da AKC sumiu a lista logo
depois de "such as:"; no da VCA sobre filhote as temperaturas saíram com
caracteres quebrados (fora da frase usada). Um pesquisador precisou completar
a cadeia de certificados de dois sites brasileiros (UnB, UFMG) com o
intermediário oficial, sem desligar a verificação.

## Deixado para depois

- **Os especialistas aprovam ou recusam as 45 fontes** (`PARA-VALIDAR.md`) e
  as frases a partir delas ([B-61](../backlog.md#b-61)). Só depois uma fonte vai
  para `backend/data/documents/`, e só então as frases viram "documento
  aprovado".
- **A decisão sobre as capturas da VCA** (direitos).
- **`referencias.md`**: as fontes novas ainda não ganharam id `R..`.
- **A frase sem fonte** e as 16 parciais: o especialista confirma pelo
  conhecimento clínico, ou a frase muda — e mudar frase é rodada medida.

## Próximo passo

A validação dos especialistas, com a folha de certificação já anotada:

```
data/curadoria/fichas/CERTIFICACAO.md
data/curadoria/fontes/PARA-VALIDAR.md
```
