# Conversas e braços pareados

Relatos sintéticos; respostas, perguntas e classificações são reais. Revisão das opções: agente de engenharia, sem validação clínica. As entradas/fatos foram congelados em `cases.json`; veja `actions.json` e `auditoria-formularios.csv`.

## c01

Fato final reservado: Ele tenta fazer xixi repetidamente há oito horas, faz força e não sai nenhuma gota de urina.

**tutor**

> Meu gato está diferente quando vai à caixa de areia. Não consegui ver o que aconteceu.

**assistant**

> O relato não traz informação suficiente para decidir a urgência.
> Procure atendimento veterinário na dúvida.
> O gato esta conseguindo urinar normalmente quando vai a caixa de areia?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informação suficiente para decidir a urgência.
> Procure atendimento veterinário na dúvida.
> Você consegue notar se sai alguma quantidade de urina ou se ele passa muito tempo na caixa sem urinar?

Estado: `form`. Opções: ["Sai apenas algumas gotas", "Não sai nada de urina", "Parece urinar normalmente", "Não observei", "Não sei dizer"]

Revisão: Pergunta sobre saída de urina, alinhada ao relato. Preset expressa parte do sinal; complemento inclui esforço/duração.

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 3.98 s.

> O relato não traz informações suficientes sobre a urina e o comportamento na caixa para decidir.
> Procure atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### before_same_text

Entrada: Não sai nada de urina — Ele tenta fazer xixi repetidamente há oito horas, faz força e não sai nenhuma gota de urina.

Resultado: `EMERGENCIA`; estado: `form`; duração: 1.72 s.

> **Emergência: procure atendimento agora**
> 
> O gato faz força repetidamente há oito horas sem conseguir urinar, indicando uma obstrução uretral grave.
> 
> **Sinais observados no relato**
> 
> - não sai nenhuma gota de urina
> - tenta fazer xixi repetidamente
> - faz força
> 
> **O que fazer**
> 
> Procure um veterinário agora mesmo.
> 
> **Baseado em**
> 
> - Obstrução uretral — fonte: Case report\: Utility, complications, and short-term outcomes in three dogs managed with percutaneous pigtail cystostomy catheters for urethral obstruction (Frontiers in Veterinary Science, 2023). <https://doi.org/10.3389/fvets.2023.1200406>; 2025 iCatCare consensus guidelines on the diagnosis and management of lower urinary tract diseases in cats (Journal of Feline Medicine and Surgery, 2025). <https://doi.org/10.1177/1098612X241309176>
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_same_text

Entrada: Não sai nada de urina — Ele tenta fazer xixi repetidamente há oito horas, faz força e não sai nenhuma gota de urina.

Resultado: `EMERGENCIA`; estado: `completed`; duração: 2.42 s.

> O gato faz força repetidamente há oito horas e não sai nenhuma gota de urina, indicando obstrução.
> Procure um veterinário agora mesmo.

### after_form

Entrada: Não sai nada de urina — Ele tenta fazer xixi repetidamente há oito horas, faz força e não sai nenhuma gota de urina.

Resultado: `EMERGENCIA`; estado: `completed`; duração: 4.06 s.

> O gato faz força repetidamente há oito horas e não sai nenhuma gota de urina, indicando obstrução.
> Procure atendimento veterinário de emergência imediatamente.


## c02

Fato final reservado: Ele respira com a boca aberta, faz muita força e não consegue se deitar de tanto esforço para respirar.

**tutor**

> Meu gato está com um jeito diferente de respirar, mas não consegui observar como está.

**assistant**

> O relato não traz informações suficientes sobre a respiração para decidir se é uma emergência.
> Procure atendimento veterinário na dúvida.
> O gato esta respirando de boca aberta ou fazendo esforco visivel com a barriga?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informações suficientes sobre a respiração para decidir.
> Procure atendimento veterinário na dúvida.
> O gato esta com a lingua ou gengiva roxa ou azulada?

Estado: `form`. Opções: ["Sim, lingua ou gengiva roxa ou azulada", "Nao, coloracao normal", "Não observei", "Não sei dizer"]

Revisão: Mudou de boca aberta/esforço para cor da mucosa, conservando a chave resp_effort_mouth_open. Fato grave entrou apenas pelo complemento.

### after_form

Entrada: Não observei — Ele respira com a boca aberta, faz muita força e não consegue se deitar de tanto esforço para respirar.

Resultado: `EMERGENCIA`; estado: `completed`; duração: 3.94 s.

> O gato respira com dificuldade, faz muita força e não consegue se deitar.
> Procure um veterinário agora mesmo.

### after_same_text

Entrada: Não observei — Ele respira com a boca aberta, faz muita força e não consegue se deitar de tanto esforço para respirar.

Resultado: `EMERGENCIA`; estado: `completed`; duração: 4.08 s.

> O gato respira com a boca aberta, faz muita força e não consegue deitar devido à dificuldade respiratória grave.
> Procure um veterinário agora mesmo.

### before_same_text

Entrada: Não observei — Ele respira com a boca aberta, faz muita força e não consegue se deitar de tanto esforço para respirar.

Resultado: `EMERGENCIA`; estado: `form`; duração: 2.4 s.

> **Emergência: procure atendimento agora**
> 
> O gato apresenta grande esforço respiratório e respira de boca aberta, indicando risco grave e imediato.
> 
> **Sinais observados no relato**
> 
> - respira com a boca aberta
> - faz muita força para respirar
> - não consegue se deitar devido ao esforço
> 
> **O que fazer**
> 
> Procure atendimento veterinário de urgência imediatamente.
> 
> **Baseado em**
> 
> - Dificuldade respiratória — fonte: Diagnostic performance of lung ultrasound compared to thoracic radiography in non-traumatized dogs and cats with respiratory distress in an emergency setting (Frontiers in Veterinary Science, 2026). <https://doi.org/10.3389/fvets.2026.1790755>
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 3.31 s.

> O relato não traz informações suficientes sobre a respiração para decidir.
> Procure atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.


## c03

Fato final reservado: Agora ele está caído, não consegue levantar e não reage quando eu o chamo e toco nele.

**tutor**

> Meu cachorro está agindo de um jeito diferente hoje. Não consegui observar o que mudou.

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> Procure atendimento veterinário para uma avaliação segura na dúvida.
> Ele recusou alguma refeicao ou cometeu menos do que o habitual?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para decidir.
> Procure atendimento veterinário na dúvida.
> Ele recusou a ultima refeicao oferecida?

Estado: `form`. Opções: ["Sim, recusou", "Comeu tudo normalmente", "Comeu apenas uma pequena quantidade", "Não observei", "Não sei dizer"]

Revisão: Relato inicial inespecífico; pergunta de apetite não alcança o fato final de ausência de resposta. Primeiro texto contém erro lexical: cometeu menos.

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 4.1 s.

> O relato não traz informações suficientes sobre os sintomas do animal para decidir.
> Procure atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### before_same_text

Entrada: Não observei — Agora ele está caído, não consegue levantar e não reage quando eu o chamo e toco nele.

Resultado: `EMERGENCIA`; estado: `form`; duração: 2.05 s.

> **Emergência: procure atendimento agora**
> 
> O animal está caído, não levanta e não reage, indicando risco grave à vida.
> 
> **Sinais observados no relato**
> 
> - caído
> - não consegue levantar
> - não reage
> 
> **O que fazer**
> 
> Procure um veterinário imediatamente, sem esperar.
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_same_text

Entrada: Não observei — Agora ele está caído, não consegue levantar e não reage quando eu o chamo e toco nele.

Resultado: `INCERTO`; estado: `insufficient`; duração: 4.45 s.

> O relato não traz informações suficientes sobre a causa da fraqueza súbita e falta de reação.
> Procure atendimento veterinário imediatamente para uma avaliação segura.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### after_form

Entrada: Não observei — Agora ele está caído, não consegue levantar e não reage quando eu o chamo e toco nele.

Resultado: `EMERGENCIA`; estado: `completed`; duração: 18.39 s.

> O animal está caído, sem conseguir levantar e sem reagir, indicando grave risco.
> Procure um veterinário imediatamente.


## c04

Fato final reservado: Eu observei agora: ele urina uma quantidade normal, sem fazer força nem chorar. Está comendo e brincando normalmente, sem vômitos ou mudança na respiração.

**tutor**

> Meu gato está diferente quando entra na caixa de areia. Não consegui observar direito.

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> Procure um veterinário na dúvida.
> O gato consegue urinar na caixa de areia ou apenas faz esforço sem sair urina?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informações suficientes sobre os sintomas urinários do gato para decidir.
> Na dúvida, procure atendimento veterinário agora.
> Você consegue notar se sai urina quando ele vai à caixa de areia?

Estado: `form`. Opções: ["Sim, sai urina normalmente", "Sim, sai apenas algumas gotas com esforço", "Não sai nada de urina", "Não observei", "Não sei dizer"]

Revisão: Opção de urinar normalmente existe; complemento adiciona somente fatos já congelados.

### after_form

Entrada: Sim, sai urina normalmente — Eu observei agora: ele urina uma quantidade normal, sem fazer força nem chorar. Está comendo e brincando normalmente, sem vômitos ou mudança na respiração.

Resultado: `NAO_EMERGENCIA`; estado: `completed`; duração: 9.48 s.

> O gato urina normalmente, sem esforço, e está ativo e comendo bem.
> Agende uma consulta de rotina para avaliar o comportamento.

### after_same_text

Entrada: Sim, sai urina normalmente — Eu observei agora: ele urina uma quantidade normal, sem fazer força nem chorar. Está comendo e brincando normalmente, sem vômitos ou mudança na respiração.

Resultado: `NAO_EMERGENCIA`; estado: `completed`; duração: 3.79 s.

> O gato urina normalmente, sem esforço, e está ativo e comendo bem.
> Agende uma consulta veterinária de rotina para avaliar o caso.

### before_same_text

Entrada: Sim, sai urina normalmente — Eu observei agora: ele urina uma quantidade normal, sem fazer força nem chorar. Está comendo e brincando normalmente, sem vômitos ou mudança na respiração.

Resultado: `NAO_EMERGENCIA`; estado: `form`; duração: 1.45 s.

> **Não parece emergência**
> 
> O gato urina normalmente, sem esforço, e está ativo, indicando que não há urgência imediata.
> 
> **O que fazer**
> 
> Agende uma consulta de rotina nas próximas 24 horas.
> 
> **Baseado em**
> 
> - Xixi fora do lugar e cistite — fonte: Prevalence, Risk Factors, Pathophysiology, Potential Biomarkers and Management of Feline Idiopathic Cystitis\: An Update Review (Frontiers in Veterinary Science, 2022). <https://doi.org/10.3389/fvets.2022.900847>
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 6.0 s.

> O relato nao traz informacao suficiente sobre a urina ou o esforco para definir a urgencia.
> Procure atendimento veterinario na duvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.


## c05

Fato final reservado: Observei agora que ele comeu a porção habitual inteira e bebeu água normalmente. Está ativo, brincando, sem vômitos, diarreia, dor ou dificuldade para respirar.

**tutor**

> Meu cachorro parece diferente perto da comida. Não consegui observar o que mudou.

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a gravidade do caso.
> Na dúvida, procure atendimento veterinário para uma avaliação segura.
> O cão recusou completamente a refeição ou apenas comeu menos?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informações suficientes sobre o comportamento ou os sintomas do animal para decidir.
> Procure atendimento veterinário na dúvida.
> O cão recusou completamente a refeição ou apenas comeu menos?

Estado: `form`. Opções: ["Recusou completamente", "Comeu menos que o habitual", "Não observei", "Não sei dizer"]

Revisão: Pergunta pressupõe alteração alimentar e não oferece alimentação normal. Teste recusou inventar negativa/desconhecimento; usou texto livre.

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 3.89 s.

> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> Procure um atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### before_same_text

Entrada: Observei agora que ele comeu a porção habitual inteira e bebeu água normalmente. Está ativo, brincando, sem vômitos, diarreia, dor ou dificuldade para respirar.

Resultado: `NAO_EMERGENCIA`; estado: `form`; duração: 2.14 s.

> **Não parece emergência**
> 
> O animal está ativo, comeu tudo, bebeu água e não apresenta sintomas graves.
> 
> **O que fazer**
> 
> Monitore o comportamento do seu pet em casa.
> 
> **Baseado em**
> 
> - Vômito isolado ou fezes moles em animal ativo — fonte: Utility of diagnostic tests in vomiting dogs presented to an internal medicine emergency service (Frontiers in Veterinary Science, 2023). <https://doi.org/10.3389/fvets.2023.1063080>
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_same_text

Entrada: Observei agora que ele comeu a porção habitual inteira e bebeu água normalmente. Está ativo, brincando, sem vômitos, diarreia, dor ou dificuldade para respirar.

Resultado: `NAO_EMERGENCIA`; estado: `completed`; duração: 2.25 s.

> O animal comeu toda a porção, bebeu água e está ativo, sem apresentar sinais de gravidade.
> Monitore o cão em casa e aguarde se houver alterações.


## c06

Fato final reservado: Ele vomitou uma única vez ontem depois de comer depressa. Desde então come e bebe normalmente, está ativo, não tem dor, não vomitou mais e não teve diarreia.

**tutor**

> Meu cachorro está estranho, acho que alguma coisa mudou na barriga, mas não observei direito.

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a gravidade.
> Procure atendimento veterinário na dúvida.
> Ele recusou alguma refeicao ou apresentou vomito?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a gravidade.
> Na dúvida, procure um atendimento veterinário para avaliação.
> O cachorro comeu normalmente hoje ou apresentou algum episódio de vômito?

Estado: `form`. Opções: ["Comeu tudo normalmente sem vômito", "Comeu menos que o habitual", "Recusou a refeição e vomitou", "Não observei", "Não sei dizer"]

Revisão: Pergunta combina alimentação e vômito, duas informações em um só item; opção referente a hoje é compatível, com temporalidade esclarecida no complemento.

### after_form

Entrada: Comeu tudo normalmente sem vômito — Ele vomitou uma única vez ontem depois de comer depressa. Desde então come e bebe normalmente, está ativo, não tem dor, não vomitou mais e não teve diarreia.

Resultado: `NAO_EMERGENCIA`; estado: `completed`; duração: 3.78 s.

> O cachorro vomitou apenas uma vez ontem após comer rápido, mas está ativo, comendo e bebendo normalmente.
> Monitore o cão e consulte um veterinário se houver piora dos sintomas.

### after_same_text

Entrada: Comeu tudo normalmente sem vômito — Ele vomitou uma única vez ontem depois de comer depressa. Desde então come e bebe normalmente, está ativo, não tem dor, não vomitou mais e não teve diarreia.

Resultado: `NAO_EMERGENCIA`; estado: `completed`; duração: 3.97 s.

> O animal come, bebe, está ativo e sem vômitos recentes, indicando um quadro leve.
> Monitore o cão e procure uma consulta comum se os sintomas retornarem.

### before_same_text

Entrada: Comeu tudo normalmente sem vômito — Ele vomitou uma única vez ontem depois de comer depressa. Desde então come e bebe normalmente, está ativo, não tem dor, não vomitou mais e não teve diarreia.

Resultado: `NAO_EMERGENCIA`; estado: `form`; duração: 1.52 s.

> **Não parece emergência**
> 
> O animal vomitou apenas uma vez e continua ativo, comendo e bebendo normalmente.
> 
> **O que fazer**
> 
> Monitore o pet em casa e aguarde uma consulta de rotina se necessário.
> 
> **Baseado em**
> 
> - Vômito isolado ou fezes moles em animal ativo — fonte: Utility of diagnostic tests in vomiting dogs presented to an internal medicine emergency service (Frontiers in Veterinary Science, 2023). <https://doi.org/10.3389/fvets.2023.1063080>
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 3.71 s.

> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> Procure atendimento veterinário na dúvida para uma avaliação.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.


## c07

Fato final reservado: Nenhuma informação nova

**tutor**

> Meu gato está estranho hoje. Não consigo explicar o que mudou.

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> Na dúvida, procure atendimento veterinário para uma avaliação segura.
> Ele recusou alguma refeição ou está comendo menos que o habitual?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a gravidade.
> Procure um veterinário na dúvida para avaliar o animal.
> Ele recusou alguma refeicao ou esta comendo menos que o habitual?

Estado: `form`. Opções: ["Comeu tudo normalmente", "Recusou refeicoes", "Comeu menos que o habitual", "Não observei", "Não sei dizer"]

Revisão: Relato inespecífico e observações desconhecidas. Formulário não cria informação.

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 4.51 s.

> O relato não traz informações suficientes sobre os sintomas do animal para definir a gravidade.
> Procure atendimento veterinário na dúvida para uma avaliação.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### before_same_text

Entrada: Não observei

Resultado: `INCERTO`; estado: `form`; duração: 1.49 s.

> **Não foi possível determinar a urgência**
> 
> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> 
> **O que fazer**
> 
> Procure atendimento veterinário na dúvida.
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_same_text

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 18.77 s.

> O relato não traz informações suficientes sobre sintomas claros para definir a urgência do atendimento.
> Procure atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### after_form

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 4.01 s.

> O relato não traz informações suficientes sobre os sintomas do animal para definir a gravidade.
> Procure atendimento veterinário na dúvida para uma avaliação.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.


## c08

Fato final reservado: Nenhuma informação nova

**tutor**

> Meu cachorro não parece ele mesmo hoje, mas não observei nenhum detalhe.

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> Procure atendimento veterinário na dúvida.
> Ele comeu normalmente hoje ou recusou alguma refeicao?

Estado: `asking`. Opções: []

**tutor**

> Não sei dizer

**assistant**

> O relato não traz informações suficientes sobre os sintomas do animal para definir a urgência.
> Procure atendimento veterinário na dúvida.
> Ele recusou alguma refeicao hoje?

Estado: `form`. Opções: ["Sim, recusou", "Comeu normalmente", "Não observei", "Não sei dizer"]

Revisão: Relato inespecífico e observações desconhecidas. Formulário não cria informação.

### after_form

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 5.46 s.

> O relato não traz informações suficientes sobre sintomas claros para definir a urgência do caso.
> Procure atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### after_same_text

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 2.92 s.

> O relato não traz informações suficientes sobre sintomas específicos para definir a gravidade do caso.
> Procure um atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

### before_same_text

Entrada: Não observei

Resultado: `INCERTO`; estado: `form`; duração: 1.68 s.

> **Não foi possível determinar a urgência**
> 
> O relato não traz informações suficientes sobre os sintomas do animal.
> 
> **O que fazer**
> 
> Procure atendimento veterinário na dúvida.
> 
> _Este sistema apoia a pré-triagem e não substitui a avaliação de um médico-veterinário._

### after_no_data

Entrada: Não observei

Resultado: `INCERTO`; estado: `insufficient`; duração: 3.99 s.

> O relato não traz informações suficientes sobre sintomas claros para definir a urgência do caso.
> Procure atendimento veterinário na dúvida.
> Ainda não há informação suficiente para determinar a urgência. Entre em contato com uma clínica; se houver piora, procure atendimento agora. Você pode enviar novas observações.

