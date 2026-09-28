# Corpo estranho gastrointestinal — fontes

**Linha do mapa:** `gastrointestinal_foreign_body` · cão e gato · emergência

**Caso da régua:** `b30`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 19/09/2026

## Fonte experimental

Kneissl et al. · Frontiers in Veterinary Science · 2025 · DOI
`10.3389/fvets.2025.1562792` · CC BY 4.0. PDF integral preservado com SHA-256
`8ca9de24e96f8fdb8549f3e0f2f970937e0c86491f0eb9f2eb5f911b16adf518`.

A inspeção das páginas selecionadas produziu 56 chunks de 46–96 tokens, com
introdução, métodos, resultados e discussão. Cinco avisos de glifos Unicode e
dois fallbacks de frases longas foram registrados.

## Limitações

É um artigo de imagem diagnóstica, não uma orientação para tutores. A classe e
o prazo do mapa continuam hipóteses pendentes de avaliação clínica.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador B) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

Agente B, rodada N6, acesso em 25/09/2026. Tarefa: achar fonte para 6 frases
já escritas da ficha de busca (4 do tutor, 2 de alarme). Casos de régua: fora
do escopo desta tarefa.

#### Candidatas capturadas

##### 1. ACVS — *Gastrointestinal Foreign Bodies*
`gastrointestinal_foreign_body__acvs_gi_fb.txt` ·
https://www.acvs.org/small-animal/gastrointestinal-foreign-bodies

| Critério | Resultado |
|---|---|
| Idioma | en (corpo) |
| Registro | tutor (página do colégio de cirurgiões para donos, com uma parte longa de cirurgia) |
| Autoridade | alta (American College of Veterinary Surgeons) |
| Espécie | cão e gato ("pets") |
| Cobre os sinais | sim: "a string may be observed wrapped around the base of the tongue" (sinais clínicos) |
| Diz quando ir | não, para o quadro inicial. Só no pós-operatório: "your pet should be re-evaluated as soon as possible" |
| Estrutura | 1101 palavras, **sem nenhum heading** (tudo ou nada na indexação); mais da metade é diagnóstico, cirurgia e complicações |
| Data | publicada em 16/05/2023, modificada em 31/03/2026 |
| Direitos | © 2026 American College of Veterinary Surgeons |
| Acesso | abriu, 25/09/2026 |

##### 2. MedVet — *Gastrointestinal Foreign Bodies in Cats and Dogs*
`gastrointestinal_foreign_body__medvet_gi_fb.txt` ·
https://www.medvet.com/gastrointestinal-foreign-bodies-in-cats-and-dogs/

| Critério | Resultado |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | média (rede de hospitais de especialidade; autor Karl C. Maritato, DVM, DACVS) |
| Espécie | cão e gato, com parágrafos separados para cada um |
| Cobre os sinais | sim: "a distended abdomen in addition to vomiting" (Signs of Foreign Objects in Pets) |
| Diz quando ir | sim: "it is essential to contact your veterinarian immediately" (Diagnosis of Foreign Objects in Pets) |
| Estrutura | 1510 palavras; seções: Common Foreign Objects…, Signs…, Diagnosis…, Treatment Options… (Endoscopy, Surgical Interventions), When is Surgery Necessary…, Risks of Surgery, Post-Surgical Care. Entram as duas primeiras; o resto é conduta |
| Data | 27/08/2025 |
| Direitos | não declara |
| Acesso | abriu, 25/09/2026 |

#### Frase por frase

| Frase | Status | Fonte | Trecho (literal) |
|---|---|---|---|
| tutor#2 Engoliu meia, brinquedo, tampinha, caroço ou osso. | parcial | MedVet (+ACVS) | "Common foreign objects found in dogs include socks, underwear, toys, bones, and even more unusual items like knives." Tampinha e caroço não aparecem |
| tutor#3 Vomita toda vez que come ou bebe água. | parcial | MedVet | "…the pet may regurgitate or vomit frequently, and the vomit may contain foreign objects or undigested food." Não liga o vômito a cada refeição ou gole |
| tutor#6 A barriga tá dolorida, reclama quando encosto. | sustentada | MedVet | "They also typically have abdominal pain when they are palpated." |
| tutor#7 Tem um fio saindo da boca ou pelo bumbum. | sustentada | ACVS | "…a string may be observed wrapped around the base of the tongue (Figure 2) or coming out of the anus." |
| alarme#1 Barriga inchada ou muito dolorida. | sustentada | MedVet | "…more severe signs, such as dehydration, shock, and a distended abdomen in addition to vomiting." |
| alarme#2 Muito fraco e prostrado. | parcial | MedVet (+ACVS) | "Common signs include … abdominal pain, and lethargy." A ACVS fala de animal "profoundly ill and in critical condition" quando há perfuração |

#### Recomendação

- **MedVet: primária para estas frases.** Cobre as duas espécies, diz quando
  ir e tem seções que dá para declarar. Mas é autoridade **média**, e o
  especialista precisa saber disso.
- **ACVS: alternativa.** Autoridade alta, e é a única que traz o fio saindo do
  ânus. Contra: sem heading nenhum (a parte de cirurgia entraria inteira na
  indexação) e sem orientação de quando ir.
- **Descartadas** (abertas, não capturadas): PDSA *Gut blockage in dogs*
  (alta, mas só cão, sem fio nem barriga inchada; é a única com "yelping or
  growling when you touch their tummy", o jeito do tutor contar a frase
  tutor#6); PDSA *Bowel obstruction in cats* (só gato: "A string hanging from
  their mouth (never pull it)"); Cornell Riney *GI foreign body obstruction
  in dogs* (só cão, lista de sinais sem nada que as outras não tenham); VCA
  *Ingestion of Foreign Bodies in Dogs* (só cão).

#### Não encontrado

- **"Tampinha" e "caroço"**: nenhuma fonte de autoridade aberta cita tampinha
  de garrafa nem caroço de fruta. "Fruit pits" só apareceu em blogs de
  clínica comercial.
- **"Vomita toda vez que come ou bebe água"**: o padrão ligado à refeição ou
  à água só apareceu em blogs de clínica comercial (recusados). As fontes
  boas dizem só "vomiting" ou "vomit frequently".
- **Fonte em português para tutor com autoridade**: não achei. A busca em
  português trouxe relatos de caso e blogs.
