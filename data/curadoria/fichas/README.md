# Fichas de busca (rascunho, aguardando certificação)

As 61 fichas de busca da arquitetura da autópsia 2, uma por linha do mapa de
assuntos (`<topic>.json`), escritas em 24/09 por um modelo de IA (Claude, seis
instâncias em paralelo) a partir do texto completo dos documentos aprovados de
cada assunto e da linha do mapa. **Estado: rascunho.** Os itens que não vêm do
mapa aguardam a certificação dos especialistas (`CERTIFICACAO.md`).

## Duas camadas

- **Ficha de busca (esta pasta).** O texto que a busca compara com o relato do
  tutor, feito para casar com o jeito como o tutor conta: 6 a 12 frases
  coloquiais, com variações, mais sinais de alarme, como diferenciar da gêmea e
  por que importa.
- **Ficha de leitura.** O texto que o atendente lê: a ficha curta do mapa, com as
  colunas validadas e a conduta fixa pela urgência. Ela é gerada a partir do mapa
  (`data/curadoria/mapa-de-assuntos.csv`), não daqui.

Separar as duas foi o resultado da
[rodada 19](../../../evidencias/joao/2026-09-24-20-fichas-em-duas-camadas.md). A
ficha de busca ajuda a busca (nos relatos de quem não viu o mapa, a ficha certa
em 1º lugar vai de 52% para 61%), mas lida inteira pelo atendente pequeno ela
piora a decisão. O texto escrito pela IA serve só para achar a ficha e nunca é
lido como orientação clínica.

## O formato de cada `<topic>.json`

`topico` (o `id` da linha do mapa), `titulo`, `nome_leigo`, `especie`, as listas
`como_o_tutor_conta`, `sinais_de_alarme`, `como_diferenciar` e `por_que_importa`, e
`notas_para_o_especialista` (o que o autor quis deixar anotado, como os conflitos
com o mapa). Cada item das listas tem:

| Campo | O que é |
|---|---|
| `texto` | a frase |
| `origem` | `mapa` (a linha validada do mapa), `documento` (tirada de um documento aprovado) ou `geral` (conhecimento veterinário geral, **para o especialista validar**) |
| `trecho` | nos itens de documento, o trecho literal (até 40 palavras) que sustenta a frase |
| `fonte` | nos itens de documento, o arquivo em `backend/data/documents/` |

`conferencia.json` tem, por ficha, o resultado da conferência automática: dos
461 itens de documento, 457 têm o trecho achado literalmente e 3 de forma
aproximada; 1 ficou de fora por não ter trecho. 124 trechos só existem no texto
completo, e não no indexado. Os sinais do mapa estão todos cobertos, com 2
inseridos pelo montador como estão no mapa.

**A conduta nunca é escrita pela IA.** Ela é fixa pela urgência do mapa e entra
na montagem.

## Regras que os autores seguiram

Proibido: remédio, dose, tratamento, cuidado caseiro, decidir a urgência, sinal
de outra espécie, achado de exame como sinal do tutor. Os autores não viram
nenhum caso de teste (prova, régua, relatos independentes).

## A certificação

`CERTIFICACAO.md` junta, por ficha, os 513 itens que não vêm do mapa
(documento, com o trecho, e `geral`), os conflitos que os autores anotaram entre
o mapa e o documento, e as notas deles. A etapa 2 soma 274 itens de documento e
48 `geral`, cerca de 2 horas. O que os especialistas aprovarem na etapa 2 vira o
conteúdo das duas colunas vazias do mapa (sinais que o tutor relata e
discriminador), e portanto também da ficha de leitura. O acompanhamento está no
[B-61](../../../evidencias/backlog.md#b-61).
