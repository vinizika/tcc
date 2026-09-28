# Gemini x Ollama, amostra ampliada para 25 casos

**Data:** 23/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 15 · **Commit:** este

## O que foi feito

Ampliei a comparação da rodada 14 (9 casos) com mais 16 casos da régua de
recuperação (b10-b25), usando o mesmo script
([`compare_query_providers.py`](../../backend/app/database/compare_query_providers.py))
e o mesmo teto de segurança para o Gemini. Total: **25 casos**, os mesmos
para os dois provedores.

## Por quê

O usuário aprovou escalar a amostra antes de levar o achado da rodada 14
(2 casos com alucinação clara do Ollama) para decisão do grupo — um número
maior sustenta a conversa melhor que dois exemplos.

## Resultado esperado

_Escrito antes de rodar._ Esperava que o padrão qualitativo da rodada 14
(Gemini sem alucinação, Ollama inventando termos) se repetisse com mais
casos, e não tinha expectativa forte sobre quem ganharia em
Precision@1/MRR — 25 casos ainda é pouco para uma conclusão estatística
forte, só o suficiente para ver se a direção se mantém.

## Resultado obtido

### Quantitativo — Gemini à frente no agregado, mas não em todo caso

| | Ollama | Gemini |
|---|---:|---:|
| Precision@1 (25 casos) | 7/25 (0,280) | 8/25 (0,320) |
| MRR médio | 0,365 | 0,433 |

Olhando caso a caso: Ollama teve o MRR mais alto em **11** dos 25 casos,
Gemini em **9**, empate em **5**. Ou seja, **o Ollama venceu mais vezes
individualmente**, mas o Gemini teve vitórias de margem maior (4 casos em
que Gemini foi de 0 para Precision@1 = 1: `b08`, `b16`, `b17`, `b24`), o
que puxa a média agregada para cima. Não há um vencedor limpo na
recuperação — as duas técnicas de consulta continuam limitadas pelo mesmo
gargalo de sempre (ordenação/reranking), que nenhum modelo de linguagem
sozinho resolve.

### Qualitativo — o padrão de alucinação se confirmou, e piorou de figura

Revisei reescrita e HyDE dos 16 casos novos. Três alucinações claras a
mais, além das duas já registradas na rodada 14:

**`b10` (claudicação leve) — Ollama inventa uma sigla:**
> "...lesão de achatamento do ligamento isquiotibial (**ITL**)..."

Não existe essa lesão nem essa sigla em ortopedia veterinária.

**`b20` (intoxicação por chumbinho) — Ollama se contradiz na própria
frase:**
> Reescrita: "...**miosis (pupila pequena)**..."
> HyDE, na sequência: "...miosis (**pupila dilatada, não pequena**, o que
> sugere hipersalivação e estresse)..."

Miose **significa** pupila pequena — é a definição da palavra. O modelo
afirma a definição certa na reescrita e a contradiz duas frases depois no
HyDE, confundindo miose com midríase. É uma alucinação particularmente
reveladora porque não é um termo exótico: é um erro dentro da própria
definição básica que o modelo acabou de usar corretamente.

**`b23` (parvovirose/panleucopenia) — Ollama inventa uma síndrome
inteira:**
> "...indicando uma resposta imunológica intensa à toxina. **Síndrome de
> Toxina de Gato (FTS)**..."

"Síndrome de Toxina de Gato" e a sigla "FTS" não existem — o quadro é
parvovirose/panleucopenia, que o próprio Gemini identificou corretamente
no mesmo caso (ver abaixo).

**O Gemini, nos mesmos três casos, foi preciso e sem invenção:**

| Caso | Gemini |
|---|---|
| `b10` | "ruptura parcial do ligamento cruzado cranial, osteoartrose incipiente ou tendinopatia do tendão calcâneo comum" — diagnósticos reais, testes ortopédicos reais (gaveta, compressão tibial) |
| `b20` | "miose puntiforme" (consistente, sem contradição), tratamento correto: "atropina como antagonista... uso de oximas como reativadores da acetilcolinesterase" — é o antídoto real de organofosforado/carbamato |
| `b23` | "principais diferenciais... parvovírus felino (panleucopenia)" — nomeou o quadro certo, sem inventar síndrome |

**Contagem final, olhando reescrita + HyDE dos 25 casos:** pelo menos
**5 alucinações claras do Ollama** (doença de Huntington, "hipotirese",
"ligamento isquiotibial ITL", contradição miose/midríase, "Síndrome de
Toxina de Gato"), **zero encontradas no Gemini**.

## O que isso decide, e o que ainda não decide

**Decide:** o padrão da rodada 14 não foi coincidência de 2 casos — com
25, o Ollama segue produzindo erros factuais que um leitor atento (tutor
ou veterinário revisando) notaria como errados, e o Gemini não. Isso é
particularmente sério porque o HyDE nunca é mostrado ao tutor, mas
**alimenta a busca vetorial** — um termo inventado na consulta pode
afastar a busca do documento certo tanto quanto aproximar.

**Ainda não decide:** se isso justifica a complexidade de uma API externa
em produção. A recuperação (Precision@1/MRR) não mostrou a mesma vantagem
clara que a leitura qualitativa mostrou — o gargalo de ordenação da busca
consome parte do benefício de uma consulta mais precisa. Precisaria de uma
amostra bem maior (a régua inteira, 66 casos, ou uma fatia da prova de 150)
e, idealmente, alguém validando as alucinações encontradas com uma
especialista, para virar número de artigo.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `evidencias/ryu/dados/2026-09-23-comparacao-gemini-ollama-lote2.json` | Resultado bruto dos 16 casos novos (b10-b25) |

Nenhuma mudança de código nesta rodada — só execução e leitura do
instrumento já construído na rodada 14.

**Custo:** 48 chamadas ao Gemini nesta rodada, 75 no total do dia (27 + 48),
bem dentro do limite gratuito diário.

## Observações

**Achado que vale registrar à parte:** em `b20`, mesmo o Gemini produzindo
o HyDE clinicamente perfeito (atropina, oximas, agentes
parassimpaticomiméticos), a recuperação **não** trouxe o documento
`carbamate_organophosphate_poisoning` em primeiro para nenhum dos dois
provedores. Ou seja, mesmo quando a consulta em si está impecável, o
gargalo de ordenação da busca (já documentado desde a régua original)
continua consumindo o ganho. Trocar o modelo da consulta não resolve
sozinho um problema que é de reranking/ordenação — reforça que os dois
trilhos (B1 e A) têm que avançar juntos.

## Deixado para depois

**Levar este achado para o grupo antes de qualquer decisão de adoção** —
é o próprio próximo passo pedido.

**Se o grupo decidir seguir**, a pergunta certa não é "trocar tudo para
Gemini", é "vale a pena usar Gemini só no HyDE" — é a etapa que mais
alucina e a que menos depende de latência (roda em paralelo com o
Multi-Query desde a rodada 8).

## Próximo passo

Reportar ao grupo com os dois números (quantitativo misto, qualitativo
favorável ao Gemini) e as 5 alucinações concretas, e perguntar se vale
seguir para uma decisão de adoção parcial (só HyDE) ou encerrar o
experimento aqui.
