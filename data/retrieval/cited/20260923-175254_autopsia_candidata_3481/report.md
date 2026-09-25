# Régua de recuperação — 20260923-175254_autopsia_candidata_3481

**Quando:** 2026-09-23T17:52:54.893266-03:00 · **commit:** `fceab20`

Mede se a busca traz o protocolo certo, por **posição**. Não mede classificação — para isso é o runner de `data/evaluation/`.

## Resultado

| Métrica | Valor |
|---|---|
| **Protocolo certo em 1º** (Precision@1) | 0.515 (66 casos com protocolo na base) |
| Posição média invertida (MRR) | 0.570 |
| Protocolo certo entre os 5 (Recall@5) | 0.667 |
| Casos com algum trecho acima de 0.70 | 0.333 |
| Nota máxima média | 0.6518 |

### Quando a resposta certa é não trazer nada

| Natureza | Casos | Busca ficou quieta |
|---|---|---|
| Caso leve | 0 | — |
| Sem cobertura na base | 0 | — |

### O número é bom? Comparado com o quê

| Estratégia | Protocolo certo em 1º |
|---|---|
| Escolher um documento ao acaso | 0.017 |
| Responder sempre o mesmo documento | 0.015 |
| **A busca** | **0.515** |

> **Cuidado ao ler o Recall.** A busca mostra em média 4.5 documentos distintos por caso, e a base tem 54 documentos no total. Com um acervo pequeno, "o certo está entre os primeiros" é quase geométrico — a métrica só passa a informar quando a base crescer.

## Caso a caso

| Caso | Natureza | Esperado | 1º lugar | Posição | Nota máx. |
|---|---|---|---|---|---|
| b01 | com protocolo | chocolate_toxicosis | chocolate_toxicosis | 1 | 0.750 |
| b02 | com protocolo | urethral_obstruction | urethral_obstruction | 1 | 0.670 |
| b03 | com protocolo | respiratory_distress | respiratory_distress | 1 | 0.635 |
| b04 | com protocolo | seizures | burns_and_electrical_injury | 4 | 0.679 |
| b05 | com protocolo | mild_upper_respiratory_signs | mild_upper_respiratory_signs | 1 | 0.702 |
| b06 | com protocolo | trauma_and_bleeding | trauma_and_bleeding | 1 | 0.675 |
| b07 | com protocolo | vomiting_and_diarrhea | vomiting_and_diarrhea | 1 | 0.721 |
| b08 | com protocolo | allium_toxicosis | allium_toxicosis | 1 | 0.721 |
| b09 | com protocolo | flea_dermatitis_pruritus | otitis_externa_mild | — | 0.567 |
| b10 | com protocolo | mild_lameness | mild_lameness | 1 | 0.779 |
| b11 | com protocolo | mild_conjunctivitis | mild_conjunctivitis | 1 | 0.721 |
| b12 | com protocolo | gastric_dilatation_volvulus | airway_foreign_body_choking | 5 | 0.662 |
| b13 | com protocolo | trauma_and_bleeding | slow_growing_lump | 3 | 0.579 |
| b14 | com protocolo | fading_neonate | fading_neonate | 1 | 0.772 |
| b15 | com protocolo | urethral_obstruction | airway_foreign_body_choking | 2 | 0.599 |
| b16 | com protocolo | anaphylaxis_facial_swelling | anaphylaxis_facial_swelling | 1 | 0.721 |
| b17 | com protocolo | acute_hindlimb_paralysis | acute_hindlimb_paralysis | 1 | 0.721 |
| b18 | com protocolo | mild_upper_respiratory_signs | mild_upper_respiratory_signs | 1 | 0.720 |
| b19 | com protocolo | human_medication_poisoning | lily_toxicosis_cats | 4 | 0.645 |
| b20 | com protocolo | carbamate_organophosphate_poisoning | airway_foreign_body_choking | — | 0.625 |
| b21 | com protocolo | permethrin_toxicosis_cats | seizures | — | 0.572 |
| b22 | com protocolo | anticoagulant_rodenticide_poisoning | anticoagulant_rodenticide_poisoning | 1 | 0.721 |
| b23 | com protocolo | parvovirus_panleukopenia | vomiting_and_diarrhea | — | 0.556 |
| b24 | com protocolo | pyometra | pyometra | 1 | 0.744 |
| b25 | com protocolo | dietary_indiscretion_mild | dietary_indiscretion_mild | 1 | 0.734 |
| b26 | com protocolo | inappropriate_urination_or_cystitis | inappropriate_urination_or_cystitis | 1 | 0.721 |
| b27 | com protocolo | collapse_and_pale_gums | collapse_and_pale_gums | 1 | 0.721 |
| b28 | com protocolo | osteoarthritis_stiffness | exertional_panting_mild | 2 | 0.572 |
| b29 | com protocolo | reduced_appetite_no_other_signs | reduced_appetite_no_other_signs | 1 | 0.544 |
| b30 | com protocolo | gastrointestinal_foreign_body | inappropriate_urination_or_cystitis | — | 0.614 |
| b31 | com protocolo | cat_bite_abscess | mild_upper_respiratory_signs | — | 0.615 |
| b32 | com protocolo | congestive_heart_failure | congestive_heart_failure | 1 | 0.709 |
| b33 | com protocolo | diabetic_ketoacidosis | dietary_indiscretion_mild | — | 0.653 |
| b34 | com protocolo | distemper_neurological | leptospirosis_acute | — | 0.662 |
| b35 | com protocolo | dystocia | hypoglycemia_toy_puppy | — | 0.614 |
| b36 | com protocolo | feline_aortic_thromboembolism | acute_hindlimb_paralysis | — | 0.611 |
| b37 | com protocolo | leptospirosis_acute | single_vomiting_or_mild_diarrhea | — | 0.605 |
| b38 | com protocolo | lily_toxicosis_cats | lily_toxicosis_cats | 1 | 0.657 |
| b39 | com protocolo | toad_bufotoxin_poisoning | otitis_externa_mild | — | 0.612 |
| b40 | com protocolo | tremors_without_seizure | tremors_without_seizure | 1 | 0.680 |
| b41 | com protocolo | normal_estrus | pyometra | — | 0.654 |
| b42 | com protocolo | collapse_and_pale_gums | collapse_and_pale_gums | 1 | 0.721 |
| b43 | com protocolo | ocular_emergency | ocular_emergency | 1 | 0.666 |
| b44 | com protocolo | airway_foreign_body_choking | lily_toxicosis_cats | — | 0.500 |
| b45 | com protocolo | snake_and_scorpion_envenomation | snake_and_scorpion_envenomation | 1 | 0.593 |
| b46 | com protocolo | tick_borne_disease_anemia | collapse_and_pale_gums | — | 0.721 |
| b47 | com protocolo | hypoglycemia_toy_puppy | hypoglycemia_toy_puppy | 1 | 0.578 |
| b48 | com protocolo | vestibular_syndrome_otitis_interna | acute_hindlimb_paralysis | — | 0.573 |
| b49 | com protocolo | high_rise_syndrome_cats | collapse_and_pale_gums | — | 0.721 |
| b50 | com protocolo | burns_and_electrical_injury | burns_and_electrical_injury | 1 | 0.606 |
| b51 | com protocolo | eclampsia | tremors_without_seizure | — | 0.697 |
| b52 | com protocolo | grape_xylitol_toxicosis | grape_xylitol_toxicosis | 1 | 0.704 |
| b53 | com protocolo | normal_whelping | airway_foreign_body_choking | — | 0.571 |
| b54 | com protocolo | insect_sting_local_reaction | anaphylaxis_facial_swelling | — | 0.628 |
| b55 | com protocolo | kennel_cough_mild | kennel_cough_mild | 1 | 0.646 |
| b56 | com protocolo | polyuria_polydipsia_investigate | carbamate_organophosphate_poisoning | — | 0.588 |
| b57 | com protocolo | otitis_externa_mild | otitis_externa_mild | 1 | 0.584 |
| b58 | com protocolo | minor_wound | cat_bite_abscess | 2 | 0.593 |
| b59 | com protocolo | periodontal_disease_mild | tremors_without_seizure | 4 | 0.613 |
| b60 | com protocolo | slow_growing_lump | airway_foreign_body_choking | 2 | 0.575 |
| b61 | com protocolo | exertional_panting_mild | canine_heatstroke | 3 | 0.614 |
| b62 | com protocolo | rabies_exposure_wild_animal_bite | rabies_exposure_wild_animal_bite | 1 | 0.628 |
| b63 | com protocolo | ticks_found_no_signs | ticks_found_no_signs | 1 | 0.585 |
| b64 | com protocolo | single_vomiting_or_mild_diarrhea | single_vomiting_or_mild_diarrhea | 1 | 0.773 |
| b65 | com protocolo | single_vomiting_or_mild_diarrhea | lily_toxicosis_cats | — | 0.594 |
| b66 | com protocolo | single_vomiting_or_mild_diarrhea | single_vomiting_or_mild_diarrhea | 1 | 0.710 |

---

Gabarito marcado pelo trilho B2, **provisório**, aguardando validação do trilho A. Ver `data/retrieval/README.md`.
