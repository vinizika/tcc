from pathlib import Path
from datetime import datetime, timedelta
import re

import pandas as pd
import streamlit as st

try:
    import pydeck as pdk
except Exception:
    pdk = None

st.set_page_config(page_title="Triagem Veterinária Mock", page_icon="🐾", layout="wide")

# ============================================================
# MOCK 100% HARD CODED
# - Sem LLM
# - Sem backend
# - Sem banco de dados
# - Sem geolocalização real
# ============================================================

RELATO_PADRAO = (
    "Meu cachorro Thor está estranho desde hoje cedo. Ele está muito quieto, "
    "parece cansado, não quis comer direito e agora está deitado respirando mais rápido. "
    "Estou preocupado porque isso não é normal para ele."
)

TUTOR = {
    "nome": "João Pedro",
    "telefone": "(11) 98765-4321",
}

PERFIL_ANIMAL = {
    "nome": "Thor",
    "especie": "Cachorro",
    "raca": "Bulldog Francês",
    "idade": "8 anos",
    "peso": "12,4 kg",
    "historico": [
        "Histórico de intolerância ao calor",
        "Episódios anteriores de tosse após esforço",
        "Vacinação em dia",
        "Sem alergias medicamentosas registradas",
    ],
}

MENSAGEM_INICIAL_ASSISTENTE = (
    f"Olá! Eu sou o assistente de triagem veterinária.\n\n"
    f"Já estou contextualizado com o histórico do {PERFIL_ANIMAL['nome']}, "
    "incluindo intolerância ao calor, episódios anteriores de tosse após esforço, "
    "vacinação em dia e ausência de alergias medicamentosas registradas.\n\n"
    f"Descreva o que está acontecendo com o {PERFIL_ANIMAL['nome']} para que eu possa te orientar."
)

LOCALIZACAO_TUTOR = {
    "nome": "Tutor - localização simulada",
    "lat": -23.6939,
    "lon": -46.5654,
}

CLINICAS = [
    {
        "id": "vitalvet",
        "aba": "Clínica - VitalVet",
        "nome": "Hospital Veterinário VitalVet 24h",
        "lat": -23.6889,
        "lon": -46.5577,
        "distancia": "1,4 km",
        "tempo": "6 min",
        "avaliacao": "4,8",
        "endereco": "Av. Central, 1200 - São Bernardo do Campo",
        "atendimento": "Emergência 24h, oxigenioterapia e internação",
    },
    {
        "id": "animalcare",
        "aba": "Clínica - AnimalCare",
        "nome": "Clínica AnimalCare Emergências",
        "lat": -23.7015,
        "lon": -46.5591,
        "distancia": "2,1 km",
        "tempo": "9 min",
        "avaliacao": "4,6",
        "endereco": "Rua das Acácias, 85 - São Bernardo do Campo",
        "atendimento": "Clínica geral, emergência e exames rápidos",
    },
    {
        "id": "petlife",
        "aba": "Clínica - PetLife",
        "nome": "Centro Veterinário PetLife",
        "lat": -23.6994,
        "lon": -46.5799,
        "distancia": "3,3 km",
        "tempo": "13 min",
        "avaliacao": "4,7",
        "endereco": "Rua Marechal Mock, 410 - São Bernardo do Campo",
        "atendimento": "Emergência, cardiologia e imagem",
    },
]

PRIMEIROS_CUIDADOS = [
    "Mantenha o Thor em local fresco, calmo e ventilado.",
    "Evite esforço físico até a avaliação veterinária.",
    "Não ofereça medicamentos por conta própria.",
    "Não force água ou alimento se ele estiver desconfortável.",
    "Procure atendimento veterinário o quanto antes.",
]

CUIDADOS_NAO_EMERGENCIAIS = [
    "Mantenha o Thor em um ambiente calmo, fresco e ventilado.",
    "Ofereça água em pequenas quantidades, sem forçar a ingestão.",
    "Observe se ele volta a se alimentar e interagir normalmente nas próximas horas.",
    "Evite exercícios, calor intenso ou brincadeiras agitadas no momento.",
    "Se surgirem novos sinais, piora do comportamento, vômitos, desmaio ou dificuldade respiratória, procure uma clínica veterinária.",
]

SINTOMA_CHAVE_OFEGANCIA = "Dyspnea"

ESPECIALIDADE_SUGERIDA = "Clínica emergencial / suporte respiratório"

ETAPAS_FLUXO = {
    "inicio": {"label": "Relato inicial", "progresso": 15},
    "pergunta_ofegante": {"label": "Pergunta decisória", "progresso": 35},
    "orientacao": {"label": "Emergência identificada", "progresso": 60},
    "orientacao_nao_emergencial": {"label": "Orientação não emergencial", "progresso": 60},
    "continuacao_conversa": {"label": "Investigação adicional", "progresso": 45},
    "busca_clinica": {"label": "Busca por clínica", "progresso": 80},
    "clinica_notificada": {"label": "Clínica notificada", "progresso": 100},
}

# Mapeamento simples de termos em português para sintomas existentes no dataset.
# O sintoma só é exibido se existir nas colunas symptoms1...symptoms5 do CSV.
MAPEAMENTO_SINTOMAS = [
    {
        "sintoma_dataset": "Tiredness",
        "termos": ["cansado", "cansada", "cansaço", "quieto", "quieta", "prostrado", "prostrada"],
    },
    {
        "sintoma_dataset": "Appetite Loss",
        "termos": ["não quis comer", "nao quis comer", "sem apetite", "não comeu", "nao comeu", "recusa alimentar"],
    },
    {
        "sintoma_dataset": "Breathing Difficulty",
        "termos": ["respirando", "respiração", "respiracao", "ofegante", "ofegância", "falta de ar", "dificuldade para respirar"],
    },
    {
        "sintoma_dataset": "Coughing",
        "termos": ["tosse", "tossindo", "tossiu"],
    },
    {
        "sintoma_dataset": "Lethargy",
        "termos": ["letargia", "muito parado", "deitado", "fraco", "fraqueza"],
    },
]


# ============================================================
# DATASET DE SINTOMAS
# ============================================================

def obter_caminhos_dataset():
    pasta_atual = Path(__file__).resolve().parent
    raiz_projeto = pasta_atual.parent

    return [
        raiz_projeto / "data" / "processed" / "dataset1_augmented_llm_validated.csv",
        pasta_atual / "dataset1_augmented_llm_validated.csv",
        raiz_projeto / "dataset1_augmented_llm_validated.csv",
    ]


@st.cache_data
def carregar_sintomas_validos():
    for caminho in obter_caminhos_dataset():
        if caminho.exists():
            df = pd.read_csv(caminho)
            colunas_sintomas = [col for col in df.columns if col.lower().startswith("symptoms")]

            sintomas = set()
            for coluna in colunas_sintomas:
                valores = df[coluna].dropna().astype(str).str.strip()
                sintomas.update(valor for valor in valores if valor)

            return sintomas, str(caminho)

    return set(), "Dataset não encontrado"


SINTOMAS_VALIDOS_DATASET, CAMINHO_DATASET_USADO = carregar_sintomas_validos()


def sintoma_existe_no_dataset(nome_sintoma):
    return nome_sintoma in SINTOMAS_VALIDOS_DATASET


def identificar_sintomas_validos(relato, resposta_ofegante=None):
    texto = f"{relato or ''} {resposta_ofegante or ''}".lower()
    sintomas_identificados = []

    for regra in MAPEAMENTO_SINTOMAS:
        sintoma = regra["sintoma_dataset"]

        if not sintoma_existe_no_dataset(sintoma):
            continue

        encontrou_termo = any(termo in texto for termo in regra["termos"])

        if encontrou_termo and sintoma not in sintomas_identificados:
            sintomas_identificados.append(sintoma)

    # Pergunta decisória do mock:
    # a resposta "Sim" confirma um quinto sintoma respiratório validado pelo dataset.
    if resposta_ofegante == "Sim" and sintoma_existe_no_dataset(SINTOMA_CHAVE_OFEGANCIA):
        if SINTOMA_CHAVE_OFEGANCIA not in sintomas_identificados:
            sintomas_identificados.append(SINTOMA_CHAVE_OFEGANCIA)

    return sintomas_identificados[:5]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def obter_clinica_por_id(clinica_id):
    for clinica in CLINICAS:
        if clinica["id"] == clinica_id:
            return clinica
    return None


def obter_clinica_por_aba(nome_aba):
    for clinica in CLINICAS:
        if clinica["aba"] == nome_aba:
            return clinica
    return None


def extrair_minutos(texto_tempo):
    resultado = re.search(r"\d+", texto_tempo or "")
    if not resultado:
        return 0
    return int(resultado.group())


def resumir_relato_tutor(relato):
    # Mock hard coded: resumo textual sem LLM.
    return (
        f"O tutor relata que {PERFIL_ANIMAL['nome']} está quieto, cansado, com recusa alimentar "
        "e respiração acelerada desde hoje cedo."
    )


def navegar_para(tela_destino, rerun=False):
    st.session_state.navegar_para = tela_destino
    if rerun:
        st.rerun()


# ============================================================
# ESTADO DA DEMONSTRAÇÃO
# ============================================================

def iniciar_estado():
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": MENSAGEM_INICIAL_ASSISTENTE,
                "autor": "Assistente de Triagem",
                "origem": "ia",
                "horario": datetime.now().strftime("%H:%M"),
            }
        ]

    if "etapa" not in st.session_state:
        st.session_state.etapa = "inicio"

    if "tela" not in st.session_state:
        st.session_state.tela = "Tutor - Chat"

    if "relato" not in st.session_state:
        st.session_state.relato = RELATO_PADRAO

    if "resposta_ofegante" not in st.session_state:
        st.session_state.resposta_ofegante = None

    if "classificacao" not in st.session_state:
        st.session_state.classificacao = "Inconclusiva"

    if "clinica_selecionada" not in st.session_state:
        st.session_state.clinica_selecionada = None

    if "relato_enviado_clinica" not in st.session_state:
        st.session_state.relato_enviado_clinica = False

    if "feed_clinicas" not in st.session_state:
        st.session_state.feed_clinicas = {clinica["id"]: [] for clinica in CLINICAS}

    # Mantido apenas para compatibilidade com versões antigas do mock.
    if "feed_clinica" not in st.session_state:
        st.session_state.feed_clinica = []


def corrigir_origens_mensagens_antigas():
    for mensagem in st.session_state.get("mensagens", []):
        if "origem" not in mensagem:
            mensagem["origem"] = "tutor" if mensagem.get("role") == "user" else "ia"

        if mensagem.get("role") == "user" and mensagem.get("origem") == "ia":
            mensagem["origem"] = "tutor"

        if "autor" not in mensagem:
            if mensagem.get("origem") == "tutor":
                mensagem["autor"] = TUTOR["nome"]
            elif mensagem.get("origem") == "clinica":
                mensagem["autor"] = "Clínica"
            else:
                mensagem["autor"] = "Assistente de Triagem"

        if "horario" not in mensagem:
            mensagem["horario"] = datetime.now().strftime("%H:%M")


def reiniciar_mock():
    for chave in list(st.session_state.keys()):
        del st.session_state[chave]
    iniciar_estado()


def adicionar_mensagem(role, content, autor=None, origem=None):
    if origem is None:
        origem = "tutor" if role == "user" else "ia"

    if autor is None:
        if origem == "tutor":
            autor = TUTOR["nome"]
        elif origem == "clinica":
            autor = "Clínica"
        else:
            autor = "Assistente de Triagem"

    mensagem = {
        "role": role,
        "content": content,
        "autor": autor,
        "origem": origem,
        "horario": datetime.now().strftime("%H:%M"),
    }
    st.session_state.mensagens.append(mensagem)
    return mensagem


def obter_caso_clinica_ativo():
    clinica = st.session_state.get("clinica_selecionada")
    if not clinica:
        return None

    casos = st.session_state.feed_clinicas.get(clinica["id"], [])
    if not casos:
        return None

    return casos[0]


def sincronizar_chat_no_caso_ativo():
    caso = obter_caso_clinica_ativo()
    if caso is not None:
        caso["chat_completo"] = list(st.session_state.mensagens)


def enviar_mensagem_clinica(clinica_id):
    texto = st.session_state.get(f"mensagem_clinica_{clinica_id}", "").strip()
    if not texto:
        return

    clinica = obter_clinica_por_id(clinica_id)
    nome_clinica = clinica["nome"] if clinica else "Clínica"

    adicionar_mensagem(
        "assistant",
        texto,
        autor=nome_clinica,
        origem="clinica",
    )
    sincronizar_chat_no_caso_ativo()
    st.session_state[f"mensagem_clinica_{clinica_id}"] = ""


def enviar_mensagem_tutor_para_clinica():
    texto = st.session_state.get("mensagem_tutor_clinica", "").strip()
    if not texto:
        return

    adicionar_mensagem(
        "user",
        texto,
        autor=TUTOR["nome"],
        origem="tutor",
    )
    sincronizar_chat_no_caso_ativo()
    st.session_state.mensagem_tutor_clinica = ""


def atualizar_classificacao_por_resposta(resposta):
    if resposta == "Sim":
        return "Emergência provável"
    if resposta == "Não":
        return "Não emergencial aparente"
    return "Inconclusiva - continuar investigação"


def obter_sintomas_identificados():
    if st.session_state.etapa == "inicio":
        return []

    return identificar_sintomas_validos(
        st.session_state.relato,
        st.session_state.resposta_ofegante,
    )


def montar_triagem_simulada():
    classificacao = st.session_state.classificacao

    if classificacao == "Emergência provável":
        nivel = "Vermelho"
        primeiros_cuidados = PRIMEIROS_CUIDADOS
    elif classificacao == "Não emergencial aparente":
        nivel = "Verde"
        primeiros_cuidados = CUIDADOS_NAO_EMERGENCIAIS
    else:
        nivel = "Cinza"
        primeiros_cuidados = []

    return {
        "classificacao": classificacao,
        "nivel": nivel,
        "especialidade": ESPECIALIDADE_SUGERIDA,
        "sinais_detectados": obter_sintomas_identificados(),
        "primeiros_cuidados": primeiros_cuidados,
    }


# ============================================================
# AÇÕES DO FLUXO
# ============================================================

def enviar_relato():
    relato = st.session_state.get("relato_digitado", RELATO_PADRAO).strip()

    if not relato:
        relato = RELATO_PADRAO

    st.session_state.relato = relato

    adicionar_mensagem("user", relato)
    adicionar_mensagem(
        "assistant",
        (
            "Entendi. Sinto muito que o Thor esteja passando por isso. "
            "Pelo histórico dele e pelo que você descreveu, alguns sinais já foram identificados. "
            "Agora preciso de uma pergunta-chave para fechar a pré-triagem: "
            "ele está ofegante ou respirando com dificuldade?"
        ),
    )

    st.session_state.etapa = "pergunta_ofegante"


def responder_ofegante(resposta):
    st.session_state.resposta_ofegante = resposta
    st.session_state.classificacao = atualizar_classificacao_por_resposta(resposta)
    adicionar_mensagem("user", resposta)

    if resposta == "Sim":
        texto_resposta = (
            "Obrigado por confirmar. Essa resposta funciona como uma pergunta decisória no mock: "
            f"ela adiciona o sintoma **{SINTOMA_CHAVE_OFEGANCIA}** à lista de sintomas identificados e altera a classificação para **Emergência provável**.\n\n"
            "Pelo relato, pelo histórico do Thor e pela confirmação de ofegância/dificuldade respiratória, recomendo atendimento veterinário imediato. "
            "Isso ainda não é um diagnóstico definitivo, mas é um sinal de alerta importante, principalmente em um cão braquicefálico.\n\n"
            "Enquanto você se desloca: mantenha-o em local fresco e ventilado, evite esforço físico, não dê medicamentos sem orientação "
            "e não force água ou comida. A seguir, você pode buscar uma clínica próxima."
        )
        st.session_state.etapa = "orientacao"

    elif resposta == "Não":
        texto_resposta = (
            "Entendi. Como você respondeu que o Thor **não** está ofegante nem com dificuldade para respirar, "
            "a pré-triagem simulada não recomenda ida imediata à clínica neste momento.\n\n"
            "A classificação foi atualizada para **Não emergencial aparente**. Ainda assim, continue observando o comportamento dele. "
            "Você pode mantê-lo em um ambiente calmo e fresco, oferecer água em pequenas quantidades, evitar esforço físico e observar se o apetite e a disposição melhoram.\n\n"
            "Caso apareçam sinais como piora importante, vômitos persistentes, desmaio, dor intensa, gengivas arroxeadas ou dificuldade respiratória, procure atendimento veterinário."
        )
        st.session_state.etapa = "orientacao_nao_emergencial"

    else:
        texto_resposta = (
            "Sem problema. Quando o tutor não consegue confirmar esse sinal, o sistema não fecha a classificação ainda.\n\n"
            "Nesta versão demonstrativa, vou simular a continuação da conversa: eu faria novas perguntas sobre frequência respiratória, coloração da gengiva, presença de tosse, desmaio, dor, vômitos e nível de consciência antes de recomendar ou não a ida imediata à clínica."
        )
        st.session_state.etapa = "continuacao_conversa"

    adicionar_mensagem("assistant", texto_resposta)


def abrir_mapa():
    if st.session_state.etapa == "orientacao":
        st.session_state.etapa = "busca_clinica"
    navegar_para("Tutor - Mapa")


def selecionar_clinica(clinica):
    st.session_state.clinica_selecionada = clinica
    st.session_state.relato_enviado_clinica = True
    st.session_state.classificacao = st.session_state.classificacao or "Emergência provável"
    st.session_state.etapa = "clinica_notificada"

    triagem = montar_triagem_simulada()
    horario_alerta_dt = datetime.now()
    minutos_ate_chegada = extrair_minutos(clinica["tempo"])
    chegada_prevista_dt = horario_alerta_dt + timedelta(minutes=minutos_ate_chegada)

    mensagem_confirmacao = (
        f"A clínica {clinica['nome']} já recebeu o relato do {PERFIL_ANIMAL['nome']}, "
        f"incluindo os sintomas identificados, o histórico do animal e a previsão de chegada de {clinica['tempo']}."
    )

    adicionar_mensagem("assistant", mensagem_confirmacao)

    caso_clinica = {
        "horario_alerta": horario_alerta_dt.strftime("%H:%M"),
        "chegada_prevista": chegada_prevista_dt.strftime("%H:%M"),
        "clinica": clinica,
        "relato": st.session_state.relato,
        "resumo_relato": resumir_relato_tutor(st.session_state.relato),
        "resposta_ofegante": st.session_state.resposta_ofegante,
        "animal": PERFIL_ANIMAL,
        "tutor": TUTOR,
        "triagem": triagem,
        "respostas_dadas": [
            {"pergunta": "O animal está ofegante ou respirando com dificuldade?", "resposta": st.session_state.resposta_ofegante or "Não informado"},
        ],
        "primeiros_cuidados_orientados": triagem["primeiros_cuidados"],
        "chat_completo": list(st.session_state.mensagens),
    }

    if "feed_clinicas" not in st.session_state:
        st.session_state.feed_clinicas = {clinica_item["id"]: [] for clinica_item in CLINICAS}

    # Cada clínica recebe apenas os casos direcionados para ela.
    st.session_state.feed_clinicas[clinica["id"]].insert(0, caso_clinica)

    # Mantido para compatibilidade com versões antigas do mock.
    st.session_state.feed_clinica = st.session_state.feed_clinicas[clinica["id"]]

    navegar_para("Tutor - Chat", rerun=True)


iniciar_estado()
corrigir_origens_mensagens_antigas()

# ============================================================
# ABAS SUPERIORES
# ============================================================

ABAS = ["Tutor - Chat", "Tutor - Mapa"] + [clinica["aba"] for clinica in CLINICAS]

if "tela" not in st.session_state or st.session_state.tela not in ABAS:
    st.session_state.tela = "Tutor - Chat"

if "aba_visualizacao" not in st.session_state or st.session_state.aba_visualizacao not in ABAS:
    st.session_state.aba_visualizacao = st.session_state.tela

if "navegar_para" in st.session_state:
    destino = st.session_state.navegar_para
    if destino in ABAS:
        st.session_state.tela = destino
        st.session_state.aba_visualizacao = destino
    del st.session_state.navegar_para

tela_escolhida = st.radio(
    "Visualização",
    ABAS,
    index=ABAS.index(st.session_state.tela),
    key="aba_visualizacao",
    horizontal=True,
    label_visibility="collapsed",
)

st.session_state.tela = tela_escolhida

st.title("Triagem Veterinária")

# ============================================================
# MENU LATERAL ESQUERDO
# ============================================================

st.sidebar.title("Perfil do animal")
st.sidebar.write(f"**Nome:** {PERFIL_ANIMAL['nome']}")
st.sidebar.write(f"**Idade:** {PERFIL_ANIMAL['idade']}")
st.sidebar.write(f"**Peso:** {PERFIL_ANIMAL['peso']}")
st.sidebar.write(f"**Espécie:** {PERFIL_ANIMAL['especie']}")
st.sidebar.write(f"**Raça:** {PERFIL_ANIMAL['raca']}")

st.sidebar.divider()

st.sidebar.subheader("Resumo simulado da triagem")

etapa_atual = ETAPAS_FLUXO.get(st.session_state.etapa, ETAPAS_FLUXO["inicio"])
st.sidebar.write(f"**Etapa atual:** {etapa_atual['label']}")
st.sidebar.progress(etapa_atual["progresso"])

st.sidebar.write(f"**Classificação:** {st.session_state.classificacao}")

sintomas_identificados = obter_sintomas_identificados()
st.sidebar.write("**Sintomas:**")
if sintomas_identificados:
    for sintoma in sintomas_identificados:
        st.sidebar.write(f"- {sintoma}")
else:
    st.sidebar.write("Aguardando identificação")

if st.session_state.clinica_selecionada:
    st.sidebar.write(f"**Clínica:** {st.session_state.clinica_selecionada['nome']}")
else:
    st.sidebar.write("**Clínica:** Aguardando seleção")

st.sidebar.caption(f"Sintomas validados pelo dataset: {len(SINTOMAS_VALIDOS_DATASET)} termos carregados.")

st.sidebar.divider()

if st.sidebar.button("Reiniciar demonstração"):
    reiniciar_mock()
    st.rerun()


# ============================================================
# COMPONENTES VISUAIS
# ============================================================

user_avatar = "👤"
assistant_avatar = "✨"
clinica_avatar = "🏥"

def mostrar_mensagens_chat():
    for mensagem in st.session_state.mensagens:
        autor = mensagem.get("autor")
        origem = mensagem.get("origem", "ia")

        if origem == "clinica":
            with st.chat_message("assistant", avatar=clinica_avatar):
                st.write(f"**{autor}:**")
                st.write(mensagem["content"])

        elif origem == "ia":
            with st.chat_message("assistant", avatar=assistant_avatar):
                st.write(mensagem["content"])

        elif origem == "tutor":
            with st.chat_message("user", avatar=user_avatar):
                st.write(mensagem["content"])

        else:
            with st.chat_message(mensagem["role"]):
                st.write(mensagem["content"])


def mostrar_mapa_simulado():
    pontos_mapa = [
        {
            "lat": LOCALIZACAO_TUTOR["lat"],
            "lon": LOCALIZACAO_TUTOR["lon"],
            "label": LOCALIZACAO_TUTOR["nome"],
            "tipo": "Tutor",
            "color": [33, 150, 243, 220],
            "radius": 180,
        }
    ]

    for clinica in CLINICAS:
        pontos_mapa.append(
            {
                "lat": clinica["lat"],
                "lon": clinica["lon"],
                "label": clinica["nome"],
                "tipo": "Clínica",
                "color": [229, 57, 53, 210],
                "radius": 120,
            }
        )

    df_mapa = pd.DataFrame(pontos_mapa)

    if pdk is None:
        st.warning("PyDeck não está disponível. Exibindo mapa simples como alternativa.")
        st.map(df_mapa, latitude="lat", longitude="lon", size="radius")
        return

    camada_pontos = pdk.Layer(
        "ScatterplotLayer",
        data=df_mapa,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
    )

    visualizacao_inicial = pdk.ViewState(
        latitude=LOCALIZACAO_TUTOR["lat"],
        longitude=LOCALIZACAO_TUTOR["lon"],
        zoom=13,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=visualizacao_inicial,
            layers=[camada_pontos],
            tooltip={"text": "{tipo}: {label}"},
        )
    )

    col1, col2 = st.columns(2)
    with col1:
        st.info("🔵 Tutor: localização simulada")
    with col2:
        st.error("🔴 Clínicas/Hospitais veterinários")


def mostrar_chat_completo(chat_completo):
    for mensagem in chat_completo:
        autor = mensagem.get("autor") or ("Tutor" if mensagem["role"] == "user" else "Assistente")
        horario = mensagem.get("horario")
        origem = mensagem.get("origem", "ia")

        cabecalho = autor
        if horario:
            cabecalho = f"{autor} • {horario}"

        if origem == "clinica":
            with st.chat_message("assistant", avatar=clinica_avatar):
                st.write(f"**Clínica: {cabecalho}**")
                st.write(mensagem["content"])

        elif origem == "ia":
            with st.chat_message("assistant", avatar=assistant_avatar):
                st.write(f"**{cabecalho}**")
                st.write(mensagem["content"])

        elif origem == "tutor":
            with st.chat_message("user", avatar=user_avatar):
                st.write(f"**{cabecalho}**")
                st.write(mensagem["content"])

        else:
            with st.chat_message(mensagem["role"]):
                st.write(f"**{cabecalho}**")
                st.write(mensagem["content"])


def mostrar_feed_caso(caso):
    animal = caso["animal"]
    tutor = caso.get("tutor", TUTOR)
    clinica = caso["clinica"]
    triagem = caso["triagem"]
    sinais = triagem.get("sinais_detectados", [])

    with st.container(border=True):
        st.write(f"### {animal['nome']}")
        st.write(f"**Telefone do tutor:** {tutor['telefone']}")
        st.write(f"**Classificação:** {triagem['classificacao']}")
        st.write(
            f"**Previsão de chegada:** {clinica['tempo']} "
            f"(alerta às {caso['horario_alerta']} + {clinica['tempo']} = chegada prevista às {caso['chegada_prevista']})"
        )
        st.write(f"**Horário do alerta:** {caso['horario_alerta']}")
        st.write("**Sintomas identificados:**")
        if sinais:
            for sinal in sinais:
                st.write(f"- {sinal}")
        else:
            st.write("Nenhum sintoma validado pelo dataset foi identificado.")
        st.write(f"**Resumo do relato do tutor:** {caso['resumo_relato']}")

    st.write("#### Dados do tutor")
    st.write(f"**Nome:** {tutor['nome']}")
    st.write(f"**Telefone:** {tutor['telefone']}")

    st.write("#### Histórico do animal")
    col_hist_1, col_hist_2 = st.columns(2)
    with col_hist_1:
        st.write(f"**Espécie:** {animal['especie']}")
        st.write(f"**Raça:** {animal['raca']}")
        st.write(f"**Idade:** {animal['idade']}")
        st.write(f"**Peso:** {animal['peso']}")
    with col_hist_2:
        for historico in animal["historico"]:
            st.write(f"- {historico}")

    st.write("#### Respostas dadas")
    for item in caso["respostas_dadas"]:
        st.write(f"**{item['pergunta']}**")
        st.write(item["resposta"])

    #st.write("#### Primeiros cuidados orientados")
    #for cuidado in caso["primeiros_cuidados_orientados"]:
    #    st.write(f"- {cuidado}")

    st.write("#### Chat completo")
    mostrar_chat_completo(caso["chat_completo"])

    st.warning(
        "Mock demonstrativo: em uma versão real, este painel receberia dados estruturados via backend/API."
    )


# ============================================================
# TELAS
# ============================================================


def tela_tutor_chat():
    mostrar_mensagens_chat()

    if st.session_state.etapa == "inicio":
        st.text_area(
            "Mensagem pronta para envio",
            value=st.session_state.relato,
            key="relato_digitado",
            height=140,
        )
        st.button("Enviar relato", type="primary", on_click=enviar_relato)

    elif st.session_state.etapa == "pergunta_ofegante":
        st.write("Responder pergunta:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Sim", type="primary", on_click=responder_ofegante, args=("Sim",), use_container_width=True)
        with col2:
            st.button("Não", on_click=responder_ofegante, args=("Não",), use_container_width=True)
        with col3:
            st.button("Não sei", on_click=responder_ofegante, args=("Não sei",), use_container_width=True)

    elif st.session_state.etapa == "orientacao":
        st.button("Encontrar clínica", type="primary", on_click=abrir_mapa)

    elif st.session_state.etapa == "orientacao_nao_emergencial":
        st.info(
            "Fluxo encerrado como não emergencial aparente. Neste caso, o mock não libera o encaminhamento imediato para clínica."
        )

    elif st.session_state.etapa == "continuacao_conversa":
        st.info(
            "Nesta amostra, a conversa adicional foi apenas simulada. Em uma versão completa, novas perguntas seriam feitas antes da classificação final."
        )

    elif st.session_state.etapa == "busca_clinica":
        st.info("Abra a aba Tutor - Mapa para selecionar uma clínica próxima.")
        if st.button("Ir para o mapa", type="primary"):
            navegar_para("Tutor - Mapa", rerun=True)

    elif st.session_state.etapa == "clinica_notificada":
        st.success("A clínica selecionada recebeu o relato simulado do tutor.")

        st.write("#### Conversa com a clínica")
        st.caption("A partir deste ponto, o chat continua entre tutor e clínica, sem interferência da IA.")
        st.text_area(
            "Responder para a clínica",
            key="mensagem_tutor_clinica",
            placeholder="Digite uma resposta para a equipe da clínica...",
            height=90,
        )
        st.button(
            "Enviar mensagem para a clínica",
            on_click=enviar_mensagem_tutor_para_clinica,
            use_container_width=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ver mapa", use_container_width=True):
                navegar_para("Tutor - Mapa", rerun=True)
        with col2:
            clinica = st.session_state.clinica_selecionada
            destino = clinica["aba"] if clinica else "Clínica - VitalVet"
            if st.button("Visualizar painel da clínica", use_container_width=True):
                navegar_para(destino, rerun=True)


def tela_tutor_mapa():
    st.subheader("Mapa de clínicas próximas")
    st.write("Mapa simulado com a posição do tutor e algumas clínicas/hospitais veterinários próximos.")

    if st.session_state.etapa in ["inicio", "pergunta_ofegante"]:
        st.warning("Para a demonstração ficar completa, primeiro envie o relato e responda à pergunta de triagem no chat.")

    if st.session_state.etapa in ["orientacao_nao_emergencial", "continuacao_conversa"]:
        st.info(
            "Neste cenário, o sistema ainda não recomenda o encaminhamento imediato para uma clínica. "
            "Volte ao chat para visualizar a orientação da triagem."
        )
        return

    if st.session_state.etapa == "orientacao":
        st.session_state.etapa = "busca_clinica"

    coluna_mapa, coluna_clinicas = st.columns([1.4, 1])

    with coluna_mapa:
        mostrar_mapa_simulado()

    with coluna_clinicas:
        st.subheader("Clínicas encontradas")

        for clinica in CLINICAS:
            with st.container(border=True):
                st.write(f"**{clinica['nome']}**")
                st.write(clinica["endereco"])
                st.write(f"Distância: {clinica['distancia']}")
                st.write(f"Tempo estimado: {clinica['tempo']}")
                st.write(f"Avaliação: ⭐ {clinica['avaliacao']}")
                st.write(f"Atendimento: {clinica['atendimento']}")

                if st.button("Selecionar clínica", key=f"selecionar_{clinica['id']}"):
                    selecionar_clinica(clinica)


def tela_clinica_painel(clinica_id):
    clinica = obter_clinica_por_id(clinica_id)

    if not clinica:
        st.error("Clínica não encontrada no mock.")
        return

    st.subheader(f"Feed da clínica: {clinica['nome']}")
    st.write("Tela simulando o recebimento antecipado dos casos direcionados para esta clínica.")

    casos = st.session_state.feed_clinicas.get(clinica_id, [])

    if not casos:
        st.info(
            "Feed vazio para esta clínica. Quando o tutor selecionar esta unidade no mapa, "
            "o relato aparecerá somente aqui."
        )
        return

    for indice, caso in enumerate(casos, start=1):
        st.write(f"## Caso {indice}")
        mostrar_feed_caso(caso)

        st.write("#### Enviar mensagem ao tutor")
        st.caption("Mensagem manual da clínica para o tutor. Ela será adicionada ao mesmo histórico do chat, sem resposta da IA.")
        st.text_area(
            "Mensagem da clínica",
            key=f"mensagem_clinica_{clinica_id}_{indice}",
            placeholder="Ex.: Estamos aguardando vocês. Mantenha o Thor em local ventilado durante o trajeto.",
            height=90,
        )
        if st.button("Enviar mensagem ao tutor", key=f"enviar_clinica_{clinica_id}_{indice}"):
            texto = st.session_state.get(f"mensagem_clinica_{clinica_id}_{indice}", "").strip()
            if texto:
                st.session_state[f"mensagem_clinica_{clinica_id}"] = texto
                enviar_mensagem_clinica(clinica_id)
                st.rerun()
            else:
                st.warning("Digite uma mensagem antes de enviar.")

        st.divider()


if st.session_state.tela == "Tutor - Chat":
    tela_tutor_chat()
elif st.session_state.tela == "Tutor - Mapa":
    tela_tutor_mapa()
else:
    clinica_atual = obter_clinica_por_aba(st.session_state.tela)
    if clinica_atual:
        tela_clinica_painel(clinica_atual["id"])
    else:
        st.error("Tela não encontrada no mock.")
