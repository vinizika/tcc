# Lote 7 — resumo

35 relatos gravados em `relatos.json` (q236–q270), na ordem dos pedidos, e 7 cadernos em `cadernos/`.

Conferência automática (Python da venv `tccv`, `PYTHONUTF8=1`), que passou sem erros:
- o JSON abre; há 35 relatos com os mesmos ids e na mesma ordem dos pedidos;
- todos os relatos com `usar_mas=true` têm a palavra "mas" e nenhum com `usar_mas=false` a tem (busca por palavra inteira, sem distinguir maiúsculas);
- nenhum relato repete 6 ou mais palavras seguidas das citações entre aspas dos cadernos. Na primeira rodada, 6 relatos falharam por reaproveitarem expressões que eu mesmo tinha sintetizado nos cadernos. Reescrevi esses trechos e conferi de novo. Também removi uma URL de `inspiracao` que não estava no caderno do quadro.

## Fontes por quadro

| Quadro | Tema | Fontes | Em PT |
|---|---|---|---|
| L7Q01 | cachorro que comeu chocolate | 6 (4 lidas + 2 perguntas do JustAnswer, das quais só vi o título) | 2 |
| L7Q02 | piometra | 7 (inclui a página sobre o cio normal, para o caso gêmeo) | 5 |
| L7Q03 | cardíaco que piorou | 3 | 1 |
| L7Q04 | gato que caiu de altura | 3 (inclui um estudo de casos da PMC) | 1 |
| L7Q05 | comeu algo que não devia, sem passar mal | 4 (2 sobre o quadro e 2 sobre chocolate, para o contraste do gêmeo) | 3 |
| L7Q06 | comendo menos, sem outro sinal | 4 | 3 |
| L7Q07 | parto normal | 4 | 0 |

## Dificuldades

- **A cota de buscas acabou cedo.** A cota de buscas na web da sessão (200 buscas, partilhada) se esgotou depois das 4 primeiras. Todo o resto veio de acesso direto a páginas conhecidas e de links internos dessas páginas. Muitos endereços que tentei deduzir deram 404. Não contornei o limite, por exemplo buscando por outro site de busca.
- **Sites que recusaram:**
  - JustAnswer (403): aproveitei só os títulos das perguntas de tutores, que apareceram na busca;
  - Reddit e web.archive.org: bloqueados para a ferramenta;
  - Petlove (403);
  - VCA: uma recusa temporária (429), que depois passou;
  - um PDF de relato de caso da Unicruz, sobre piometra em gata, veio ilegível.
- **Pouca fala real de tutor.** Quase tudo o que consegui ler são páginas informativas de clínicas e blogs. Fala de tutor mesmo só apareceu em três lugares:
  - comentários de leitores na Cobasi e no Perito Animal (piometra);
  - frases de tutor reunidas pela VetôPet (chocolate);
  - os títulos das perguntas do JustAnswer.
  
  Para cardíaco, queda de gato, comer menos e parto, não achei nenhum comentário de tutor. A linguagem desses relatos vem do meu conhecimento de como tutores brasileiros escrevem.
- **Parto (L7Q07) ficou sem fonte em português acessível.**

## Pedidos em que o rótulo ou a combinação me pareceu estranha

Não mudei nenhum rótulo nem pedido.

- **Persona × espécie.** A persona da universitária de Pelotas diz que "o gato é da república", mas a espécie pedida é cão ou cadela em q238, q243, q248, q258, q263 e q268. Adaptei para "o cachorro/a cadela da república". Nos pedidos de gato (q253) ficou como está.
- **Cardíaco em gato (q247, q249).** Gato com o coração descompensando raramente tosse; o sinal principal é o esforço para respirar (boca aberta, respiração rápida parado). Escrevi a tosse como um "barulho tipo tosse/engasgo", secundário. O rótulo EMERGENCIA está correto; só o termo "tosse" do quadro é mais típico de cão.
- **L7Q05, "comeu algo, sem passar mal", com consulta em 24 h.** Sem nenhum sinal, muitos veterinários mandariam apenas observar em casa. Para o rótulo fazer sentido, escolhi ingestões que justificam uma consulta sem pressa:
  - gordura de churrasco em quantidade (q258);
  - guardanapo engordurado (q256);
  - embalagem de chocolate engolida (q260);
  - comida temperada ou salgada em gato (q257, q259).
- **q241 (piometra, `mas_come_normal`).** Uma cadela com piometra que ainda come é possível (na forma aberta, no início), e o quadro continua sendo de atendimento imediato. A combinação torna o caso deliberadamente difícil; acho o rótulo correto.
- **q270 (parto normal, gêmeo do "parto que não anda").** A pausa descrita de "1 hora e pouco" com a mãe calma está dentro do normal: a PDSA dá até 1,5 h entre filhotes. Mas está perto do limite, e alguns veterinários mandariam ao menos ligar. É um caso de fronteira.
- **L7Q07 como "consulta de rotina".** Para um parto normal em andamento, o rótulo é defensável: o parto sem complicação não precisa de veterinário. Mesmo assim, um serviço de triagem tende a pedir contato em caso de dúvida.
