"""One observation per question, selected by the LLM, never a classification rule.

Keys and wording are immutable within this version. An unsupported discriminator
ends the interview instead of fabricating a question. Options are self-contained
so they can also be typed freely without depending on channel metadata.
"""

QUESTIONS = {
    "urine_output": ("Quantidade de urina", "Quanto xixi você observou sair?",
        ["Sai uma quantidade normal de xixi", "Sai pouco xixi", "Não sai nenhum xixi"]),
    "breathing_effort": ("Esforço para respirar", "Como está o esforço para respirar?",
        ["Respira sem esforço aparente", "Faz esforço para respirar"]),
    "responsiveness": ("Resposta ao chamado", "Como ele reage quando você o chama?",
        ["Reage ao chamado como de costume", "Reage menos que de costume ao chamado", "Não reage ao chamado"]),
    "appetite": ("Quantidade de comida ingerida", "Quanto ele comeu em relação ao habitual?",
        ["Comeu a quantidade habitual", "Comeu menos que o habitual", "Não comeu nada", "Comeu mais que o habitual"]),
    "vomiting_frequency": ("Frequência de vômito", "Quantas vezes ele vomitou desde que você percebeu a mudança?",
        ["Não vomitou", "Vomitou uma vez", "Vomitou mais de uma vez"]),
    "abdomen_size": ("Tamanho da barriga", "Como está o tamanho da barriga em relação ao habitual?",
        ["A barriga está do tamanho habitual", "A barriga está maior que o habitual"]),
    "stool": ("Consistência das fezes", "Como está a consistência das fezes?",
        ["As fezes estão com a consistência habitual", "As fezes estão mais moles ou líquidas", "As fezes estão mais duras"]),
    "mobility": ("Capacidade de andar", "Como ele está andando?",
        ["Anda como de costume", "Anda com dificuldade", "Não consegue andar"]),
    "pain": ("Sinais observados de dor", "Você percebe sinais de dor nele?",
        ["Não percebo sinais de dor", "Percebo sinais de dor"]),
    "bleeding_amount": ("Quantidade de sangramento", "Quanto sangramento você observou?",
        ["Não observei sangramento ao olhar", "Observei pouco sangramento", "Observei muito sangramento"]),
    "discharge": ("Aspecto da secreção", "Qual é o aspecto da secreção que você viu?",
        ["Não há secreção visível", "A secreção é transparente", "A secreção tem sangue", "A secreção parece pus"]),
    "eye_opening": ("Abertura do olho", "Como está a abertura do olho?",
        ["O olho abre normalmente", "O olho fica parcialmente fechado", "O olho não abre"]),
    "onset": ("Início da mudança", "Quando você percebeu essa mudança pela primeira vez?",
        ["Não percebo mais essa mudança", "Percebi a mudança hoje", "Percebi a mudança há alguns dias", "Percebi a mudança há semanas ou meses"]),
    "exposure": ("Contato com substância suspeita", "Você viu contato com alguma substância que possa fazer mal?",
        ["Observei e não houve contato com substância suspeita", "Vi contato com uma substância suspeita"]),
    "gum_color": ("Cor da gengiva já observada", "Se você já conseguiu ver sem forçar a boca, como estava a cor da gengiva?",
        ["A gengiva estava com a cor habitual", "A gengiva estava muito pálida", "A gengiva estava azulada ou arroxeada", "A gengiva estava diferente de outra forma"]),
    "water_intake": ("Quantidade de água ingerida", "Quanto ele bebeu em relação ao habitual?",
        ["Bebeu a quantidade habitual", "Bebeu menos que o habitual", "Não bebeu água", "Bebeu mais que o habitual"]),
}

OTHER_OPTION = "Nenhuma dessas opções descreve o que observei"
UNKNOWN_OPTIONS = ["Não observei", "Não sei dizer"]
