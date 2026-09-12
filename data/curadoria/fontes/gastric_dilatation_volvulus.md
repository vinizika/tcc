# Torção gástrica — fontes

**Linha do mapa:** `gastric_dilatation_volvulus` · cão · emergência ·
imediato · prioridade A · etapa 1
**Discriminador:** *Sai alguma coisa quando tenta vomitar, e a barriga está
estufada e dura?*
**Par de confusão:** `single_vomiting_or_mild_diarrhea`
**Pesquisado em:** 12/09/2026, pelo [roteiro do pesquisador](../../../agentes/pesquisador.md)
**Estado:** `fonte_encontrada` — duas capturas esperando validação

> **Recapturado em 12/09.** O piloto da linha leve mostrou que a extração
> deixava a indentação do markdown no texto, e um heading indentado não bate
> com o nome declarado na ficha. A correção mudou o hash das duas capturas; o
> conteúdo é o mesmo, e os hashes atuais estão nas fichas `.json`.

## Casos da régua

A linha **já tem caso**: `b12` em [`data/retrieval/cases.csv`](../../retrieval/cases.csv),
marcado hoje como "sem cobertura" justamente porque nenhum documento da base
trata do quadro.

> meu cachorro grande está com a barriga muito inchada e dura tentando
> vomitar sem sair nada e muito inquieto

**Quando esta linha for indexada, o b12 precisa deixar de ser "sem cobertura"
e virar "com protocolo", com `expected_topics = gastric_dilatation_volvulus`.**
Sem isso a régua continua premiando o silêncio num caso que agora tem
resposta. O `compare` do agente de ingestão avisa ([B-51](../../../evidencias/backlog.md#b-51)).

Nenhum caso novo foi escrito — e nenhuma fonte foi aberta antes de conferir
isso, para o relato não copiar a linguagem do documento.

## As candidatas

### 1. PDSA — GDV (Gastric Dilatation Volvulus) in dogs · **primária (EN, tutor)**

<https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/gdv-gastric-dilatation-volvulus-in-dogs>

| Critério | Valor | Citação |
|---|---|---|
| Idioma | en | corpo em inglês, conferido |
| Registro | tutor | — |
| Autoridade | alta | ONG veterinária britânica, hospitais próprios |
| Espécie | sim | cão |
| **Cobre os sinais** | **sim** | "Retching or unproductive vomiting (when they bring up a nothing or a small amount of foam)" — seção *GDV Symptoms* |
| **Responde o discriminador** | **sim** | "Bloat (swollen tummy) – this is not always obvious as your dog's tummy might be tucked up under their ribcage" — *GDV Symptoms* |
| **Diz quando ir** | **sim** | "Contact your vet straight away if your dog has symptoms of a GDV, it's a life threatening condition" — *Overview* |
| Estrutura | boa | 1.189 palavras; headings curtos; listas |
| Data | jun/2024 | "Published: June 2024" |
| Acesso | 12/09/2026 | ✅ |

**Seções que entram:** `Overview`, `What is GDV?`, `Which dogs are most at
risk of GDV?`, `GDV Symptoms`.
**Ficam de fora:** `Treatment`, `After surgery care`, `Outlook`,
`Preventing GDV`, `Cost` — o sistema não prescreve, e conduta cirúrgica no
prompt só competiria com o que decide a triagem.

**Inspeção** (`--inspect`, sem tocar no banco): 6 seções detectadas, **4
indexadas**, `Front matter` e `Treatment` excluídas; **9 trechos**, de 46 a
116 tokens. As três citações acima caíram em seções indexadas — conferido.

### 2. Ciência Rural — Síndrome da dilatação volvo gástrica em cães · **complementar (PT, acadêmico)**

<https://www.scielo.br/j/cr/a/CPzTSK3tQkWxFSz7Q3L3zLv/?lang=pt> ·
Silva SSR, Castro JLC, Castro VSP, Raiser AG · 2012 · 42(1) ·
DOI [10.1590/S0103-84782012000100020](https://doi.org/10.1590/S0103-84782012000100020) ·
acesso aberto, CC BY-NC

| Critério | Valor | Citação |
|---|---|---|
| Idioma | **pt** | "A síndrome da dilatação volvo gástrica (DVG) é uma condição grave, de caráter agudo" |
| Registro | academico | — |
| Autoridade | alta | periódico revisado por pares |
| Espécie | sim | cão |
| **Cobre os sinais** | **parcial** | cita "taquicardia, taquipneia, pulsos hipocinéticos rápidos" — sinais de exame, não o que o tutor vê |
| **Responde o discriminador** | **não** | não distingue vômito improdutivo de vômito comum |
| **Diz quando ir** | parcial | "A rápida identificação, escolha da terapia adequada e estabilização precoce do paciente são os principais componentes de sucesso" |
| Estrutura | ruim para triagem | 5.745 palavras; 16 seções, quase todas de fisiopatologia e cirurgia |
| Data | 2012 | — |
| Acesso | 12/09/2026 | ✅ |

**Seções que entram:** só `Síndrome da dilatação volvo gástrica` — a que traz
a definição, os fatores de risco (tórax profundo) e o diferencial com
"timpanismo alimentar".
**Ficam de fora:** as 15 seguintes, de `Fisiopatologia gástrica` a
`Lesão à mucosa gástrica e perfuração`.

**Inspeção:** com só a seção desejada declarada, o documento produziu **217
trechos** — a seção engoliu o artigo inteiro, porque o ingestor não enxerga um
heading que a ficha não declarou. Declarando as 15 seguintes em
`exclude_sections`, caiu para **29**. É a lição que virou regra no passo 6 do
roteiro.

**Por que entra mesmo sendo fraca para triagem:** é a melhor fonte em
**português** que existe para este quadro, e é ela que torna possível
perguntar, na etapa 1, se a busca prefere a língua do relato ou o registro de
quem escreve para tutor. Se a régua mostrar que ela nunca é recuperada para o
b12, ela sai — e isso já é resposta.

### Alternativas verificadas

- **VCA — Bloat: Gastric Dilatation and Volvulus in Dogs**
  <https://vcahospitals.com/know-your-pet/bloat-gastric-dilatation-and-volvulus-in-dogs>
  EN, tutor, autoridade alta. "Immediate veterinary attention (within minutes
  to a few hours) is required". Substitui a PDSA se o especialista preferir.
- **Cornell Riney — Gastric dilatation volvulus (GDV) or "bloat"**
  <https://www.vet.cornell.edu/departments-centers-and-institutes/riney-canine-health-center/canine-health-topics/gastric-dilatation-volvulus-gdv-or-bloat>
  EN, tutor, universidade. Terceira opção.

### Descartadas

| Fonte | Motivo |
|---|---|
| MSD Manual Veterinário, versão PT, "Dilatação gástrica e vólvulo em animais de pequeno porte" | **Títulos em português, corpo em inglês.** Não serve como fonte em PT; como fonte em EN é profissional, com tratamento e dosagem — pior que a PDSA para triagem |
| UNESP, TCC 2010, "Síndrome dilatação-vólvulo gástrico em cães" | "There are no files associated with this item" — sem PDF |
| UFRGS/Lume, revisão de literatura | Erro de certificado na leitura automatizada — **não verificada**; vale alguém abrir no navegador |
| VET Profissional, Animalcare.pt, revistas de baixo rigor editorial | Autoridade baixa ou comercial, com fontes melhores disponíveis |

## Não encontrado

- **Fonte em português, com autoridade, escrita para tutor.** Procurei em
  CRMVs, hospitais veterinários universitários e manuais traduzidos. O que
  existe em PT para tutor é de clínica comercial. É a lacuna que o
  [redator de lacuna](../../../agentes/README.md) existe para cobrir, se o
  time decidir.
- **Caderno Técnico UFMG nº 87 (Emergência em Medicina Veterinária)** — a URL
  existe (`vet.ufmg.br/ARQUIVOS/FCK/file/editora/cteletronico 87 …`), mas o
  PDF passa de 10 MB e não abriu na leitura automatizada. É a melhor
  candidata institucional brasileira e vale baixar à mão.

## Para o especialista

Duas perguntas, uma por fonte, em `PARA-VALIDAR.md`. A segunda é a que
importa: **uma revisão acadêmica de 2012, da qual indexaríamos só a seção de
definição e fatores de risco, serve como referência para este quadro no
Brasil — ou é melhor não ter fonte em português do que ter essa?**
