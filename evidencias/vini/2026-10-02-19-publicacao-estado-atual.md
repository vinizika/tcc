# Rodada 19 — disponibilização do estado atual para a equipe

## Decisão de 02/10/2026

O usuário pediu para documentar a interpretação da avaliação, commitar o sistema
como está e abrir um PR para disponibilizar o trabalho à equipe. Esta publicação
preserva o comportamento avaliado. As correções identificadas ficam explícitas
como pendências; não são misturadas ao resultado do experimento.

Ao atualizar as referências do GitHub, constatou-se que o frontend React
remodelado e a integração anterior já estão na `main`, pelo PR #15, commit de
merge `4b7ba4a`. O novo PR parte dessa base e acrescenta o acompanhamento de
INCERTO, formulário integrado ao chat, persistência, testes e evidências.

## O que a avaliação permite concluir

Não foi demonstrado que o formulário, isoladamente, piorou o sistema. A queda de
94,4% para 83,3% ocorreu na classificação inicial do conjunto das mudanças, antes
da resposta ao formulário, em 18 casos de calibração repetidos duas vezes por
versão. Foram dois casos que regrediram nas duas repetições; um era emergência.
Os rótulos da calibração são provisórios, não uma validação clínica independente.

A investigação encontrou regras e JSON de orquestração no texto enviado à busca
vetorial. Ao retirar apenas isso no experimento, os dois casos voltaram à classe
esperada em ambas as repetições. A alteração foi exploratória e não foi aplicada
silenciosamente ao produto que será commitado.

O acompanhamento conseguiu concluir casos quando recebeu fatos suficientes e
manteve INCERTO nos oito controles sem informação nova. Isso verifica o mecanismo,
mas não demonstra que pessoas observam/respondem melhor por causa do formulário.
Também foram observadas limitações concretas:

- um formulário não oferecia a opção verdadeira de alimentação normal;
- o mesmo relato grave foi classificado de modo diferente conforme a origem
  texto/formulário, inclusive em rechecagens;
- uma chave de pergunta foi reutilizada com mudança de informação solicitada;
- uma pergunta combinava duas informações em um item.

A decisão é compartilhar a POC e manter a ideia do formulário, sem afirmar que
ela já foi aprovada ou descartada pela avaliação. Próxima etapa técnica:
separar a consulta clínica dos metadados, corrigir a consistência entre canais e
a cobertura das opções, e repetir a comparação. O PR não representa aprovação
para uso clínico nem implantação em URL pública.

## Evidências e validação disponíveis

- [Avaliação completa](2026-09-28-17-avaliacao-pre-triagem-conversacional.md):
  145 turnos reais, 185 chamadas lógicas ao Gemini, matrizes, latências e consumo.
- [Artefatos reproduzíveis](2026-09-28-avaliacao-conversacional/README.md): entradas
  congeladas, resultados brutos, transcrições, auditoria, scripts e hashes.
- [Fechamento de 01/10](2026-10-01-18-fechamento-avaliacao-conversacional.md):
  integridade conferida e métricas regeneradas de forma idêntica.
- Última rodada completa: 330 testes backend, 221 de scripts, sete testes de
  navegador e build React passaram. Não são anunciados como nova execução hoje.

Fichas, rótulos e coleção ativa permanecem preservados. As evidências históricas
que dizem “sem commit/push” descrevem o momento dessas rodadas; a decisão atual
é posterior. Nenhum segredo de `.env` faz parte da publicação. O pedido autoriza
commit, push da branch e abertura de PR; não inclui merge ou deploy remoto.

Na preparação do commit, o diff de código e documentação passou na checagem
de espaços. Os CSVs e a transcrição gerada do pacote congelado têm finais CRLF
e espaços de formatação apontados pelo Git; foram preservados byte a byte para
manter os hashes e a reprodutibilidade das evidências.
