"""
Gera os pedidos de escrita da prova 2 (rodada 28 do João; desenho na rodada 20).

A prova 2 tem 330 relatos: 5 por quadro de emergência do mapa (38 x 5 = 190),
5 por quadro leve (23 x 5 = 115) e 25 casos especiais. Quem escreve os relatos
são agentes de IA isolados, que **não veem** o mapa, as fichas nem a prova 1.
Este script é o orquestrador: ele lê o mapa e escreve, para cada relato, um
pedido com o que o autor pode saber:

- o quadro em linguagem leiga (texto deste arquivo, não do mapa nem das fichas);
- a espécie e o sexo do animal do relato;
- a gravidade que o relato precisa ter (é o rótulo);
- o tom, a família de frase calma, o quadro com que o relato deve se parecer
  (a "gêmea"), se usa "mas" e se pode trazer um palpite de diagnóstico;
- uma persona de tutor.

As correções do piloto (rodada 20) estão nos pedidos, não só na instrução:
"mas" em 2 de cada 5 relatos das duas classes; no máximo 1 palpite em cada 5
(o relato "gêmea"); quatro famílias de frase calma e relatos calmos sem frase
pronta.

Saída, em ``data/prova2/geracao/pedidos/``:

- ``lote_<n>.json``: os pedidos completos (com o tópico do mapa e o rótulo),
  que a montagem usa;
- ``lote_<n>.instancia.json``: só o que o autor do lote pode ver.

Uso:

    python scripts/prova2_pedidos.py            # grava os 9 lotes
    python scripts/prova2_pedidos.py --check    # confere que os arquivos estão em dia
"""

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MAPA = RAIZ / "data" / "curadoria" / "mapa-de-assuntos.csv"
DESTINO = RAIZ / "data" / "prova2" / "geracao" / "pedidos"
SEMENTE = 20260925
LOTES_DE_QUADROS = 8

# O quadro em linguagem leiga. Escrito para esta prova, sem copiar a coluna de
# sinais do mapa nem as fichas: é o que o autor pesquisa, não o que ele copia.
LEIGO = {
    "chocolate_toxicosis": "cachorro que comeu chocolate",
    "allium_toxicosis": "comeu cebola ou alho (comida temperada, sopa, resto de comida)",
    "respiratory_distress": "dificuldade para respirar",
    "seizures": "convulsão (crise em que o animal fica fora de si)",
    "trauma_and_bleeding": "trauma grave: atropelamento, pancada forte, briga feia ou sangramento que não para",
    "urethral_obstruction": "não consegue fazer xixi (obstrução urinária)",
    "vomiting_and_diarrhea": "vômito e diarreia que não param, com o animal piorando",
    "canine_heatstroke": "cachorro passando mal de calor (insolação)",
    "gastric_dilatation_volvulus": "barriga inchando de repente e ânsia de vômito sem sair nada (torção de estômago)",
    "fading_neonate": "filhote recém-nascido que não mama e está ficando fraco",
    "acute_hindlimb_paralysis": "de repente parou de mexer ou passou a arrastar as patas de trás",
    "carbamate_organophosphate_poisoning": "envenenamento por chumbinho, veneno de lavoura ou inseticida",
    "anticoagulant_rodenticide_poisoning": "comeu veneno de rato",
    "human_medication_poisoning": "comeu ou recebeu remédio de gente (analgésico, anti-inflamatório, outros)",
    "anaphylaxis_facial_swelling": "reação alérgica forte, com a cara inchando",
    "pyometra": "infecção no útero (piometra) em fêmea não castrada",
    "single_vomiting_or_mild_diarrhea": "vomitou uma vez ou está com as fezes um pouco moles, animal ativo",
    "dietary_indiscretion_mild": "comeu algo que não devia (lixo, comida comum de gente), sem passar mal",
    "mild_upper_respiratory_signs": "espirros e coriza leves, animal bem",
    "tremors_without_seizure": "tremor com o animal acordado e atento (frio, medo, idade), sem convulsão",
    "mild_lameness": "mancando de leve, ainda apoiando a pata",
    "inappropriate_urination_or_cystitis": "xixi fora do lugar ou muitas idas à caixa/ao tapete, conseguindo urinar (cistite)",
    "osteoarthritis_stiffness": "animal idoso mais duro para levantar e andar (artrose)",
    "flea_dermatitis_pruritus": "coceira e pele irritada (pulga, alergia)",
    "normal_estrus": "cadela no cio normal",
    "collapse_and_pale_gums": "desmaiou ou está caído, muito fraco, com a gengiva branca",
    "parvovirus_panleukopenia": "filhote com vômito e diarreia com sangue (parvovirose no cão, panleucopenia no gato)",
    "ocular_emergency": "problema grave no olho (olho para fora, machucado, dor forte, olho fechado de dor)",
    "mild_conjunctivitis": "olho vermelho com remela, abrindo o olho normalmente (conjuntivite leve)",
    "reduced_appetite_no_other_signs": "comendo menos que o normal, sem outro sinal",
    "permethrin_toxicosis_cats": "gato em que passaram antipulgas de cachorro",
    "gastrointestinal_foreign_body": "engoliu um objeto (brinquedo, meia, osso, linha) que ficou preso por dentro",
    "airway_foreign_body_choking": "engasgado com algo preso na garganta, sem conseguir respirar direito",
    "dystocia": "parto que não anda (fêmea em trabalho de parto com dificuldade)",
    "snake_and_scorpion_envenomation": "picada de cobra, escorpião ou aranha",
    "distemper_neurological": "cinomose atacando os nervos (tremedeira, tiques, crises)",
    "leptospirosis_acute": "leptospirose (contato com água de enchente, lama ou rato, e ficou doente)",
    "tick_borne_disease_anemia": "doença do carrapato, com o cão ficando anêmico",
    "congestive_heart_failure": "animal cardíaco que piorou: tosse e cansaço para respirar",
    "hypoglycemia_toy_puppy": "filhote de raça bem pequena com queda de açúcar no sangue",
    "diabetic_ketoacidosis": "animal diabético que ficou muito doente de repente",
    "feline_aortic_thromboembolism": "gato que de repente perdeu o movimento das patas de trás, com muita dor (trombo)",
    "vestibular_syndrome_otitis_interna": "perdeu o equilíbrio de repente: cabeça torta, andando em círculo, caindo",
    "cat_bite_abscess": "gato com ferida ou caroço depois de brigar com outro gato",
    "high_rise_syndrome_cats": "gato que caiu de janela, varanda ou telhado",
    "burns_and_electrical_injury": "queimadura ou choque elétrico (mordeu fio, água quente, fogo)",
    "eclampsia": "cadela amamentando com tremedeira e o corpo endurecendo (falta de cálcio depois do parto)",
    "lily_toxicosis_cats": "gato que mordeu ou lambeu lírio (a flor ou a planta)",
    "grape_xylitol_toxicosis": "cachorro que comeu uva, uva-passa ou doce/chiclete sem açúcar (xilitol)",
    "toad_bufotoxin_poisoning": "cachorro que mordeu ou lambeu sapo",
    "normal_whelping": "parto normal acontecendo, sem complicação",
    "insect_sting_local_reaction": "picada de abelha, vespa ou formiga, com inchaço só no lugar da picada",
    "kennel_cough_mild": "tosse dos canis leve (tosse seca, cão animado)",
    "polyuria_polydipsia_investigate": "bebendo muito mais água e fazendo muito mais xixi que o normal",
    "otitis_externa_mild": "otite leve (coçando a orelha, cera, cheiro)",
    "minor_wound": "ferida pequena e superficial, com o sangramento já parado",
    "periodontal_disease_mild": "tártaro e mau hálito",
    "slow_growing_lump": "caroço que vem crescendo devagar, animal bem",
    "exertional_panting_mild": "cachorro ofegante depois de correr, brincar ou tomar sol, que se recupera",
    "rabies_exposure_wild_animal_bite": "foi mordido ou arranhado por morcego ou animal silvestre e está bem agora",
    "ticks_found_no_signs": "achou carrapatos no animal, que está bem",
}

# Quadros sem par de confusão no mapa: com o que o relato "gêmea" se parece.
GEMEA_SEM_PAR = {
    "fading_neonate": "achar que o filhote só está dormindo muito, como todo recém-nascido",
    "human_medication_poisoning": LEIGO["dietary_indiscretion_mild"],
    "snake_and_scorpion_envenomation": LEIGO["insect_sting_local_reaction"],
    "leptospirosis_acute": LEIGO["reduced_appetite_no_other_signs"],
    "burns_and_electrical_injury": LEIGO["minor_wound"],
    "cat_bite_abscess": LEIGO["trauma_and_bleeding"],
    "periodontal_disease_mild": "um problema grave na boca, com dor forte ou o rosto inchado",
    "rabies_exposure_wild_animal_bite": LEIGO["trauma_and_bleeding"],
}

FEMEA = {"pyometra", "normal_estrus", "dystocia", "normal_whelping", "eclampsia"}

GRAVIDADE = {
    "imediato": ("EMERGENCIA", "emergência: um veterinário mandaria atender agora, sem esperar"),
    "ate_24h": ("NAO_EMERGENCIA", "não é emergência: precisa de consulta nas próximas 24 horas"),
    "rotina": ("NAO_EMERGENCIA", "não é emergência: pode esperar uma consulta de rotina"),
}

# O tom de cada um dos 5 relatos de um quadro (rodada 20, decisão 3).
TONS = {
    "EMERGENCIA": ["calmo", "calmo", "aflito", "neutro", "gemea"],
    "NAO_EMERGENCIA": ["aflito", "aflito", "neutro", "neutro", "gemea"],
}
# Famílias de frase calma (rodada 18; correção 3 do piloto), em rodízio.
FAMILIAS_CALMAS = ["minimizacao", "adiamento", "bem_estar", "mas_come_normal", "sem_frase_pronta"]

PERSONAS = [
    "Senhora de 68 anos em Belo Horizonte (MG), pontuação caprichada e frases longas",
    "Rapaz de 22 anos em Recife (PE), tudo minúsculo, abreviações (vc, pq, tb, blz)",
    "Mãe de dois filhos em Curitiba (PR), mensagem curta e objetiva, no intervalo do trabalho",
    "Estudante de 19 anos em Manaus (AM), gírias e 'kkk', sem acento",
    "Aposentado de 74 anos no interior de São Paulo, escreve devagar, com erros de digitação",
    "Auxiliar de enfermagem de 41 anos em Salvador (BA), descreve com detalhe e horários",
    "Motorista de aplicativo de 35 anos no Rio de Janeiro (RJ), mensagem de áudio transcrita, sem pontuação",
    "Adolescente de 15 anos em Brasília (DF), sozinha em casa, CAPS LOCK e abreviações",
    "Produtor rural de 52 anos no Mato Grosso do Sul, fala simples e direta, termos da roça",
    "Professora de 47 anos em Porto Alegre (RS), 'bah', 'tri', escreve em parágrafos",
    "Programador de 29 anos em Florianópolis (SC), objetivo, faz lista de sinais",
    "Dona de casa de 58 anos em Fortaleza (CE), 'oxe', 'visse', mistura o caso com a vida da família",
    "Casal jovem em Goiânia (GO), quem escreve é o marido, muito ansioso, faz várias perguntas",
    "Senhor de 80 anos em Juiz de Fora (MG), a neta digitou por ele, frases truncadas",
    "Tutora de 33 anos em Campinas (SP) que leu muito na internet e usa alguns termos técnicos do jeito errado",
    "Garçom de 27 anos em Belém (PA), 'égua', mensagem escrita correndo no celular",
    "Advogada de 44 anos em São Paulo (SP), formal, pontuação correta, pede orientação objetiva",
    "Estudante de administração de 21 anos em Londrina (PR), informal, escreve entre uma aula e outra",
    "Pedreiro de 46 anos em Teresina (PI), poucas palavras, sem pontuação",
    "Tutora de 38 anos em Natal (RN), protetora de animais com vários bichos, conta rápido",
    "Enfermeira de 50 anos em Vitória (ES), descreve como se passasse plantão",
    "Jovem de 24 anos em São Luís (MA), mistura português com expressões da internet",
    "Mãe de 31 anos em Uberlândia (MG), 'uai', 'trem', escreve enquanto cuida do bebê",
    "Senhora de 63 anos em Maceió (AL), religiosa, 'meu Deus', 'Nossa Senhora', muito aflita com tudo",
    "Taxista de 57 anos em Porto Velho (RO), texto curto, erros de ortografia",
    "Universitária de 20 anos em Pelotas (RS), divide apartamento, o gato é da república",
    "Cozinheiro de 39 anos em João Pessoa (PB), conta o que o bicho comeu com detalhe",
    "Empresário de 49 anos em Ribeirão Preto (SP), quer resposta rápida, sem paciência",
    "Criança de 12 anos em Aracaju (SE), escreve do celular da mãe, frases simples",
    "Agricultora de 60 anos no oeste do Paraná, sotaque do interior, 'o bichinho'",
    "Designer de 26 anos em Belo Horizonte (MG), escreve como em rede social, com 'gente' e 'socorro'",
    "Policial militar de 43 anos em Cuiabá (MT), seco e direto",
    "Aposentada de 70 anos em Santos (SP), mora sozinha com o gato, carinhosa, conta a rotina dele",
    "Jovem pai de 28 anos em Campo Grande (MS), primeiro animal, não sabe o que é normal",
    "Cuidadora de idosos de 45 anos em Niterói (RJ), escreve à noite, cansada, frases curtas",
    "Estudante do ensino médio de 17 anos em Palmas (TO), abreviações, sem letra maiúscula",
    "Engenheiro de 36 anos em Joinville (SC), detalhista, dá números (horas, vezes, peso)",
    "Vendedora de 34 anos em Manaus (AM), mensagem com áudio transcrito, repete palavras",
    "Senhor de 66 anos em Caruaru (PE), 'visse', 'arretado', fala do bicho como da família",
    "Tutora de 30 anos em Blumenau (SC), mora no apartamento, escreve bem, preocupada com o vizinho",
]

# Os 25 casos especiais (rodada 20): o rótulo é do orquestrador, provisório,
# como todos os outros.
ESPECIAIS = [
    # 10 com informação insuficiente: a resposta certa é INCERTO.
    ("informacao_insuficiente", "o tutor só diz que o gato está 'estranho' hoje, sem contar o que viu", "gato", "INCERTO", ""),
    ("informacao_insuficiente", "pergunta se é grave o cachorro 'não estar legal', sem nenhum sinal concreto", "cão", "INCERTO", ""),
    ("informacao_insuficiente", "conta que a cadela 'está diferente' desde ontem e pede uma opinião, sem dizer o que mudou", "cadela", "INCERTO", ""),
    ("informacao_insuficiente", "diz que o gato 'não parece bem' e que está preocupado, sem nenhum detalhe", "gato", "INCERTO", ""),
    ("informacao_insuficiente", "o cachorro ficou 'meio assim' depois do passeio, sem explicar o quê", "cão", "INCERTO", ""),
    ("informacao_insuficiente", "quer saber se deve se preocupar porque a gata 'mudou o jeito', sem dizer em quê", "gata", "INCERTO", ""),
    ("informacao_insuficiente", "mensagem que começa a contar algo sobre o cachorro e termina no meio, sem chegar ao problema", "cão", "INCERTO", ""),
    ("informacao_insuficiente", "pergunta 'o que pode ser?' dizendo só que o gato anda quieto, sem duração nem outro sinal", "gato", "INCERTO", ""),
    ("informacao_insuficiente", "diz que o filhote 'não está normal' e que a vizinha achou grave, sem dizer o que ela viu", "cão", "INCERTO", ""),
    ("informacao_insuficiente", "relata só uma impressão ('acho que ele está sentindo alguma coisa'), sem sinal, duração ou contexto", "gato", "INCERTO", ""),
    # 8 quadros clínicos reais que o mapa não cobre.
    ("fora_do_mapa_clinico", "cachorro macho com o pênis para fora, que não volta para dentro, inchando e escurecendo", "cão", "EMERGENCIA", "imediato"),
    ("fora_do_mapa_clinico", "animal que ficou horas na chuva ou no frio e está gelado, mole e sem reação", "cão", "EMERGENCIA", "imediato"),
    ("fora_do_mapa_clinico", "depois do parto saiu uma massa vermelha grande pela vulva e ficou para fora (prolapso de útero)", "gata", "EMERGENCIA", "imediato"),
    ("fora_do_mapa_clinico", "uma parte vermelha saindo pelo ânus que não volta (prolapso retal)", "cão", "EMERGENCIA", "imediato"),
    ("fora_do_mapa_clinico", "orelha que inchou como uma almofada, mole, depois de o animal coçar e sacudir a cabeça", "cão", "NAO_EMERGENCIA", "ate_24h"),
    ("fora_do_mapa_clinico", "apareceu uma bolinha vermelha no canto do olho do filhote, que enxerga e brinca normal", "cão", "NAO_EMERGENCIA", "ate_24h"),
    ("fora_do_mapa_clinico", "filhote com um carocinho mole no umbigo (hérnia pequena), comendo e brincando", "gato", "NAO_EMERGENCIA", "rotina"),
    ("fora_do_mapa_clinico", "cachorro arrastando o bumbum no chão e lambendo a região, bem-disposto", "cão", "NAO_EMERGENCIA", "rotina"),
    # 7 perguntas não clínicas.
    ("nao_clinico", "como fazer o gato parar de arranhar o sofá", "gato", "NAO_EMERGENCIA", "rotina"),
    ("nao_clinico", "qual a melhor ração para um filhote de cachorro", "cão", "NAO_EMERGENCIA", "rotina"),
    ("nao_clinico", "quando dar as vacinas do filhote e quantas doses são", "cão", "NAO_EMERGENCIA", "rotina"),
    ("nao_clinico", "com que idade castrar a gata", "gata", "NAO_EMERGENCIA", "rotina"),
    ("nao_clinico", "como levar o cachorro numa viagem longa de carro", "cão", "NAO_EMERGENCIA", "rotina"),
    ("nao_clinico", "de quanto em quanto tempo dar banho no cachorro", "cão", "NAO_EMERGENCIA", "rotina"),
    ("nao_clinico", "adotou um segundo gato e quer saber como apresentar os dois", "gato", "NAO_EMERGENCIA", "rotina"),
]
TONS_ESPECIAIS = ["neutro", "aflito", "neutro", "calmo", "neutro"]

# O que o autor NÃO vê (vai só no arquivo completo).
CAMPOS_DO_ORQUESTRADOR = {"topic", "expected_urgency", "difficulty_tag", "confusion_pair_topic", "lote"}


def ler_mapa() -> list[dict]:
    with MAPA.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def especies_do_quadro(linha: dict, k: int) -> list[str]:
    """As espécies (e o sexo, quando importa) dos 5 relatos de um quadro."""
    topico, esp = linha["id"], linha["especie"]
    if esp == "cao":
        base = ["cão"] * 5
    elif esp == "gato":
        base = ["gato"] * 5
    else:  # ambos: 3 de uma espécie e 2 da outra, alternando entre quadros
        base = ["cão", "gato", "cão", "gato", "cão"] if k % 2 == 0 else ["gato", "cão", "gato", "cão", "gato"]
    if topico in FEMEA:
        base = ["cadela" if e == "cão" else "gata" for e in base]
    return base


def gemea(linha: dict, leigo_por_id: dict) -> tuple[str, str]:
    par = [p for p in linha["par_de_confusao"].split(";") if p]
    if par:
        return par[0], leigo_por_id[par[0]]
    return "", GEMEA_SEM_PAR[linha["id"]]


def distribuir_mas_e_familia(classe: str, tons: list[str], rng: random.Random, contador_familia: list[int]) -> tuple[list[bool], list[str]]:
    """'mas' em 2 dos 5 relatos das duas classes; a família calma em rodízio."""
    familias = [""] * 5
    for i, tom in enumerate(tons):
        if tom == "calmo":
            familias[i] = FAMILIAS_CALMAS[contador_familia[0] % len(FAMILIAS_CALMAS)]
            contador_familia[0] += 1
    mas = [False] * 5
    fixos = [i for i, f in enumerate(familias) if f == "mas_come_normal"]
    for i in fixos:
        mas[i] = True
    livres = [i for i in range(5) if not mas[i] and familias[i] not in ("mas_come_normal",)]
    rng.shuffle(livres)
    for i in livres[: max(0, 2 - len(fixos))]:
        mas[i] = True
    return mas, familias


def gerar() -> dict[int, list[dict]]:
    rng = random.Random(SEMENTE)
    mapa = ler_mapa()
    leigo_por_id = {l["id"]: LEIGO[l["id"]] for l in mapa}
    assert set(leigo_por_id) == set(LEIGO), "LEIGO e o mapa têm quadros diferentes"

    # Quadros em lotes: ordena por classe e etapa e distribui em rodízio, para
    # cada lote ter emergências e leves das duas etapas.
    ordenados = sorted(mapa, key=lambda l: (l["classe"], l["etapa"], l["id"]))
    lote_de = {l["id"]: (i % LOTES_DE_QUADROS) + 1 for i, l in enumerate(ordenados)}

    personas = list(PERSONAS)
    rng.shuffle(personas)
    p_idx = 0
    contador_familia = [0]
    por_lote: dict[int, list[dict]] = {n: [] for n in range(1, LOTES_DE_QUADROS + 2)}

    for k, linha in enumerate(ordenados):
        classe, gravidade = GRAVIDADE[linha["urgencia"]]
        tons = TONS[classe]
        especies = especies_do_quadro(linha, k)
        par_id, par_leigo = gemea(linha, leigo_por_id)
        mas, familias = distribuir_mas_e_familia(classe, tons, rng, contador_familia)
        for i in range(5):
            pedido = {
                "lote": lote_de[linha["id"]],
                "quadro_leigo": LEIGO[linha["id"]],
                "especie": especies[i],
                "classe": classe,
                "gravidade": gravidade,
                "tom": tons[i],
                "familia_calma": familias[i],
                "parecido_com": par_leigo if tons[i] == "gemea" else "",
                "usar_mas": mas[i],
                "palpite_permitido": tons[i] == "gemea",
                "persona": personas[p_idx % len(personas)],
                "topic": linha["id"],
                "expected_urgency": linha["urgencia"],
                "difficulty_tag": _dificuldade(classe, tons[i]),
                "confusion_pair_topic": par_id if tons[i] == "gemea" else "",
            }
            p_idx += 1
            por_lote[pedido["lote"]].append(pedido)

    lote_especial = LOTES_DE_QUADROS + 1
    for j, (tipo, descricao, especie, classe, urgencia) in enumerate(ESPECIAIS):
        pedido = {
            "lote": lote_especial,
            "quadro_leigo": descricao,
            "especie": especie,
            "classe": classe,
            "gravidade": _gravidade_especial(tipo, classe, urgencia),
            "tom": TONS_ESPECIAIS[j % len(TONS_ESPECIAIS)],
            "familia_calma": "",
            "parecido_com": "",
            "usar_mas": j % 5 in (1, 3),
            "palpite_permitido": False,
            "persona": personas[p_idx % len(personas)],
            "topic": "",
            "expected_urgency": urgencia,
            "difficulty_tag": tipo,
            "confusion_pair_topic": "",
        }
        p_idx += 1
        por_lote[lote_especial].append(pedido)

    # O id do relato e uma referência opaca do quadro (o autor grava o caderno
    # de linguagem com ela, sem saber o id do mapa).
    n = 0
    for lote in sorted(por_lote):
        refs: dict[str, str] = {}
        for pedido in por_lote[lote]:
            n += 1
            pedido["id"] = f"q{n:03d}"
            chave = pedido["topic"] or pedido["id"]
            if chave not in refs:
                refs[chave] = f"L{lote}Q{len(refs) + 1:02d}"
            pedido["quadro_ref"] = refs[chave]
    return por_lote


def _dificuldade(classe: str, tom: str) -> str:
    if tom == "gemea":
        return "par_confuso"
    if classe == "EMERGENCIA":
        return "calma_grave" if tom == "calmo" else "controle_emergencia"
    return "alarme_leve" if tom == "aflito" else "controle_leve"


def _gravidade_especial(tipo: str, classe: str, urgencia: str) -> str:
    if tipo == "informacao_insuficiente":
        return ("informação insuficiente: o relato NÃO pode trazer sinal clínico concreto, duração nem "
                "contexto que permita julgar a urgência (a resposta certa de um triador é 'não dá para saber')")
    if tipo == "nao_clinico":
        return "pergunta que não é sobre doença: não há sinal clínico nenhum no relato"
    return GRAVIDADE[urgencia][1]


def para_instancia(pedido: dict) -> dict:
    return {k: v for k, v in pedido.items() if k not in CAMPOS_DO_ORQUESTRADOR}


def conferir(por_lote: dict[int, list[dict]]) -> Counter:
    todos = [p for lote in por_lote.values() for p in lote]
    classes = Counter(p["classe"] for p in todos)
    assert len(todos) == 330, len(todos)
    assert classes == Counter({"EMERGENCIA": 194, "NAO_EMERGENCIA": 126, "INCERTO": 10}), classes
    assert len({p["id"] for p in todos}) == 330
    quadros = Counter(p["topic"] for p in todos if p["topic"])
    assert len(quadros) == 61 and set(quadros.values()) == {5}
    return classes


def renderizar(por_lote: dict[int, list[dict]]) -> dict[str, str]:
    arquivos = {}
    for lote, pedidos in sorted(por_lote.items()):
        arquivos[f"lote_{lote}.json"] = json.dumps(
            {"lote": lote, "semente": SEMENTE, "pedidos": pedidos}, ensure_ascii=False, indent=1) + "\n"
        arquivos[f"lote_{lote}.instancia.json"] = json.dumps(
            {"lote": lote, "pedidos": [para_instancia(p) for p in pedidos]}, ensure_ascii=False, indent=1) + "\n"
    return arquivos


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    por_lote = gerar()
    classes = conferir(por_lote)
    arquivos = renderizar(por_lote)

    if args.check:
        velhos = [n for n, s in arquivos.items()
                  if not (DESTINO / n).exists() or (DESTINO / n).read_text(encoding="utf-8") != s]
        if velhos:
            raise SystemExit(f"pedidos desatualizados: {', '.join(velhos)}; rode python scripts/prova2_pedidos.py")
        print("pedidos da prova 2 em dia")
        return

    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in arquivos.items():
        with open(DESTINO / nome, "w", encoding="utf-8", newline="\n") as f:
            f.write(conteudo)
    tamanhos = {lote: len(p) for lote, p in sorted(por_lote.items())}
    print(f"gravados {len(arquivos)} arquivos em {DESTINO}; por lote: {tamanhos}; por classe: {dict(classes)}")


if __name__ == "__main__":
    main()
