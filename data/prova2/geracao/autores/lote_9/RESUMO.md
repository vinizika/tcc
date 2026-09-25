# Lote 9 — resumo do autor (casos especiais)

25 relatos em `relatos.json` (q306–q330, na ordem de `pedidos.json`), 25 cadernos em `cadernos/`.

## Conferência (Python do tccv, PYTHONUTF8=1)
- O JSON abre; 25 relatos, com os mesmos ids e na mesma ordem dos pedidos.
- "mas" (palavra inteira, sem distinguir maiúsculas): presente nos 10 pedidos com `usar_mas=true`, ausente nos 15 com `false`.
- Nenhum relato repete 6+ palavras seguidas das 209 expressões entre aspas dos cadernos.
- Conferência extra: comparei cada relato com o texto integral das 45 páginas que abriram (artigo + comentários). Duas falhas no q316 ("meu cachorro está com o pênis…" e "…com o pênis de fora e…" aparecem em comentários de leitores). Reescrevi e conferi de novo: zero sobreposições.
- Todos têm de 1 a 6 frases. Toda URL em `inspiracao` está no caderno da situação.

## Fontes por situação
| Quadro | Fontes (detalhe nos cadernos) |
|---|---|
| L9Q01–L9Q10 (informação insuficiente) | Comentários de leitores no PeritoAnimal (gato quieto, como saber se o gato está doente, gato deprimido, depois da tosa, filhote que não come, pênis de cachorro); Bionicão Hospital Veterinário; VetôPet; Medt Veterinária; cats.com; títulos de perguntas do JustAnswer (só o título que a busca mostrou, porque a página deu 403) |
| L9Q11 pênis que não recolhe | PeritoAnimal (anatomia e doenças do pênis, com dezenas de comentários; por que o pênis fica para fora); Wikipedia (Paraphimosis, só para humanos) |
| L9Q12 frio/chuva | PeritoAnimal (hipotermia em cachorros); Cobasi (cachorro sente frio) |
| L9Q13 massa pela vulva pós-parto | Wag! (uterine prolapse in cats); PeritoAnimal (complicações no parto de gatas, com comentários); Cobasi (parto de gato) |
| L9Q14 parte vermelha pelo ânus | Cobasi (prolapso retal em cães); PeritoAnimal (prolapso retal em gatos) |
| L9Q15 orelha como almofada | PeritoAnimal e Cobasi (otohematoma) |
| L9Q16 bolinha vermelha no olho | Cobasi; PeritoAnimal; VCA Hospitals; Wikipedia (Cherry eye); comentários do PeritoAnimal sobre a terceira pálpebra |
| L9Q17 caroço mole no umbigo | PeritoAnimal (hérnia em gatos; hérnia umbilical em cães); Cobasi (gato tem umbigo) |
| L9Q18 arrastar o bumbum | Cobasi (glândula adanal); PeritoAnimal (cheiro de peixe; comentários de "depois da tosa") |
| L9Q19 arranhar o sofá | PeritoAnimal; ASPCA |
| L9Q20 ração de filhote | PeritoAnimal (como escolher a ração, com comentários); Cobasi |
| L9Q21 vacinas do filhote | PeritoAnimal (calendário de vacinas, com comentários); Cobasi |
| L9Q22 idade para castrar a gata | PeritoAnimal (idade ideal, com cerca de 30 comentários); Cobasi |
| L9Q23 viagem de carro | Cobasi (duas páginas); ASPCA |
| L9Q24 frequência de banho | PeritoAnimal (com comentários); Cobasi |
| L9Q25 apresentar dois gatos | PeritoAnimal (duas páginas, uma com comentários); Cobasi |

Todas as situações têm pelo menos 2 fontes e pelo menos 1 em português.

## Dificuldades
- **Busca esgotada cedo.** Depois de 8 buscas, a ferramenta de busca devolveu "orçamento da sessão esgotado (200 de 200)"; o limite parece compartilhado com outros lotes. A partir daí só abri endereços conhecidos e naveguei pelas páginas de categoria dos sites: páginas de seção do PeritoAnimal e sitemap público do blog da Cobasi. Não usei buscador por fora para contornar o limite.
- **Bloqueios que não contornei.** JustAnswer (403), Reddit (bloqueado para a ferramenta), Tudo Sobre Cachorros (bloqueio anti-robô Mod_Security), Petz, Petlove, Dogster e Catster (403). Wag! e VCA deram 429 (limite de requisições) em parte das páginas. O `robots.txt` do PeritoAnimal proíbe sitemap e busca interna, e respeitei isso.
- **Pouca linguagem de tutor em inglês.** Por causa dos bloqueios, a linguagem real de tutores veio quase toda dos comentários do PeritoAnimal. Para os quadros raros (hipotermia, prolapsos, olho, hérnia), os artigos novos quase não têm comentários, e me apoiei nas páginas de orientação e no meu conhecimento.
- **Mensagem interrompida (q312).** Para o tom aflito com corte no meio, parei a mensagem antes de qualquer coisa observada ("quando eu fui chamar ele pra comer"). Os horários da persona são de chegada e de rotina, não de sintoma.

## Rótulos que me pareceram estranhos (não mudei nada)
- **L9Q03 (q308):** o `quadro_leigo` pede "desde ontem", e a `gravidade` diz que o relato não pode trazer duração. Mantive "desde ontem" porque está no quadro. Sem sinal nenhum, a duração sozinha não permite julgar, mas é um conflito entre os dois campos.
- **L9Q08 (q313):** "anda quieto" já é um sinal leve de comportamento. Um triador pode achar que isso basta para "consulta sem pressa" em vez de "não dá para saber".
- **L9Q09 (q314):** "filhote" e "a vizinha achou grave" são contexto que um triador prudente pode usar para mandar atender logo (filhote piora rápido). O rótulo INCERTO se sustenta, mas é fronteiriço.
- **L9Q05 (q310):** "depois do passeio" abre hipóteses graves (calor, algo que comeu, trauma). Também é INCERTO fronteiriço.
- **L9Q07 (q312):** o pânico da tutora e o corte no meio tendem a puxar o sistema para EMERGENCIA. É um caso difícil de propósito, e o rótulo está certo.
- **L9Q13 (q318):** a persona diz "mora sozinha com o gato", e o pedido é "gata" (parto). Segui o campo `especie`.
- **L9Q24:** as fontes divergem sobre a frequência de banho (semanal/quinzenal numa, 4 a 8 semanas na outra). Isso não afeta o rótulo.
