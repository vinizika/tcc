# Bebe e urina mais que o normal — fontes

**Linha do mapa:** `polyuria_polydipsia_investigate`

**Caso da régua:** `b56`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R89 · Arginine vasopressin and copeptin: comparative review and perspective in veterinary medicine · Frontiers in Veterinary Science · 2025. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`1dc6a723fb06371b7cf6fd7075dd67d3b2398b019935a7c6241e5ea8a10d4ec4`.

A inspeção individual do recorte produziu **51 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Cobre causas e investigação de PUPD; não estabelece sozinho a urgência de atendimento.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador B) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

Agente B, rodada N6, acesso em 25/09/2026. Duas frases do tutor. Casos de
régua: fora do escopo desta tarefa.

#### Candidatas capturadas

##### 1. PDSA — *Why is my dog drinking lots of water and weeing more than usual?*
`polyuria_polydipsia_investigate__pdsa_dog_drinking_weeing.txt` ·
https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/is-my-dog-drinking-and-weeing-too-much

| Critério | Resultado |
|---|---|
| Idioma | en |
| Registro | tutor (página de **sintoma**, que é o que serve a esta linha) |
| Autoridade | alta (PDSA; "Written by vets and vet nurses") |
| Espécie | só cão (a PDSA tem a página irmã para gato, *Is my cat drinking and weeing too much?*, aberta e não capturada) |
| Cobre os sinais | sim: "Weeing in the house during the day or overnight despite being previously house trained." (lista inicial) |
| Diz quando ir | sim, e no tom da linha (consulta, não emergência): "If this is the case, contact your vet for an appointment." |
| Estrutura | 878 palavras; Overview, a lista "Have you noticed your dog", Causes (inclui piometra, a gêmea de alarme), Cost, e duas perguntas: termos médicos (PUPD) e quanto um cão deve beber. Mais o rodapé padrão da PDSA |
| Data | julho de 2024 |
| Direitos | © The People's Dispensary for Sick Animals; "This advice is for UK pets only" |
| Acesso | abriu, 25/09/2026 |

##### 2. Cornell Feline Health Center — *Feline Diabetes*
`polyuria_polydipsia_investigate__cornell_feline_diabetes.txt` ·
https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/feline-diabetes

| Critério | Resultado |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (Cornell University College of Veterinary Medicine) |
| Espécie | só gato |
| Cobre os sinais | sim: "weight loss despite a good appetite and increased thirst and urination" (Clinical Signs) |
| Diz quando ir | não, para os sinais iniciais. Só nas complicações: "Ketoacidosis is considered a medical emergency" |
| Estrutura | 2210 palavras; What is Diabetes?, Risk Factors, Clinical Signs, Diagnosis, Treatment, Insulin Therapy, Dietary Therapy, Oral Medications (esses três headings aparecem duas vezes no texto), Monitoring, Prognosis and Remission, Possible Complications, Monitoring Your Cat At Home. **Atenção:** Possible Complications tem cuidado caseiro para hipoglicemia (mel, xarope de milho), que a ficha não pode usar. Declarar como excluída na ingestão |
| Data | "Updated 2024" |
| Direitos | Cornell University ©2026 |
| Acesso | abriu, 25/09/2026 |

#### Frase por frase

| Frase | Status | Trecho (literal) |
|---|---|---|
| tutor#5 Começou a fazer xixi pela casa ou pede pra sair de madrugada | parcial | PDSA: "Weeing in the house during the day or overnight despite being previously house trained." A metade "começou a fazer xixi pela casa" está literal, e a madrugada aparece como "overnight". O "pede pra sair" não está |
| tutor#6 Bebe muita água e tá emagrecendo, mesmo comendo | sustentada | Cornell: "The two most common signs of diabetes noticed by owners at home are weight loss despite a good appetite and increased thirst and urination." |

#### Recomendação

- **PDSA (cão): primária.** É página de sintoma, que é a certa para esta
  linha: diz quando marcar consulta e lista as causas, piometra entre elas.
- **Cornell (gato): alternativa, para a frase do emagrecimento.** Página de
  condição (diabetes), não de sintoma. Para o cão, dizem o mesmo e não foram
  capturadas pelo limite de 2 fontes: MSD para tutores, *Disorders of the
  Pancreas in Dogs* ("increased thirst and urination, along with increased
  appetite and weight loss"), e VCA, *Diabetes Mellitus in Dogs* ("weight
  loss despite a ravenous appetite").
- **Abertas e descartadas:** VCA *Cushing's Disease in Dogs* (sede, urina e
  apetite, nada de xixi pela casa); MSD *Disorders of the Adrenal Glands in
  Dogs*; Cornell *Chronic Kidney Disease* (gato).

#### Não encontrado

- **"Pede pra sair de madrugada"**, com essas palavras (pedir para sair à
  noite). A PDSA fala de urinar dentro de casa à noite e de parar mais vezes
  no passeio.
- **Fonte em português**: não procurei. Sem busca na web disponível (limite
  de 200 buscas da sessão esgotado). As páginas certas da PDSA vieram do
  sitemap.xml do próprio site.
