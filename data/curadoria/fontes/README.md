# Fontes: o caminho de uma linha do mapa até a base

Cada linha do [mapa de assuntos](../mapa-de-assuntos.csv) precisa de fonte
antes de virar documento. Esta pasta é onde esse trabalho mora.

```
fontes/
├── README.md                  <- este arquivo
├── PARA-VALIDAR.md            <- a mesa dos especialistas: uma linha por fonte
├── <topic>.md                 <- o dossiê de um quadro: candidatas, julgamento, citações
└── capturas/
    ├── <topic>__<slug>.txt    <- o texto capturado da fonte (ou .pdf)
    └── <topic>__<slug>.json   <- a ficha, no formato que a base espera
```

## A máquina de estados, e quem move cada seta

A coluna `cobertura` do mapa diz onde cada quadro está:

| Estado | Significa | Quem move para o próximo |
|---|---|---|
| `sem_documento` | Ninguém procurou ainda | **Pesquisador** |
| `sintetico` | Tem o protocolo de teste, que não é fonte real | **Pesquisador** |
| `fonte_encontrada` | Dossiê e captura existem; ninguém validou | quem leva a `PARA-VALIDAR.md` ao especialista |
| `fonte_enviada` | Está na mesa do especialista | **Especialista** |
| `fonte_aprovada` | Especialista e direitos registrados; pode ser candidata à indexação | **Agente de ingestão** |
| `indexada` | Está no ChromaDB e a régua já mediu | — |

Nada pula etapa. Em particular: **arquivo em `capturas/` não é documento da
base.** A cópia para `backend/data/documents/` acontece uma vez, depois da
aprovação, e é do agente de ingestão. O agente não concede essa aprovação:
apenas confere se ela já foi registrada. O pesquisador só copia temporariamente
para rodar `--inspect`, e apaga em seguida.

## Como uma fonte é capturada

Sempre pelo script, nunca à mão:

```bash
python scripts/capturar_fonte.py <url> --topic <id do mapa> --slug <apelido> \
    --title "Titulo curto" --source "Instituicao" \
    --document-type owner_guidance --species dog --language en --register tutor
```

O script baixa a página, extrai o texto principal (sem menu, rodapé nem
banner de cookie), grava UTF-8 e calcula o hash. **O que o especialista
aprova é esse arquivo**, com data e hash — não a URL, que pode mudar amanhã.

A diferença importa: quando um agente "lê" uma página, o que ele devolve é o
que entendeu dela. Indexar isso faria a base ser paráfrase, que é o oposto da
decisão de usar fontes originais. O agente lê para julgar; o script captura
para guardar.

## As seções, e a armadilha que elas escondem

Uma fonte raramente entra inteira. A ficha declara, em
`indexing.include_sections`, quais seções são indexadas — tipicamente sinais
e orientação de urgência. **Tratamento, cirurgia e dose ficam de fora de
propósito:** o sistema orienta a procurar atendimento, não a tratar em casa.

Duas regras que o piloto de 12/09 custou a aprender:

1. **Declare o nome exato do arquivo capturado**, acento por acento. O
   ingestor compara sem normalizar acentos, e uma seção declarada com nome
   ligeiramente diferente é ignorada **em silêncio**.
2. **Declare também as seções que você quer excluir.** O ingestor só enxerga
   um heading que a ficha declarou; se você listar só o que quer incluir, a
   seção desejada engole o resto do documento. No piloto, o artigo do SciELO
   produziu 217 trechos de fisiopatologia e cirurgia; com os 15 headings
   seguintes declarados em `exclude_sections`, caiu para 29.

Confira sempre com `--inspect` antes de dar por pronto — ele mostra as seções
detectadas, as indexadas e o número de trechos, e não escreve nada no banco.

## O que os especialistas recebem

`PARA-VALIDAR.md`, com uma linha por fonte e uma pergunta só: **serve como
referência para este quadro, para um tutor brasileiro?** Respostas: sim, não,
ou com ressalva escrita. O detalhe — as citações que sustentam cada
julgamento — está no dossiê do quadro, para quem quiser conferir.

O veredito vai para três lugares: `validation_status` e `specialist` na
ficha, e a coluna `validacao` da linha no mapa.

## Estado

| Quadro | Estado | Dossiê |
|---|---|---|
| Torção gástrica | `fonte_encontrada` — 2 capturas, aguardando validação | [gastric_dilatation_volvulus.md](gastric_dilatation_volvulus.md) |
| Medicamento humano | `fonte_aprovada` — ASAVET, ainda restrita ao perfil experimental | [human_medication_poisoning.md](human_medication_poisoning.md) |
| Carbamato/organofosforado | `fonte_aprovada` — ASAVET, ainda restrita ao perfil experimental | [carbamate_organophosphate_poisoning.md](carbamate_organophosphate_poisoning.md) |
| Permetrina em gato | `fonte_aprovada` — ASAVET, ainda restrita ao perfil experimental | [permethrin_toxicosis_cats.md](permethrin_toxicosis_cats.md) |
| Raticida anticoagulante | `fonte_aprovada` — ASAVET, ainda restrita ao perfil experimental | [anticoagulant_rodenticide_poisoning.md](anticoagulant_rodenticide_poisoning.md) |
| Parvovirose/panleucopenia | `fonte_aprovada` — ASAVET; captura canina e lacuna felina | [parvovirus_panleukopenia.md](parvovirus_panleukopenia.md) |
| Piometra | `fonte_aprovada` — ASAVET, 2 capturas ainda experimentais | [pyometra.md](pyometra.md) |
| Neonato que não mama | `fonte_aprovada` — ASAVET, ainda restrita ao perfil experimental | [fading_neonate.md](fading_neonate.md) |
| Paralisia aguda dos membros traseiros | `fonte_aprovada` — ASAVET, cão e gato, ainda experimental | [acute_hindlimb_paralysis.md](acute_hindlimb_paralysis.md) |
| Anafilaxia e inchaço facial | `fonte_aprovada` — ASAVET, ainda restrita ao perfil experimental | [anaphylaxis_facial_swelling.md](anaphylaxis_facial_swelling.md) |

As demais linhas da etapa 1 seguem no estado verdadeiro registrado no mapa.
A fila e a porta de decisão estão no [README da curadoria](../README.md).
