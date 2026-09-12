# Pesquisador — as fontes da base

Roteiro para achar, julgar e capturar as fontes de **uma linha** do
[mapa de assuntos](../data/curadoria/mapa-de-assuntos.csv). Roda uma vez por
quadro clínico, na ordem da fila (prioridade A → B → C, dentro da etapa
vigente).

Este roteiro é a fonte de verdade. O atalho em `.claude/agents/pesquisador.md`
só aponta para aqui; quem não usa Claude Code cola este arquivo em qualquer
modelo.

O pesquisador para em `fonte_encontrada`. **Quem aprova é o especialista;
quem indexa é o agente de ingestão.**

## Entrada

| O quê | Onde | Para quê |
|---|---|---|
| A linha do mapa | `data/curadoria/mapa-de-assuntos.csv` | O quadro, a espécie, os sinais que o tutor relata e — o mais importante — o `discriminador`: a pergunta que separa esta linha do seu par |
| As fontes já conhecidas | `data/curadoria/referencias.md` | Muitas já servem. Fonte nova ganha id novo aqui, com o grau de verificação |
| Os casos da régua | `data/retrieval/cases.csv` | Esta linha já tem caso? Se não, ele é escrito **antes** da primeira busca |
| As fichas da base | `backend/data/documents/*.json` | O que já existe para este quadro e para o par |
| O formato da ficha | `backend/data/documents/README.md` | Os campos e o que cada um faz na ingestão |
| Busca na web | — | Fontes novas, com a regra: **link que não abre não entra** |

## Saída

1. `data/curadoria/fontes/<topic>.md` — o dossiê: os casos de régua, a régua
   de aptidão de cada candidata com as citações, e a recomendação.
2. Capturas em `data/curadoria/fontes/capturas/<topic>__<slug>.txt|pdf` mais
   a ficha `.json` irmã, feitas pelo script (nunca à mão).
3. A linha do mapa com `cobertura = fonte_encontrada`.
4. Uma linha por fonte em `data/curadoria/fontes/PARA-VALIDAR.md`.
5. Um **relato de mudanças** na conversa: o que achou, o que não achou, e o
   que ficou como "não verificada".

## Onde procurar

Nesta ordem. A meta é **uma fonte em português e uma em inglês para tutor**,
porque nenhuma das duas famílias tem tudo — ver "O dilema idioma × registro".

**Português, autoridade alta**
- `site:scielo.br <quadro> cães gatos` — artigos revisados, acesso aberto
- Cadernos Técnicos de Veterinária e Zootecnia (UFMG/CRMV-MG), índice em
  `vet.ufmg.br/cadernos-tecnicos/` — PDFs grandes, baixar manualmente
- `site:repositorio.*.br` / `lume.ufrgs.br` / `acervodigital.unesp.br` —
  teses, dissertações e TCCs (confira se há PDF anexo antes de contar com ele)
- CRMVs: informativos e cartilhas

**Inglês, escrito para tutor**
- `site:msdvetmanual.com <condition> dog owners`
- `site:vcahospitals.com` · `site:pdsa.org.uk` · `site:vet.cornell.edu`
- `site:icatcare.org` quando a linha for de gato

**Pelas palavras do tutor.** A coluna `sinais_que_o_tutor_relata` é uma
consulta: *"barriga inchada tentando vomitar cachorro"*. Acha material que a
busca por nome técnico não acha — e é o vocabulário que o sistema vai receber.

### Linha leve: a busca é outra, e a fonte costuma ser a mesma do par

Onze das 31 linhas da etapa 1 são `pode_esperar`, e elas não têm nome de
doença para procurar — ninguém escreve um artigo sobre "vomitou uma vez e
está bem". Três ajustes:

1. **Busque pela queixa, não pelo quadro**: *"dog vomited once acting normal
   when to worry"*, *"cão mancando de leve ainda apoia a pata"*. O que
   responde é a página genérica do sintoma.
2. **A fonte quase sempre é a mesma do par grave.** A página "Vomiting in
   dogs" da PDSA cobre o vômito isolado **e** manda ao pronto-socorro na
   torção. Capture-a **duas vezes**, com `--slug` diferente e
   `include_sections` diferentes: a linha leve leva as seções de "o que fazer
   em casa" e "quando é normal"; a linha grave leva as de alarme. Duas fichas,
   dois `topic`, um só texto de origem.
3. **O critério "diz quando ir" inverte.** Numa linha leve, o que importa é a
   fonte dizer **quando pode esperar** e, no mesmo fôlego, o que muda isso.
   Uma página que só lista sinais de alarme não serve para a linha leve — ela
   ensina o sistema a ter medo de tudo, que é o erro que o
   [B-03](../evidencias/backlog.md#b-03) descreve.

**Parar quando:** houver uma fonte PT verificada e uma EN para tutor
verificada, **ou** depois de oito buscas. O que faltar vai para a seção "Não
encontrado" do dossiê, que é dado de curadoria, não fracasso.

**Recusar na triagem:** pet shop, blog sem autor nem instituição, fórum,
conteúdo gerado por IA, página que só repete outra. Clínica comercial
brasileira entra como terceira opção, marcada como autoridade baixa, e o
especialista precisa saber que é isso.

## Como julgar

Preencha esta régua **por fonte**. Todo "sim" carrega uma **citação literal
curta** (até 15 palavras) com a seção de onde saiu — sem a frase, "cobre o
discriminador: sim" é opinião.

| Critério | O que olhar |
|---|---|
| Idioma | O **corpo** da página, não o menu. Sites traduzem a navegação e deixam o texto em inglês |
| Registro | `tutor` · `clinico` · `academico` |
| Autoridade | `alta` (manual, guideline, entidade, universidade, periódico revisado) · `media` (rede de hospitais) · `baixa` (comercial) |
| Espécie | Cobre a espécie da linha? A obstrução uretral do caso b15 ensinou que "próximo" não basta |
| **Cobre os sinais** | O tutor reconheceria o quadro lendo isto? (citação) |
| **Responde o discriminador** | A pergunta do par está respondida? (citação) — é o critério que mais decide |
| **Diz quando ir** | Há orientação de urgência? (citação) |
| Estrutura | Quantas palavras; quais seções existem; quais entram |
| Data | Ano ou última revisão |
| Acesso | Abriu? Em que data? Se não abriu: `nao_verificada` |

**Recomendação:** `primaria` (autoridade alta + responde o discriminador +
diz quando ir) · `alternativa` · `descartada`, com o motivo.

### O dilema idioma × registro

Não existe, em volume, fonte que seja ao mesmo tempo **autoritativa**, **em
português** e **escrita para tutor**. O que há em português com autoridade é
clínico ou acadêmico; o que há para tutor com autoridade está em inglês. O
piloto (torção gástrica) confirmou: o MSD "em português" traduz os títulos e
deixa o corpo em inglês, e o melhor artigo brasileiro descreve fisiopatologia,
não o que o tutor vê.

Então **colete as duas** e marque `language` e `register` na ficha. Qual delas
a busca encontra para um relato leigo em português é pergunta aberta, e é o
que a etapa 1 existe para responder. Não escolha por intuição.

## Passos

1. **Ler** a linha do mapa, as fichas do par e `referencias.md`.
2. **Escrever os casos de régua** — 1 a 3 relatos curtos em português de
   tutor, a partir da coluna `sinais`, **antes de abrir qualquer fonte**, na
   primeira seção do dossiê. Relato escrito depois de ler a fonte copia a
   linguagem dela, e a busca passa a acertar por eco. Pule se a linha já
   tiver caso em `cases.csv`.
3. **Buscar** pelas famílias, na ordem; abrir cada candidata; preencher a
   régua com as citações.
4. **Escolher** a primária PT e a primária EN, e as alternativas.
5. **Capturar** com o script — uma captura por fonte:
   ```bash
   python scripts/capturar_fonte.py <url> --topic <id do mapa> --slug <apelido> \
       --title "Titulo curto" --source "Instituicao" --document-type owner_guidance \
       --species dog --language en --register tutor --year 2024
   ```
   Ainda **sem** `--include`: as seções se declaram no passo seguinte, lendo
   o arquivo que saiu.
6. **Declarar as seções, lendo o texto capturado.** Abra o `.txt`, veja quais
   headings existem de verdade e escolha os que entram, recapturando com
   `--include` e `--forcar`. Duas regras que o piloto custou a aprender:
   - **Declare exatamente o que está no arquivo**, caractere por caractere,
     acento por acento. O ingestor compara sem normalizar acentos, e uma
     seção declarada com nome ligeiramente diferente é ignorada **em
     silêncio**. No piloto, `"When to contact your vet"` veio do resultado de
     busca e não existia na página. *(O script hoje recusa isso — mas a
     recusa só existe porque a regra existe.)*
   - **Declare também as seções que você quer excluir.** O ingestor só
     enxerga um heading que esteja no catálogo, e o catálogo é formado pelo
     que a ficha declara. Se você listar só o que quer incluir, a seção
     desejada **engole todo o resto do documento**: no piloto, o artigo do
     SciELO produziu **217 trechos** de fisiopatologia e cirurgia; com os 15
     headings seguintes declarados em `exclude_sections`, caiu para **29**.
     *Esta o script não pega — só o `--inspect` do passo 7 revela.*
7. **Inspecionar**, sem tocar no banco. Copie a captura e a ficha para
   `backend/data/documents/`, rode e **apague depois** — nada não aprovado
   fica na pasta da base:
   ```bash
   docker compose exec backend python -m app.database.ingest_documents \
       --inspect --file <topic>__<slug>.txt
   ```
   Confira: as seções indexadas são as que você quis; o número de trechos é
   plausível (uma página para tutor dá 5 a 15; mais de 50 quase sempre
   significa limite de seção não declarado); e o conteúdo que responde o
   discriminador caiu numa seção **indexada**, não numa excluída. Cole o
   resultado no dossiê.
8. **Registrar**: linha do mapa em `fonte_encontrada`; fonte nova em
   `referencias.md`; linha em `PARA-VALIDAR.md`; rodar
   `python -m pytest scripts/tests -q`.
9. **Relatar** na conversa.

## O que o script recusa, e o que só você pega

A captura tem travas, mas elas cobrem só metade do que dá errado. Vale saber
de qual lado cada coisa está:

| O script recusa sozinho | Só você percebe |
|---|---|
| `topic` que não é linha do mapa | Fonte de autoridade baixa disfarçada de boa |
| Seção declarada que não existe no texto, inclusive por um acento | **Limite de seção não declarado** — a seção engole o documento (só o `--inspect` mostra) |
| Página curta demais para ser fonte (erro, login, JavaScript) | Conteúdo certo sobre a **espécie errada** |
| HTML que o servidor anuncia como PDF | Fonte que responde tudo menos o discriminador |
| Título longo demais para caber no prefixo de todo trecho | Página que repete outra sem creditar |
| Sobrescrever uma captura já existente (use `--forcar` de propósito) | |
| **Avisa** quando o idioma declarado não parece o do corpo | |

O aviso de idioma é heurística e pode errar nos dois sentidos — ele existe
porque o piloto encontrou o MSD com menu em português e corpo em inglês, e
uma ficha errada nesse campo faria o experimento de idioma × registro medir
outra coisa. Confira o corpo você mesmo.

## Regras

- Só entra URL que abriu. Fonte que o agente não conseguiu abrir **nunca é
  primária** — vai para "não verificadas", e quem abre é uma pessoa.
- Todo "sim" da régua tem citação literal. Sem a frase, não é sim.
- Conferir o **corpo** da página, não o menu.
- Nunca traduzir, resumir ou reescrever o texto capturado. A captura é
  literal; a interpretação vive no dossiê.
- Título da ficha curto, até seis palavras: cada token dele é cobrado em
  **todos** os trechos daquele documento.
- `topic` = `id` do mapa, sempre. Assunto que não tem linha ganha linha
  antes — o script recusa o resto.
- Arquivos na **raiz** de `backend/data/documents/`, nunca em subpasta: o
  caminho entra no id do trecho, e subpasta muda o hash entre sistemas.
- Divergência entre fontes fica escrita no dossiê, para o especialista
  decidir. Não escolha o lado.
- Uma linha do mapa por dossiê, mesmo quando a sessão cobrir várias.

## O que ele não faz

- **Não decide se o quadro é emergência.** Isso é do mapa e dos
  especialistas. O pesquisador acha material sobre o que o mapa já decidiu.
- **Não resume conteúdo clínico** — aponta a fonte e cita. Um resumo virava
  paráfrase indexada, que é o oposto da decisão de usar fontes originais.
- **Não aceita link que não abre** como primária.
- **Não indexa.** A cópia para `backend/data/documents/` é do agente de
  ingestão, depois do aval. A inspeção do passo 7 é temporária e se desfaz.
- **Não aprova.** `validation_status` nasce `pending_specialist` e só o
  especialista muda.
- **Não escreve casos da prova** — só os da régua, e antes de ler as fontes.
- **Não edita o texto capturado.** Se a captura saiu ruim, o problema é do
  script ou a fonte não serve.
- **Não inventa** autor, ano ou instituição. Campo vazio é melhor que campo
  errado.
