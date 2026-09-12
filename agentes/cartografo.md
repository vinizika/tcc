# Cartógrafo — o mapa de assuntos

Roteiro para construir ou revisar `data/curadoria/mapa-de-assuntos.csv`: a
lista de quadros clínicos que a base deve cobrir e sobre os quais a prova
deve perguntar. Roda uma vez por revisão — a primeira foi em 12/09, e a
próxima é no dia em que a porta de decisão abrir ou quando os especialistas
devolverem a validação.

Este roteiro é a fonte de verdade. O atalho em `.claude/agents/cartografo.md`
só aponta para aqui; quem não usa Claude Code cola este arquivo em qualquer
modelo.

## Entrada

Tudo isto já existe no repositório; o agente **lê antes de escrever**:

| O quê | Onde | Para quê |
|---|---|---|
| O mapa atual, se houver | `data/curadoria/mapa-de-assuntos.csv` | Revisar em vez de refazer. Linha `validada` não se toca sem devolver a `rascunho` |
| As referências e o grau de verificação de cada uma | `data/curadoria/referencias.md` | Toda linha cita um id daqui; fonte nova entra aqui antes de entrar na linha |
| Os casos da régua de recuperação | `data/retrieval/cases.csv` | Todo `expected_topics` precisa de linha; os casos "sem cobertura" são quadros que faltam |
| As fichas JSON da base | `backend/data/documents/*.json` | Todo `topic` indexado precisa de linha; o `id` do mapa **é** esse `topic` |
| Os dois CSVs de checagem | `data/curadoria/vocabulario-dataset1.csv`, `doencas-dataset2.csv` | Cada termo do conjunto de avaliação cai em alguma linha ou é inespecífico com motivo |
| O que o time já decidiu | `evidencias/backlog.md` (B-03, B-50, B-53), `docs/plano-base-e-prova.md` §6 | O critério de cobertura e as decisões de produto (binário + INCERTO; primeira convulsão conservadora) |
| Busca na web | — | Fontes novas, com a regra: **link que não abre não entra** |

## Saída

1. `mapa-de-assuntos.csv` atualizado, com as colunas exatamente como o
   README da pasta descreve (o teste `scripts/tests/test_mapa_de_assuntos.py`
   recusa coluna renomeada, id fora do formato, par órfão e referência
   inexistente).
2. `referencias.md` atualizado — id novo por fonte nova, com `direta`,
   `resumo` ou `bloqueada` dizendo o que foi lido de verdade.
3. Os dois CSVs de checagem atualizados quando uma linha entra ou sai.
4. Um **relato de mudanças**, na conversa e no histórico do README: o que
   entrou, o que saiu, o que mudou de classe ou de etapa, e por quê — para
   os outros dois revisarem sem ler o diff inteiro.

## Passos

1. **Esqueleto por eixos.** Sistema orgânico × classe (emergência / pode
   esperar) × espécie. A grade não pode ter buraco: cada sistema tem
   emergência e tem quadro leve, para cão e para gato.
2. **Lado emergência**, de três entradas: os documentos que a base já tem;
   os casos "sem cobertura" da régua; e referência publicada — a *Veterinary
   Triage List*, a casuística de pronto-socorro (o que chega mais) e as
   casuísticas brasileiras (o que chega mais **aqui**: chumbinho, diclofenaco,
   parvovirose, permetrina). Frequência vira prioridade.
3. **Lado "pode esperar"**, por sistema: as queixas de clínica geral que um
   tutor traz e que podem aguardar. Sem este lado, o sistema só aprende
   emergência — é o critério do B-03.
4. **Par de confusão e discriminador.** Para cada emergência, a gêmea leve
   que usa as mesmas palavras do tutor; para cada par, a **pergunta** que
   separa ("sai alguma coisa quando vomita e a barriga está dura?"). O par
   sempre atravessa as classes. Algumas emergências não têm versão leve
   honesta — o campo fica vazio, não se inventa.
5. **Urgência pelos três níveis do MSD** (`imediato` / `ate_24h` / `rotina`)
   e **classe pela regra de colapso** (`imediato` → emergência; o resto →
   pode esperar). Nunca o contrário.
6. **Referência por linha.** Toda afirmação de classe tem id em
   `referencias.md`. Sem fonte, a linha entra com `SEM_FONTE` e prioridade
   C — declarar a lacuna é melhor que inventar.
7. **Prioridade pela regra** (A / B / C, no README da pasta) e **etapa** pelo
   corte vigente. A etapa 2 fica no esqueleto: completar sinais e
   discriminador dela é para quando a porta de decisão disser "vai".
8. **Checagem cruzada**: cada termo do conjunto de avaliação em alguma linha
   ou marcado inespecífico com motivo; cada doença do `dataset2` com linha ou
   excluída com motivo. Os datasets são **vocabulário, nunca rótulo** — o
   `dataset1` é a prova atual, e usar suas combinações para decidir o que
   entra na base é olhar a chave de resposta.
9. **Rodar o teste** e só então escrever o relato de mudanças.

## Regras

- Toda linha tem referência; referência sem URL que abre não entra.
- `sinais_que_o_tutor_relata` em português leigo, itens separados por `;`,
  **sem frases completas** — a coluna alimenta a base, e a prova é escrita
  a partir do cenário, nunca daqui.
- Espécie explícita; cobertura é conferida por espécie.
- Decisão de produto conservadora onde as fontes divergem: o erro grave em
  pré-triagem é o falso não urgente. Divergência entre fontes fica escrita
  em `observacoes`, para os especialistas decidirem.
- O que ficou de fora fica dito, e por quê (no relato de mudanças ou no
  README).
- Termos brasileiros primeiro: "chumbinho", não "aldicarb", no que o tutor
  relata; o nome técnico vai em `quadro` ou `observacoes`.

## O que ele não faz

- **Não decide verdade clínica.** Propõe, com fonte; os especialistas
  decidem, e a coluna `validacao` registra quem e quando.
- **Não escreve casos de prova nem documentos da base.** É a muralha do
  plano: quem desenha o mapa não escreve o relato que vai medir o sistema.
- **Não altera linha `validada`** sem devolvê-la a `rascunho` com nota em
  `observacoes`.
- **Não inventa referência**, não completa autor ou ano de memória, e não
  promove `bloqueada` a `direta` sem alguém ter aberto a página.
- **Não usa os rótulos do dataset** ("Dangerous") como evidência de classe.
