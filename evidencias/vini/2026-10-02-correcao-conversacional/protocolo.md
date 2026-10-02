# Repetição congelada após correções — 02/10/2026

Definido antes das novas chamadas. Mesmos 18 casos de calibração e oito diálogos
da rodada 17, mesmos fatos finais e rótulos provisórios, sem usar prova final.
`cases.json`, `freeze.json` e `baseline_workspace.py` são cópias byte a byte da
rodada 17. Nenhum caso ou rótulo será ajustado após observar os resultados.

Comparação principal: baseline antigo executado novamente versus versão corrigida,
duas repetições por caso, ordem alternada, provedor Gemini real e coleção ativa
preservada. Também comparar separadamente com os resultados históricos do PR #16.
Banco isolado: `tcc_followup_eval_20261002`. Saídas da rodada anterior imutáveis.

Correções em avaliação: consulta vetorial composta somente pelos relatos do tutor;
primeira classificação com relato original; histórico clínico sem origem text/form;
planejador escolhe uma observação em catálogo versionado de perguntas atômicas,
com opções normais/negativas, alterações, alternativa livre e desconhecimento.
O catálogo não contém classes clínicas nem seleciona a classificação. Se nenhuma
observação for pertinente, o serviço mantém INCERTO e encerra o acompanhamento.

Primeiro executar testes de contrato. Depois executar `baseline`, `prepare`,
inspecionar as perguntas realmente selecionadas, fixar `actions.json` usando
somente os fatos congelados e executar `finish`. Repetir três pares extras de
c03, mantendo o mesmo histórico e texto e alternando a origem. Registrar hashes
dos prompts efetivos para verificar igualdade de entradas; isso não promete
determinismo absoluto de um provedor remoto.

Aceitação: recuperar pelo menos a concordância histórica de 34/36 e recall de
emergência de 18/18, sem regressões em casos antes corretos na comparação atual;
igualdade de entrada clínica entre canais e concordância dos pares observados;
todos os controles sem informação nova continuam INCERTO. Cobertura factual e
atomicidade das perguntas são auditadas separadamente dos acertos clínicos.

Resultados negativos, erros e variação do provedor também serão registrados.
Nenhuma alteração de produto durante a rodada; se necessária, abrir outra execução
identificada. Testes com dublês verificam contratos, não acurácia. Esta amostra já
é de desenvolvimento e não permite afirmar eficácia clínica ou benefício humano.

## Verificação adicional de compatibilidade com o histórico v1

Antes de responder aos formulários novos, acrescentou-se uma verificação de
regressão: repetir também três pares de c03 usando exatamente as mensagens,
pergunta/opções e resposta congeladas de 28/09. O runner reconstrói cópias desse
estado no banco novo e executa a implementação corrigida, sem modificar o banco
antigo. A fase `legacy_recheck` é separada dos diálogos principais. Assim, o teste
de canal não depende apenas da pergunta nova escolhida pelo catálogo v2.
