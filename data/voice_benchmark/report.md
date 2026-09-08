# Benchmark de transcrição de voz (Whisper)

**Gerado em:** 2026-09-08 20:26 UTC · **commit:** `b6f567f`
· **modelo:** small

Fala **sintética** (edge-tts, vozes neurais PT-BR) a partir de
`scripts/voice_benchmark/references.csv`. É um limite otimista: áudio limpo e
bem articulado, não um tutor real ao telefone (evidencias/backlog.md#b-13).

## Resultado

| Métrica | Valor |
|---|---:|
| **WER agregado** | **0.052** (5.2%) |
| CER agregado | 0.018 (1.8%) |
| Áudios | 18 |
| Palavras de referência | 345 |
| Substituições / remoções / inserções | 13 / 3 / 2 |
| Tempo mediano por requisição | 4.5s |
| Idioma detectado ≠ pt | 0 |

WER agregado = (S + D + I) ÷ palavras de referência, sobre todos os áudios.

## Por item

| id | classe | voz | WER | S/D/I | ref → hipótese |
|---|---|---|---:|---|---|
| b01 | EMERGENCIA | Francisca | 0.00 | 0/0/0 | meu cachorro comeu um pedaço grande de chocolate hoje de manhã e agora está tremendo e vomitando<br>→ _Meu cachorro comeu um pedaço grande de chocolate hoje de manhã e agora está tremendo e vomitando._ |
| b02 | EMERGENCIA | Antonio | 0.06 | 1/0/0 | minha gata não consegue fazer xixi desde ontem fica tentando na caixa e miando de dor<br>→ _Minha gata não consegue fazer xixi desde ontem, fica tentando na caixa e meando de dor._ |
| b03 | EMERGENCIA | ThalitaMultilingual | 0.09 | 2/0/0 | meu cachorro está respirando com muita dificuldade a barriga vai pra dentro e pra fora bem rápido e a língua está meio roxa<br>→ _Meu cachorro está respirando com muita dificuldade, a barriga vai para dentro e para fora bem rápido e a língua está meio roxa._ |
| b04 | EMERGENCIA | Francisca | 0.10 | 1/1/0 | meu cão teve uma convulsão agora ficou caído de lado tremendo por uns dois minutos e fez xixi no chão<br>→ _Meu cão teve uma convulsão agora, ficou caído de lado tremendo por uns dois minutos e fechou no chão._ |
| b05 | NAO_EMERGENCIA | Antonio | 0.19 | 2/1/0 | minha gata está espirrando de vez em quando desde ontem mas continua comendo e brincando normalmente<br>→ _Unyagata está espirrando de vez em quando desde ontem mais continua comendo e brincando normalmente._ |
| b06 | EMERGENCIA | ThalitaMultilingual | 0.05 | 0/1/0 | meu cachorro foi atropelado agora há pouco ele está consciente mas mancando muito e tem um sangramento na pata<br>→ _Meu cachorro foi atropelado agora pouco, ele está consciente mas mancando muito e tem um sangramento na pata._ |
| b07 | EMERGENCIA | Francisca | 0.00 | 0/0/0 | meu cão está com vômito e diarreia desde ontem à noite já foram umas cinco vezes e ele está bem quietinho<br>→ _Meu cão está com vômito e diarreia desde ontem à noite. Já foram umas cinco vezes e ele está bem quietinho._ |
| b08 | EMERGENCIA | Antonio | 0.09 | 1/0/1 | acho que meu cachorro comeu comida com bastante cebola e alho ontem hoje ele está sem energia e a gengiva está pálida<br>→ _Acho que meu cachorro com meu comida com bastante cebola e alho ontem hoje ele está sem energia e a gengiva está pálida._ |
| b09 | NAO_EMERGENCIA | ThalitaMultilingual | 0.00 | 0/0/0 | meu cachorro está se coçando bastante atrás da orelha e tem uma casquinha na pele mas está comendo bem<br>→ _Meu cachorro está se coçando bastante atrás da orelha e tem uma casquinha na pele, mas está comendo bem._ |
| b10 | NAO_EMERGENCIA | Francisca | 0.00 | 0/0/0 | meu cão começou a mancar de leve da pata de trás depois de correr no parque mas ainda apoia o pé no chão<br>→ _Meu cão começou a mancar de leve da pata de trás depois de correr no parque, mas ainda apoia o pé no chão._ |
| b11 | NAO_EMERGENCIA | Antonio | 0.11 | 2/0/0 | a gata está com o olho lacrimejando e um pouco de remela há uns dois dias sem inchaço<br>→ _A gata está com o olho lacrimejando e um pouco de remela a uns dois dias sem chasso._ |
| b12 | EMERGENCIA | ThalitaMultilingual | 0.00 | 0/0/0 | meu cachorro grande está com a barriga muito inchada e dura tentando vomitar sem sair nada e muito inquieto<br>→ _Meu cachorro grande está com a barriga muito inchada e dura tentando vomitar sem sair nada e muito inquieto._ |
| b13 | EMERGENCIA | Francisca | 0.05 | 1/0/0 | meu cão cortou a pata em um vidro e está sangrando bastante já faz uns dez minutos e não para<br>→ _Meu cão cortou a pata em um vidro e está sangrando bastante, já faz uns 10 minutos e não para._ |
| b14 | EMERGENCIA | Antonio | 0.00 | 0/0/0 | meu filhote de dois meses está muito molinho não quer mamar e a boca dele está fria<br>→ _Meu filhote de dois meses está muito molinho. Não quer mamar e a boca dele está fria._ |
| b15 | EMERGENCIA | ThalitaMultilingual | 0.00 | 0/0/0 | meu cachorro macho fica indo no lugar de fazer xixi toda hora e só sai umas gotinhas e ele chora quando faz<br>→ _Meu cachorro macho fica indo no lugar de fazer xixi toda hora e só sai umas gotinhas e ele chora quando faz._ |
| b16 | EMERGENCIA | Francisca | 0.10 | 2/0/0 | meu cão foi picado por uma abelha e o focinho dele está inchando bem rápido e ele está se coçando muito<br>→ _Meu cão foi picado por uma belha e o focinho dele está enchendo bem rápido e ele está se coçando muito._ |
| b17 | EMERGENCIA | Antonio | 0.14 | 1/0/1 | minha cadela idosa amanheceu sem conseguir levantar as pernas de trás e está ofegante<br>→ _Minha cadela idosa amanheceu sem conseguir levantar as pernas de trás e está o fegante._ |
| b18 | NAO_EMERGENCIA | ThalitaMultilingual | 0.00 | 0/0/0 | meu gato está com um pouco de secreção no nariz e espirrando mas sem febre e comendo bem<br>→ _Meu gato está com um pouco de secreção no nariz e espirrando, mas sem febre e comendo bem._ |
