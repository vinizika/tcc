# Insuficiência cardíaca descompensada — fontes

**Linha do mapa:** `congestive_heart_failure` · cão e gato · emergência

**Caso da régua:** `b32`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 19/09/2026

## Fonte experimental

Hsieh e Beets · Frontiers in Veterinary Science · 2020 · DOI
`10.3389/fvets.2019.00513` · CC BY 4.0. SHA-256
`9fc525f2ebfd6e0ebc9cfe6c932cc8649a21ca4ef06bcf6975dda849daa9d881`.

A inspeção do recorte clínico produziu 80 chunks de 52–115 tokens, incluindo
localização da tosse, imagem torácica e manejo médico.

## Limitações

A fonte discute tosse cardíaca e diagnóstico diferencial; não transforma todo
episódio de tosse em insuficiência cardíaca nem valida sozinha a urgência.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador C) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `congestive_heart_failure` (cão e gato; imediato)
**Pesquisado em:** 25/09/2026 · **Frases do grupo C:** tutor#4, alarme#1, alarme#2

#### Régua de aptidão

##### Tufts HeartSmart — *Difficulty Breathing (Dyspnea)*
`congestive_heart_failure__tufts_dispneia.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en (conferido no corpo) |
| Registro | tutor |
| Autoridade | alta (Cummings School of Veterinary Medicine, Tufts University, serviço de cardiologia) |
| Espécie | cão e gato ("Cats with difficulty breathing may act in a similar fashion") |
| Cobre os sinais | sim — "refuse to lie down on their side" (corpo); "a tongue that looks purple/blue instead of pink" (corpo) |
| Responde o discriminador | sim, quanto ao ritmo: "fast breathing or extra breathing effort present even at rest" |
| Diz quando ir | sim — "Difficulty breathing is an emergency and you should seek treatment right away." |
| Estrutura | 689 palavras; praticamente sem headings (título + legendas de vídeo curtas soltas como linhas próprias + "Assessment of Breathing Rate and Breathing Effort:" embutido no parágrafo). Página curta: tudo-ou-nada não é grave aqui, mas as legendas de vídeo podem virar pseudo-seções |
| Data | não declarada (só "© Tufts University 2026") |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© Tufts University 2026"; sem licença declarada |

##### VCA — *Congestive Heart Failure in Dogs*
`congestive_heart_failure__vca_icc.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | média (rede de hospitais; texto LifeLearn) |
| Espécie | só cão |
| Cobre os sinais | sim — "coughing when at rest or sleeping, an increased resting respiratory rate" ("What clinical signs should I expect?"); "pale or bluish gums" |
| Responde o discriminador | em parte — define frequência em repouso "when they are sleeping or resting quietly" ("Is there a way to detect CHF early?") |
| Diz quando ir | sim — "…in a pet with a heart murmur, notify your veterinarian immediately." |
| Estrutura | 1.250 palavras; 8 headings em pergunta. Entrariam "What clinical signs should I expect?" e "Is there a way to detect CHF early?"; excluir o resto (fisiopatologia, diagnóstico, tratamento) e a linha de copyright no fim |
| Data | 15/11/2023 (última atualização) |
| Acesso | abriu em 25/09/2026 |
| Direitos | © 2023 LifeLearn; "licensed to this practice for the personal use of its clients"; proíbe cópia sem consentimento e **proíbe uso de IA para reescrever/republicar** — levar à revisão de direitos |

#### Frases

| Frase | Status | Fonte | Trecho (literal) |
|---|---|---|---|
| tutor#4 "Respira rápido até quando tá dormindo." | sustentada | VCA | "Other signs associated with heart failure include coughing when at rest or sleeping, an increased resting respiratory rate or excessive panting" (+ definição de RRR "when they are sleeping or resting quietly") |
| alarme#1 "Língua ou gengiva arroxeada." | sustentada | Tufts (língua) + VCA (gengiva) | "A dog with severe difficulty breathing may have a tongue that looks purple/blue instead of pink, showing that they are not getting enough oxygen." |
| alarme#2 "Não consegue deitar, fica sentado pra conseguir respirar." | sustentada (nuance: recusa deitar **de lado**) | Tufts | "Many dogs with severe difficulty breathing will refuse to lie down on their side because it is harder for them to breathe in this position. Instead, they will prefer to sit or stand." |

#### Recomendação

- **Primária:** Tufts — autoridade alta, cão e gato, diz quando ir, cobre as duas frases de alarme.
- **Alternativa:** VCA — cobre gengiva e respiração dormindo, mas é só cão, autoridade média e tem restrição de direitos explícita.

#### Não encontrado

- Nada faltou nas três frases. Não achei fonte em português de autoridade para tutor.
- Candidatas vistas e não capturadas (limite de 2): PDSA *Heart problems in dogs* (abriu, sem respiração dormindo, cor da gengiva nem postura — descartada); VCA *Home Breathing Rate Evaluation*, Tufts *Monitoring Heart Disease Treatment at Home*, Cardiac Education Group (PDF) — só vistas na busca.
