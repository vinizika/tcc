# Cinomose com sinais neurológicos — fontes

**Linha do mapa:** `distemper_neurological` · cão · emergência

**Caso da régua:** `b34`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 19/09/2026

## Fonte experimental

Wu et al. · Viruses · 2022 · DOI `10.3390/v14071520` · CC BY 4.0. SHA-256
`243b8581f721719db97f8fd95b8db4aa7fc31774f340502fea2ea35ed42f969d`.

Somente a página de sinais clínicos entra no recorte: 16 chunks de 69–93
tokens e um fallback de frase longa.

## Limitações

O artigo é acadêmico e o recorte não substitui diagnóstico. O vínculo entre os
sinais e o grau de urgência ainda depende dos especialistas.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador D) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `distemper_neurological` · cão · imediato
**Pesquisado em:** 25/09/2026 (agente D, rodada N6)
**Frases procuradas:** `como_o_tutor_conta#8` (filhote com vacinas incompletas) e `sinais_de_alarme#0` (convulsão mastigando no vazio e babando)

#### Candidata 1: MSD Veterinary Manual, versão para tutor

`distemper_neurological__msd_owner_distemper.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en (o corpo também está em inglês) |
| Registro | tutor |
| Autoridade | alta (manual veterinário) |
| Espécie | cão |
| Cobre os sinais | sim: "seizures, often with drooling and chewing motions of the jaw"; "twitching of muscles, such as in the leg or face" |
| Diz quando ir | não: não há orientação de urgência |
| Estrutura | 392 palavras e **nenhum heading**, então o documento é indexado inteiro, sem escolha de seção. Por ser curto, o problema é pequeno |
| Data | Full review jun/2026, Nick Roman, DVM, MPH |
| Acesso | abriu em 25/09/2026 |
| Direitos | "Copyright © 2026 Merck & Co., Inc. … All rights reserved." |

**Recomendação:** primária para `sinais_de_alarme#0`. Na outra frase só ajuda de lado ("Vaccination is the best prevention.").

#### Candidata 2: Texas A&M Veterinary Medical Diagnostic Laboratory (TVMDL)

`distemper_neurological__tvmdl_2026_distemper.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor (notícia de divulgação do laboratório, dirigida a quem vai adotar) |
| Autoridade | alta (laboratório do sistema Texas A&M University). O texto não tem autor assinado e cita Cathy Campbell, DVM |
| Espécie | cão |
| Cobre os sinais | sim: "puppies younger than four months are the most vulnerable to CDV"; os sinais neurológicos aparecem em lista ("Muscle twitching", "Seizures", "Paralysis"), sem mastigação |
| Diz quando ir | parcial: "it is important to consider diagnostic testing from the initial onset" |
| Estrutura | 971 palavras. Headings: What is distemper? · How it spreads · Recognizing clinical signs · Protecting dogs from distemper · Why testing matters · Ensuring a safe start in a new home. Tem trechos sobre os testes do laboratório (PCR, anticorpos) que não interessam ao tutor e devem ficar de fora na ingestão |
| Data | 29/04/2026 |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© 2026 Texas A&M Veterinary Medical Diagnostic Laboratory. All Rights Reserved." |

**Recomendação:** primária para `como_o_tutor_conta#8`.

#### Descartadas ou não capturadas

- **AVMA, "Canine distemper"** (para tutor): segundo o resultado de busca, cobria as duas frases. O script não conseguiu extrair o texto e o WebFetch também voltou vazio, então fica como **não verificada**.
- **Silva et al. 2007, Pesq. Vet. Bras. (620 casos)**, em português e acadêmico. Diz "maior predileção por filhotes e cães não-vacinados" e lista convulsão e sialorreia em itens separados. Foi lida pelo WebFetch e não capturada: é alternativa em PT, mais fraca que as duas acima.
- **Revisão "Cinomose canina" (Medicina Veterinária, UFRPE)**: o servidor falha no certificado SSL e a captura não abre.
- **CRMV-SP (2011)**: reprodução de matéria de jornal, sem os sinais.

#### Não encontrado

- Fonte PT para tutor com autoridade que descreva a convulsão com mastigação e baba.
- A expressão "não completou as vacinas". O que as fontes dizem é "before they are fully vaccinated", que tem o mesmo sentido.
