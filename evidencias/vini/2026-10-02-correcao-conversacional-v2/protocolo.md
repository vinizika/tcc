# Segunda execução corretiva — histórico legível

A primeira correção recuperou 34/36 e todos os diálogos novos, mas a rechecagem
do histórico antigo de c03 teve uma resposta INCERTO em seis chamadas com hash
de prompt idêntico. O resultado negativo fica preservado na pasta irmã
`2026-10-02-correcao-conversacional`, inclusive hashes e logs.

Alteração adicional: o histórico de classificação deixa de conter RULES + JSON.
Apresenta os relatos anteriores e o relato atual, em ordem, com cada pergunta
identificada como pergunta do assistente, não observação do tutor. A primeira
classificação permanece byte a byte igual. Nenhum caso específico ou palavra de
alarme recebe regra especial. O classificador e seus prompts científicos não mudam.

Reexecutar o protocolo principal completo: mesmos 18 casos, duas repetições,
baseline antiga intercalada; oito diálogos até formulário e inspeção das opções
antes de escolher respostas que expressem somente os mesmos fatos congelados.
Depois executar três pares de c03 novo e três pares com as mensagens/pergunta/
resposta exatas de 28/09. Os resultados desta pasta não substituem a primeira
tentativa: são uma nova execução, com banco `tcc_followup_eval_20261002_v2`.

Os critérios continuam os mesmos: pelo menos 34/36 e recall emergencial 18/18,
sem regressões pareadas; entradas clínicas iguais e resultados concordantes nos
canais observados; oito controles sem fatos novos devem continuar INCERTO.
Temperatura zero e seed não garantem determinismo absoluto de serviço remoto.
Nenhum ajuste de produto durante a execução. Instabilidade residual será relatada.
