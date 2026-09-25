# Régua de recuperação — 20260925-031753_fichas_bge_m3_vector

**Quando:** 2026-09-25T03:17:53.471867-03:00 · **commit:** `828ff40`

Mede se a busca traz o protocolo certo, por **posição**. Não mede classificação — para isso é o runner de `data/evaluation/`.

## Resultado

| Métrica | Valor |
|---|---|
| **Protocolo certo em 1º** (Precision@1) | 0.879 (66 casos com protocolo na base) |
| Posição média invertida (MRR) | 0.931 |
| Protocolo certo entre os 5 (Recall@5) | 0.985 |
| Casos com algum trecho acima de 0.70 | 0.258 |
| Nota máxima média | 0.6573 |

### Quando a resposta certa é não trazer nada

| Natureza | Casos | Busca ficou quieta |
|---|---|---|
| Caso leve | 0 | — |
| Sem cobertura na base | 0 | — |

### O número é bom? Comparado com o quê

| Estratégia | Protocolo certo em 1º |
|---|---|
| Escolher um documento ao acaso | 0.016 |
| Responder sempre o mesmo documento | 0.030 |
| **A busca** | **0.879** |

> **Cuidado ao ler o Recall.** A busca mostra em média 50.0 documentos distintos por caso, e a base tem 61 documentos no total. Com um acervo pequeno, "o certo está entre os primeiros" é quase geométrico — a métrica só passa a informar quando a base crescer.

## Caso a caso

| Caso | Natureza | Esperado | 1º lugar | Posição | Nota máx. |
|---|---|---|---|---|---|
| b01 | com protocolo | chocolate_toxicosis | chocolate_toxicosis | 1 | 0.731 |
| b02 | com protocolo | urethral_obstruction | urethral_obstruction | 1 | 0.640 |
| b03 | com protocolo | respiratory_distress | respiratory_distress | 1 | 0.715 |
| b04 | com protocolo | seizures | seizures | 1 | 0.718 |
| b05 | com protocolo | mild_upper_respiratory_signs | mild_upper_respiratory_signs | 1 | 0.643 |
| b06 | com protocolo | trauma_and_bleeding | trauma_and_bleeding | 1 | 0.695 |
| b07 | com protocolo | vomiting_and_diarrhea | vomiting_and_diarrhea | 1 | 0.719 |
| b08 | com protocolo | allium_toxicosis | allium_toxicosis | 1 | 0.721 |
| b09 | com protocolo | flea_dermatitis_pruritus | flea_dermatitis_pruritus | 1 | 0.646 |
| b10 | com protocolo | mild_lameness | mild_lameness | 1 | 0.644 |
| b11 | com protocolo | mild_conjunctivitis | mild_conjunctivitis | 1 | 0.630 |
| b12 | com protocolo | gastric_dilatation_volvulus | gastric_dilatation_volvulus | 1 | 0.696 |
| b13 | com protocolo | trauma_and_bleeding | trauma_and_bleeding | 1 | 0.596 |
| b14 | com protocolo | fading_neonate | fading_neonate | 1 | 0.597 |
| b15 | com protocolo | urethral_obstruction | urethral_obstruction | 1 | 0.638 |
| b16 | com protocolo | anaphylaxis_facial_swelling | insect_sting_local_reaction | 2 | 0.732 |
| b17 | com protocolo | acute_hindlimb_paralysis | acute_hindlimb_paralysis | 1 | 0.598 |
| b18 | com protocolo | mild_upper_respiratory_signs | mild_upper_respiratory_signs | 1 | 0.727 |
| b19 | com protocolo | human_medication_poisoning | human_medication_poisoning | 1 | 0.692 |
| b20 | com protocolo | carbamate_organophosphate_poisoning | carbamate_organophosphate_poisoning | 1 | 0.569 |
| b21 | com protocolo | permethrin_toxicosis_cats | permethrin_toxicosis_cats | 1 | 0.732 |
| b22 | com protocolo | anticoagulant_rodenticide_poisoning | anticoagulant_rodenticide_poisoning | 1 | 0.687 |
| b23 | com protocolo | parvovirus_panleukopenia | vomiting_and_diarrhea | 2 | 0.612 |
| b24 | com protocolo | pyometra | pyometra | 1 | 0.630 |
| b25 | com protocolo | dietary_indiscretion_mild | dietary_indiscretion_mild | 1 | 0.569 |
| b26 | com protocolo | inappropriate_urination_or_cystitis | urethral_obstruction | 2 | 0.654 |
| b27 | com protocolo | collapse_and_pale_gums | collapse_and_pale_gums | 1 | 0.716 |
| b28 | com protocolo | osteoarthritis_stiffness | osteoarthritis_stiffness | 1 | 0.609 |
| b29 | com protocolo | reduced_appetite_no_other_signs | reduced_appetite_no_other_signs | 1 | 0.618 |
| b30 | com protocolo | gastrointestinal_foreign_body | gastrointestinal_foreign_body | 1 | 0.616 |
| b31 | com protocolo | cat_bite_abscess | cat_bite_abscess | 1 | 0.670 |
| b32 | com protocolo | congestive_heart_failure | congestive_heart_failure | 1 | 0.735 |
| b33 | com protocolo | diabetic_ketoacidosis | diabetic_ketoacidosis | 1 | 0.628 |
| b34 | com protocolo | distemper_neurological | parvovirus_panleukopenia | 7 | 0.585 |
| b35 | com protocolo | dystocia | normal_whelping | 2 | 0.582 |
| b36 | com protocolo | feline_aortic_thromboembolism | feline_aortic_thromboembolism | 1 | 0.677 |
| b37 | com protocolo | leptospirosis_acute | ocular_emergency | 2 | 0.600 |
| b38 | com protocolo | lily_toxicosis_cats | lily_toxicosis_cats | 1 | 0.724 |
| b39 | com protocolo | toad_bufotoxin_poisoning | toad_bufotoxin_poisoning | 1 | 0.704 |
| b40 | com protocolo | tremors_without_seizure | tremors_without_seizure | 1 | 0.674 |
| b41 | com protocolo | normal_estrus | pyometra | 2 | 0.603 |
| b42 | com protocolo | collapse_and_pale_gums | collapse_and_pale_gums | 1 | 0.709 |
| b43 | com protocolo | ocular_emergency | ocular_emergency | 1 | 0.612 |
| b44 | com protocolo | airway_foreign_body_choking | gastrointestinal_foreign_body | 3 | 0.608 |
| b45 | com protocolo | snake_and_scorpion_envenomation | snake_and_scorpion_envenomation | 1 | 0.700 |
| b46 | com protocolo | tick_borne_disease_anemia | tick_borne_disease_anemia | 1 | 0.654 |
| b47 | com protocolo | hypoglycemia_toy_puppy | hypoglycemia_toy_puppy | 1 | 0.617 |
| b48 | com protocolo | vestibular_syndrome_otitis_interna | vestibular_syndrome_otitis_interna | 1 | 0.654 |
| b49 | com protocolo | high_rise_syndrome_cats | high_rise_syndrome_cats | 1 | 0.641 |
| b50 | com protocolo | burns_and_electrical_injury | burns_and_electrical_injury | 1 | 0.755 |
| b51 | com protocolo | eclampsia | eclampsia | 1 | 0.718 |
| b52 | com protocolo | grape_xylitol_toxicosis | grape_xylitol_toxicosis | 1 | 0.779 |
| b53 | com protocolo | normal_whelping | normal_whelping | 1 | 0.618 |
| b54 | com protocolo | insect_sting_local_reaction | insect_sting_local_reaction | 1 | 0.656 |
| b55 | com protocolo | kennel_cough_mild | kennel_cough_mild | 1 | 0.610 |
| b56 | com protocolo | polyuria_polydipsia_investigate | polyuria_polydipsia_investigate | 1 | 0.620 |
| b57 | com protocolo | otitis_externa_mild | otitis_externa_mild | 1 | 0.620 |
| b58 | com protocolo | minor_wound | minor_wound | 1 | 0.647 |
| b59 | com protocolo | periodontal_disease_mild | periodontal_disease_mild | 1 | 0.673 |
| b60 | com protocolo | slow_growing_lump | slow_growing_lump | 1 | 0.668 |
| b61 | com protocolo | exertional_panting_mild | exertional_panting_mild | 1 | 0.717 |
| b62 | com protocolo | rabies_exposure_wild_animal_bite | rabies_exposure_wild_animal_bite | 1 | 0.671 |
| b63 | com protocolo | ticks_found_no_signs | ticks_found_no_signs | 1 | 0.665 |
| b64 | com protocolo | single_vomiting_or_mild_diarrhea | single_vomiting_or_mild_diarrhea | 1 | 0.596 |
| b65 | com protocolo | single_vomiting_or_mild_diarrhea | single_vomiting_or_mild_diarrhea | 1 | 0.563 |
| b66 | com protocolo | single_vomiting_or_mild_diarrhea | single_vomiting_or_mild_diarrhea | 1 | 0.635 |

---

Gabarito marcado pelo trilho B2, **provisório**, aguardando validação do trilho A. Ver `data/retrieval/README.md`.
