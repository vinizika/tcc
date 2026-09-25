# Lotes de diagnóstico (autópsia 2)

Relatos usados para **diagnosticar** o sistema na autópsia 2 (rodadas 14 a 21
do trilho B2). **Não são prova.** Eles serviram para tomar decisões de desenho,
então não podem dar o número final do TCC: esse é da prova 2, com os rótulos
validados por veterinários.

## `relatos_independentes.csv` — 122 relatos de quem não viu o mapa

Escritos por dois modelos de IA de famílias diferentes do atendente testado:
`indep` (i01 a i61) pelo `gemma-4-31b-it` e `indep2` (j01 a j61) pelo
`gemini-3.1-flash-lite`. Um relato por quadro do mapa, por autor.

- **O que o autor recebeu:** o nome leigo do quadro, a espécie, se é ou não
  emergência e o tom. **Não** recebeu a coluna de sinais do mapa, nem as fichas,
  nem a prova.
- **Composição, por autor:** 38 emergências (19 contadas com calma ou
  minimizando, 10 aflitas, 9 neutras) e 23 não emergências (12 aflitas ou
  exageradas, 11 neutras).
- **Rótulo:** a urgência do mapa para o quadro pedido (`marked_by`). **Não foi
  validado por veterinário.** Há rótulos discutíveis: "comeu pão com passas" e
  "comeu um pedaço de chocolate", marcados leves; "inchaço enorme na cara",
  marcado como picada de inseto local; "rosto meio inchado, picada de algum
  bicho", marcado como cobra.
- `author_severe_sign` é o sinal de gravidade que o próprio autor disse ter
  posto no relato.

O piloto da prova 2 (`piloto_prova2.csv` e os cadernos de linguagem) entra com a
[rodada 20](../../evidencias/joao/2026-09-24-21-prova-2-desenho-e-piloto.md).
