# Síndrome vestibular — fontes

**Linha do mapa:** `vestibular_syndrome_otitis_interna`

**Caso da régua:** `b48`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R81 · Current definition, diagnosis, and treatment of canine and feline idiopathic vestibular syndrome · Frontiers in Veterinary Science · 2023. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`087d0c4f0d5af75cd1d31f24ee7d0755738b776b24d034593eb66046bf2f2d66`.

A inspeção individual do recorte produziu **112 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Cobre síndrome vestibular idiopática e diferenciais; não é fonte específica de otite interna.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador D) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `vestibular_syndrome_otitis_interna` · cão e gato · imediato
**Pesquisado em:** 25/09/2026 (agente D, rodada N6)
**Frases procuradas:** `como_o_tutor_conta#5` (anda em círculos ou rola pro mesmo lado) e `sinais_de_alarme#3` (sonolento, confuso ou com fraqueza nas patas)

#### Candidata 1: Fitzpatrick Referrals, "Vestibular disease"

`vestibular_syndrome_otitis_interna__fitzpatrick_vestibular.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor (página do serviço de neurologia escrita para o dono do animal, com trechos técnicos) |
| Autoridade | média (hospital veterinário de referência privado no Reino Unido, com especialistas em neurologia) |
| Espécie | cão e gato (o texto fala mais de cão; cita gato na síndrome idiopática e nos pólipos) |
| Cobre os sinais | sim: "Circling or deviating (towards the side of the problem)". Rolar não aparece |
| Responde o discriminador (central × periférica) | sim: "indication of central vestibular disease is depressed mental status (e.g. poorly interactive and disorientated)" |
| Diz quando ir | não: não há orientação de urgência para o tutor |
| Estrutura | 1468 palavras. Headings: What is vestibular disease? · How can I tell if my dog has vestibular disease? · What is the cause of vestibular disease? · How is vestibular disease diagnosed? · How is vestibular disease treated? · What is the prognosis of vestibular disease?. Diagnóstico (RM, TC, líquor, miringotomia) e tratamento são longos e devem ser excluídos na ingestão |
| Data | não informada |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© 2026 Fitzpatrick Referrals" (sem licença de reuso declarada) |

**Recomendação:** primária para `sinais_de_alarme#3`. Em `como_o_tutor_conta#5` só cobre a metade dos círculos.

#### Candidata 2: VCA Animal Hospitals, "Vestibular Disease in Cats"

`vestibular_syndrome_otitis_interna__vca_feline_vestibular.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | média (rede de hospitais; conteúdo da LifeLearn) |
| Espécie | **só gato**. A página de cão da mesma rede diz "Falling or circling to one side", sem rolar |
| Cobre os sinais | sim: "Falling, rolling or circling to one side" |
| Diz quando ir | sim (piora): "If your cat does not improve or gets worse, a more serious underlying disorder" |
| Estrutura | 646 palavras em seis headings de pergunta; boa estrutura. O rodapé de direitos da LifeLearn saiu no fim do arquivo capturado e deve ficar fora da indexação |
| Data | "Last updated on Sep 4, 2026" (T. Hunter, M. Weir, E. Ward) |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© Copyright 2026 LifeLearn Inc." Uso pessoal dos clientes; proíbe copiar e redistribuir sem consentimento e proíbe usar IA para reescrever ou republicar. **O especialista precisa saber disto antes de aprovar.** |

**Recomendação:** primária para `como_o_tutor_conta#5`, com a ressalva da espécie. Na frase de alarme só tem "Disorientation", como sinal vestibular geral.

#### Descartadas ou não capturadas

- **MSD, "Otitis Media and Interna" (versões para tutor de cão e de gato)**: cabeça torta, descoordenação e olhos mexendo; não fala de círculos, de rolar nem de estado mental.
- **Davies Veterinary Specialists, fact sheet**: "rolling over" e "circling" aparecem em frases separadas, e para o cérebro cita "seizures, weakness", sem sonolência. É alternativa média.
- **MSPCA-Angell**: texto clínico, só de cão. **Veterinary Partner (VIN)**: a página só carrega com JavaScript.
- **Em português**: só TCCs e dissertações (UnB 2019, U. Porto) e pet shop. Nenhuma fonte PT para tutor com autoridade.

#### Não encontrado

- Fonte que diga "sonolento" com todas as letras. "Depressed mental status" é o termo técnico mais próximo.
- Fonte que localize a fraqueza "nas patas". O que achei foi "loss of strength and proprioception", sem dizer onde.
- Uma fonte única, para cão e gato, que traga círculos e rolar na mesma frase.
