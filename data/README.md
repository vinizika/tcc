# data/

Os dados do projeto: os datasets de origem, o que foi derivado deles e as
rodadas de avaliação. **A base de conhecimento (os PDFs dos protocolos) não
fica aqui** — está em `backend/data/documents/`, porque é o backend que a
indexa.

```
data/
├── dataset1_raw.csv     <- Animal Disease (Kaggle), como baixado
├── dataset1.csv         <- o mesmo, com as colunas usadas
├── dataset2.csv         <- Animal Disease Prediction (Kaggle), como baixado
├── processed/           <- tudo que os scripts derivam dos dois acima
└── evaluation/          <- rodadas de avaliação → README próprio
```

Regra: os três CSVs de origem **não se editam**. Tudo em `processed/` é
regenerável pelos scripts de `scripts/`, na ordem descrita abaixo.

## Os datasets de origem

| Arquivo | Origem | Colunas | Para que serve |
|---|---|---|---|
| `dataset1.csv` | *Animal Disease*, G. Hephzibah, Kaggle (acesso em maio/2026) | `AnimalName`, `symptoms1`…`symptoms5`, `Dangerous` (Yes/No) | É o **conjunto de avaliação**: cada linha é um animal com até cinco sintomas e o rótulo de perigo, que vira EMERGENCIA / NAO_EMERGENCIA |
| `dataset2.csv` | *Animal Disease Prediction*, S. John, Kaggle (acesso em maio/2026) | `Animal_Type`, `Breed`, `Gender`, `Duration`, `Symptom_1`…`Symptom_4`, colunas binárias de sintoma, `Disease_Prediction` | Mais bem organizado; usado como **vocabulário padrão de sintomas** para o data augmentation |

Os relatos usados na avaliação são montados a partir do `dataset1`:
`Animal: Dog. Sintomas observados: Fever, Vomiting, ...` — o nome do animal
e os sintomas em inglês, como vêm no arquivo. Ver
[B-15](../evidencias/backlog.md#b-15) sobre isso.

## `processed/` — o que cada arquivo é, na ordem em que é gerado

| Passo | Script | Gera | O que faz |
|---|---|---|---|
| 1 | `clean_datasets.py` | `dataset1_clean.csv` | Normaliza nomes de animal e sintoma ("Dogs", "dog" → "Dog"; "Vomitting" → "Vomiting"), remove 2 linhas sem rótulo e 30 duplicatas: **871 → 839 linhas** (819 Yes, 20 No). Marca `Source = original` |
| 1 | `clean_datasets.py` | `dataset2_clean.csv`, `symptom_vocabulary_dataset2.csv` | Limpa o dataset 2 e extrai seu vocabulário de sintomas com frequência |
| 2 | `list_dataset2_symptoms.py` | — (imprime) | Lista os 16 sintomas do dataset 2 para cão e gato |
| 3 | `create_allowed_symptoms.py` | `allowed_symptoms_for_synthetic_no.csv` | Os **5 sintomas leves** escolhidos com a especialista: Eye Discharge, Nasal Discharge, Skin Lesions, Sneezing, Lameness |
| 4 | `data_augmentation_dataset_1_nao_emergencia.py` | `dataset1_synthetic_no_cases.csv`, `dataset1_augmented.csv` | Gera as linhas sintéticas de **não emergência** (ver abaixo) e as anexa ao dataset limpo |
| 5 | `validate_synthetic_no_with_llm.py` | `dataset1_synthetic_no_cases_llm_approved.csv`, **`dataset1_augmented_llm_validated.csv`** | Um modelo de linguagem revisa cada linha sintética e rejeita as que poderiam ser urgentes: 32 avaliadas, **27 aprovadas**. O arquivo final tem 839 + 27 = **866 linhas** e é o que o runner de avaliação lê |

O runner filtra `AnimalName` em Dog e Cat, o que dá as **98 linhas** usadas
em todas as medições: 71 emergências e 27 não emergências.

## Como o data augmentation foi feito — e o que o rótulo não diz

O dataset 1 limpo tem 819 emergências para 20 não emergências, e nenhuma
não emergência de cão ou gato. Para dar ao conjunto uma classe de não
emergência avaliável, foram geradas linhas sintéticas assim:

1. A especialista escolheu **5 sintomas leves** do vocabulário do dataset 2.
2. O script gerou **todas as combinações** de 3, 4 e 5 desses sintomas,
   para cão e para gato: (10 + 5 + 1) × 2 = **32 linhas**. Geração
   combinatória e determinística — não foi um modelo que inventou.
3. Um modelo de linguagem local revisou cada linha e rejeitou 5 que
   considerou potencialmente urgentes. Ficaram **27**.

**Atenção ao rótulo:** a coluna `Source` dessas linhas diz
`llm_data_augmentation`, e o diário antigo fala em "geração via LLM". O
método real é o descrito acima — a geração foi combinatória; o modelo só
validou. É um método melhor (controlado e reprodutível), mas o nome induz a
descrição errada. Item [B-16](../evidencias/backlog.md#b-16) do backlog.

## O que o conjunto de avaliação mede — e o que não mede

Duas limitações que acompanham qualquer número medido sobre ele:

- **Rótulo e origem estão confundidos.** Nas 98 linhas, as 71 emergências
  são todas `original` e as 27 não emergências são todas sintéticas.
- **O rótulo é trivialmente separável.** As não emergências usam só os 5
  sintomas leves e têm 3 ou 4 sintomas; as emergências têm sempre 5, de 192
  termos. A regra "só sintomas leves → não emergência" acerta **98 de 98**
  sem modelo nenhum.

Ou seja: o conjunto mede se o sistema **parou de exagerar a urgência de
cinco sinais leves**, não a capacidade geral de triagem. O relatório de cada
rodada traz essas regras triviais como referência, por isso. Detalhe e
próximos passos em [B-05](../evidencias/backlog.md#b-05).

## `evaluation/`

As rodadas de avaliação, as métricas e como medir: ver
[`evaluation/README.md`](evaluation/README.md).
