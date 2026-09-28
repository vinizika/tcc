# Lote 4 — resumo

40 relatos (q121–q160) em `relatos.json`, 8 cadernos em `cadernos/`. Conferência em Python: JSON válido, 40 ids iguais aos dos pedidos e na mesma ordem, "mas" presente nos 16 com `usar_mas=true` e ausente nos 24 com `false`. Nenhum relato repete 6 palavras seguidas de trecho entre aspas dos cadernos (duas repetições de expressões minhas, em q126 e q137, foram reescritas). Nenhum relato diz "é emergência". Todas as URLs de `inspiracao` estão no caderno do quadro.

## Fontes por quadro (consultadas com conteúdo útil / em português)

| Quadro | Tema | Fontes úteis | Em PT | Observação |
|---|---|---|---|---|
| L4Q01 | veneno de rato | 7 | 4 | fala de tutora em notícia (CNN Brasil); pergunta de tutor (Dial A Vet) |
| L4Q02 | olho grave | 6 | 3 | fórum de tutores de shih tzu (proptose) |
| L4Q03 | vômito/diarreia que não param | 5 | 3 | comentários de leitores na Cobasi |
| L4Q04 | trombo em gato | 5 | 2 | as 2 em PT não tratam do trombo (mancar genérico; cardiomiopatia) |
| L4Q05 | doença do carrapato com anemia | 5 | 4 | comentários de leitores na Cobasi |
| L4Q06 | espirro/coriza leve | 6 | 3 | um caso grave (PDSA) só como contraste |
| L4Q07 | picada com inchaço local | 6 | 4 | notícia de cão com focinho inchado (Portal do Dog) |
| L4Q08 | caroço crescendo devagar | 4 (+1 descartada) | 3 | comentários de leitores na Cobasi |

## Dificuldades
- **Cota de busca esgotada cedo.** A cota de WebSearch da sessão chegou a 200/200 depois de poucas buscas minhas (é compartilhada com o resto da sessão). Continuei abrindo páginas direto com WebFetch. Para achar os endereços, usei os mapas públicos dos sites (`sitemap.xml` de Cobasi, Portal do Dog e PDSA). Não usei outro buscador para contornar a cota.
- **Pouca fala direta de tutor.** Os fóruns e sites de pergunta e resposta recusaram acesso (HTTP 403): TheCatSite, JustAnswer, BackyardChickens, Catster, Petz e Petlove. O Tudo Sobre Cachorros bloqueou por mod_security, o blogdocachorro.com.br não resolveu o endereço (DNS), e o robots.txt do PeritoAnimal proíbe o mapa do site. Não tentei contornar nenhum desses bloqueios. A linguagem de tutor veio sobretudo:
  - dos comentários de leitores da Cobasi;
  - do fórum Mundo Shih Tzu;
  - de notícias (CNN Brasil, Portal do Dog);
  - de uma pergunta de tutor no Dial A Vet.

  O resto são páginas de orientação de clínicas e hospitais (PDSA, VCA, Cornell, RexVet, PetMD).
- **L4Q04 (trombo) foi o quadro mais pobre.** Não encontrei nenhuma fonte em português sobre o quadro nem fala de tutor, e várias URLs tentadas deram 404. A linguagem desse caderno é mais síntese minha a partir dos guias em inglês e dos comentários sobre gato mancando.

## Pedidos com rótulo ou combinação que me pareceu estranha (nada foi alterado)
- **q160** (caroço, NAO_EMERGENCIA, gêmea de "desmaiou/caído, gengiva branca"): a dupla é pouco natural. Qualquer detalhe que lembre desmaio põe no relato um episódio que um triador pode pesar. Resolvi com um falso alarme (sono pesado, levanta na hora, gengiva conferida e rosada), mas o relato fica um pouco artificial.
- **q155** (picada, NAO_EMERGENCIA "consulta de rotina", gêmea de "cara inchando"): algumas orientações (PDSA, para cães) mandam falar com o veterinário quando o inchaço é no rosto. Mantive um calombo pequeno, parado há horas, sem se espalhar, mas é caso de fronteira. Na prática parece mais "observar/até 24 h" do que "rotina".
- **L4Q07 em geral:** uma picada só com inchaço local muitas vezes nem pede consulta. "Consulta de rotina" é aceitável, mas severo.
- **q121** (veneno, EMERGENCIA, adiamento): o tutor viu o gato comer a isca e o gato ainda não tem sinal nenhum. O rótulo está certo pelas fontes (não esperar sintoma), mas o acerto depende de o sistema dar peso à ingestão, porque não há sinal clínico no texto.
- **q131** (vômito/diarreia piorando, `mas_come_normal`): "come normal" contradiz um animal que piora com vômito contínuo. Usei "água ele bebe normal", seguido de vomitar a água, o que na verdade é sinal de piora.
- **q158** (caroço em gato, 10 anos, crescendo em 6 meses, "rotina"): dá para defender, mas em gatos um caroço costuma merecer avaliação mais breve que em cães. Mantive mole, móvel e sem ferida para ficar dentro do rótulo.

## Observação sobre a espécie
Nos pedidos com `especie` "gato"/"cão" usei sempre macho, para não misturar com os pedidos que dizem "gata"/"cadela".
