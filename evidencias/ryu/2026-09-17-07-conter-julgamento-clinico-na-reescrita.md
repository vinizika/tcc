# Conter julgamento clínico na reescrita (B-08)

**Data:** 17/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 7 · **Commit:** este

## O que foi feito

`QueryClient.rewrite` ganhou duas camadas de contenção contra o problema
registrado em B-08: o prompt inseria juízo de urgência que o relato do
tutor não tinha (*"meu gato está espirrando"* → *"gato apresentando
espirro, sintoma que requer avaliação veterinária imediata"*).

1. **Prompt**: instrução direta contra julgamento de gravidade/urgência,
   mais um exemplo negativo explícito (entrada, saída errada rejeitada,
   saída correta ao lado) — o mesmo caso do espirro que motivou o item.
2. **Guarda-corpo determinístico**: `_contains_unwarranted_urgency`
   compara a reescrita contra o relato original procurando os termos
   "imediata", "imediato", "urgente", "urgência", "emergência" e
   "emergencial". Se algum aparecer na reescrita sem estar no relato, a
   reescrita inteira é descartada e `rewrite` devolve o relato original.

## Por quê

O prompt sozinho já tinha a instrução "nunca adicione informações que não
estavam no relato original" e mesmo assim falhou — é o próprio sintoma que
abriu o item. Um LLM de 3B não segue instrução negativa com confiabilidade
suficiente para um critério de "zero inserções"; só um guarda-corpo
determinístico garante isso por construção. O prompt melhora a taxa de
acerto (menos vezes que o guarda-corpo precisa agir); o guarda-corpo
garante o critério mesmo quando o prompt falha.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Descartar a reescrita inteira, não tentar limpar só o trecho ofensivo | Editar a frase gerada por regex arrisca produzir uma reescrita gramaticalmente quebrada; o relato original é sempre uma opção segura e válida como consulta (é o que o pipeline já busca quando a reescrita está desligada) |
| 2 | Lista fechada de termos, não um classificador | O critério do próprio B-08 já é escrito em termos de string ("zero inserções de 'imediata', 'urgente' ou 'emergência'"); uma lista é auditável e não depende de outra chamada ao modelo |
| 3 | Comparar contra o relato original, não contra uma lista de termos proibidos sempre | Um tutor que já disse "acho que é uma emergência" não deve ter a palavra descartada da reescrita — só a inserção não solicitada é o problema |

## Resultado esperado

_Escrito antes de rodar._ Esperava que o guarda-corpo nunca disparasse
nos exemplos do próprio prompt (positivos), e sempre disparasse no
exemplo negativo documentado no item (espirro → "imediata").

## Resultado obtido

Dois testes novos em `test_query_client.py`:

- Reescrita que injeta "imediata" sem o termo estar no relato original →
  descartada, `rewrite` devolve o relato original.
- Reescrita que usa "emergência" quando o próprio tutor já disse
  "acho que é uma emergência" → mantida.

Suíte completa do backend: 205 → **207 passed**.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/clients/query_client.py` | prompt com instrução + exemplo negativo; função `_contains_unwarranted_urgency`; `rewrite` descarta a reescrita quando ela introduz urgência não solicitada |
| `backend/tests/test_query_client.py` | 2 testes novos |
| `evidencias/backlog.md` | B-08 marcado Resolvido em 17/09 |

## Observações

O guarda-corpo cobre só os seis termos citados no critério do item — não
generaliza para sinônimos ("crítico", "grave", "risco de vida"). Se a
régua de recuperação ou a autópsia de algum caso mostrar um sinônimo
escapando, a lista cresce; não vale generalizar antes de ver o problema
de novo.

## Deixado para depois

**Investigar por que a reescrita sozinha perde do relato cru em recall**
(observação da rodada 6) — pode ser o mesmo mecanismo (vocabulário técnico
demais, mesmo sem urgência), mas essa rodada só ataca a inserção de
julgamento clínico, não a métrica de recuperação. Vale medir de novo com
`measure_query_techniques.py` quando houver mais casos.

## Próximo passo

B-56 (autenticação/política aberta do Supabase) é o próximo item aberto
do meu trilho, seguido de B-07 (latência da etapa de consulta).
