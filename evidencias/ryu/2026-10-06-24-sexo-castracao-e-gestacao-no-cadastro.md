# Sexo, castração e gestação no cadastro do pet

**Data:** 06/10/2026 · **Trilho:** B1, no app (parte do Vinicius) · **Rodada:** 24 · **Commit:** este

## O que foi feito

O cadastro do pet ganhou três campos opcionais: **sexo** (macho/fêmea),
**castrado(a)** (sim/não/não sei) e, só para fêmeas, **prenhe ou amamentando**.
Eles vão:

- para a **IA que decide**, junto com o resto do cadastro (bloco "Dados
  cadastrais do animal" do prompt) e na seleção de pergunta do acompanhamento;
- para o **resumo enviado à clínica** quando o tutor encaminha o caso (antes, o
  resumo descartaria campos novos sem avisar);
- para as telas: cartão do animal, revisão antes do envio e painel da clínica.

## Por quê

Melhoria 3 da lista aprovada pelo Ryu em 06/10. Na
[rodada 20](2026-10-06-20-o-cadastro-do-pet-ajuda.md), sexo, castração e
gestação decidiram **3 dos 8 pares** de casos (obstrução urinária no gato macho,
piometra na fêmea não castrada, eclâmpsia na cadela amamentando) e não existiam
no formulário: só funcionaram porque
foram escritos no campo livre de histórico, o que um tutor real pode não fazer.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Os três campos são opcionais, com "Não informar"/"Não sei" | O formulário diz "preencha o que souber"; o tutor com pressa não pode ficar preso |
| 2 | "Prenhe ou amamentando" só aparece para fêmea, e o backend recusa a combinação com macho (422) | Evita dado impossível chegando à IA |
| 3 | Um pet sem os campos novos gera **exatamente o mesmo texto** de contexto de antes | Paridade com tudo o que já foi medido; há teste para isso |
| 4 | A lista de campos que vão à IA virou uma constante só (`ANIMAL_CONTEXT_FIELDS`), usada pela decisão e pela seleção de pergunta | Estava repetida em dois arquivos; um campo novo esquecido num deles chegaria à decisão e não à pergunta |

## Resultado esperado

_Escrito antes de testar._ O formulário mostra os três campos; um pet salvo
com eles aparece no cartão e chega à IA no formato `sex: femea; neutered: False;
reproductive_status: amamentando`; pets antigos continuam iguais; a suíte do
backend e a compilação do frontend passam.

## Resultado obtido

**Funcionou.** Testes automáticos: backend 344 → **346** (2 novos: os campos
são salvos e validados, e chegam à IA; o pet sem eles gera o texto de antes),
todos passando com os padrões do time. Frontend: `npm run build` (com a checagem
de tipos do TypeScript) passou na imagem Docker.

**Conferido no app, no navegador** (localhost, conta fictícia de tutor): o
formulário "Cadastrar animal" mostra "Sexo", "Castrado(a)?" e, ao escolher
fêmea, "Está prenhe ou amamentando?". Um animal de teste salvo como fêmea, não
castrada, amamentando aparece no cartão como **"Cachorro · 3 anos · Fêmea · não
castrada · amamentando"**. O animal de teste ("Mel (teste)") ficou salvo no
MongoDB local da conta fictícia.

**O que esta rodada não mede:** se os campos melhoram a decisão. A rodada 20 já
mostrou que o cadastro pesa para o lado da segurança quando esses fatos estão
escritos; aqui o ganho é o tutor conseguir informá-los. Os testes de navegador
do app (Playwright) não rodaram nesta máquina.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/schemas/workspace.py` | os três campos em `AnimalInput`, a validação e `ANIMAL_CONTEXT_FIELDS` |
| `backend/app/schemas/referral.py` | os três campos no resumo do pet enviado à clínica |
| `backend/app/services/workspace_service.py`, `followup_service.py` | usam `ANIMAL_CONTEXT_FIELDS` |
| `backend/tests/test_workspace.py` | 2 testes |
| `frontend-react/src/types.ts`, `api.ts` | o tipo `Pet` e o envio dos campos |
| `frontend-react/src/components/PetForm.tsx` | os campos no formulário e `describeSexAndStatus()` |
| `frontend-react/src/components/ShareReview.tsx`, `pages/TutorFlow.tsx`, `pages/ClinicDashboard.tsx` | mostram sexo, castração e gestação |

## Próximo passo

Avisar o Vinicius, dono do app, e seguir para a melhoria 4 (rotas antigas do
Supabase).
