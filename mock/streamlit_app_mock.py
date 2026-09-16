"""Protótipo navegável e independente do fluxo tutor–clínica.

Execute a partir da raiz do repositório:
    python -m streamlit run mock/streamlit_app_mock.py --server.port 8502

Tudo nesta interface é local e simulado. Nenhuma função deste arquivo chama o
backend real, um mapa externo ou uma clínica.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pandas as pd
import streamlit as st

try:
    import pydeck as pdk
except Exception:  # pragma: no cover - exercitado manualmente sem PyDeck
    pdk = None

from mock.demo_data import (
    CLINICS,
    DEFAULT_REPORT,
    DEMO_PET,
    DEMO_TIMEZONE,
    DEMO_TUTOR,
    EMERGENCY_GUIDANCE,
    INITIAL_AI_MESSAGE,
    NON_EMERGENCY_GUIDANCE,
    TRIAGE_CAVEATS,
)
from mock.demo_service import (
    ConsentRequiredError,
    create_referral,
    dashboard_metrics,
    filter_cases,
    filter_clinics,
    find_case,
    get_clinic,
    get_location,
    initial_case_store,
    list_clinic_cases,
    list_clinics,
    new_demo_state,
    send_message,
    update_status,
)
from mock.domain import (
    Case,
    CaseStatus,
    Classification,
    Clinic,
    Message,
    MessageAuthor,
    Triage,
    TriageAnswer,
)


st.set_page_config(
    page_title="VetAI — demonstração de encaminhamento",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { --vet-teal: #116466; --vet-ink: #18343b; --vet-soft: #eef7f5; }
      .block-container { max-width: 1440px; padding-top: 1.5rem; }
      h1, h2, h3 { color: var(--vet-ink); letter-spacing: -0.02em; }
      [data-testid="stMetric"] { background: #f7faf9; border: 1px solid #dce8e5;
        border-radius: .75rem; padding: .7rem; }
      .demo-banner { background: #fff7df; border: 1px solid #e5c766;
        border-radius: .75rem; color: #4d400f; padding: .75rem 1rem; margin-bottom: 1rem; }
      .clinic-card { border-left: 4px solid var(--vet-teal); padding-left: .8rem; }
      @media (max-width: 760px) { .block-container { padding-left: 1rem; padding-right: 1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def now() -> datetime:
    return datetime.now(DEMO_TIMEZONE)


def new_message(
    author_type: MessageAuthor,
    author_name: str,
    content: str,
) -> Message:
    return Message(
        id=uuid4().hex,
        author_type=author_type,
        author_name=author_name,
        content=content,
        created_at=now(),
    )


def initialize_session() -> dict:
    if "demo" not in st.session_state:
        state = new_demo_state()
        state.update(
            {
                "area": "Área do tutor",
                "tutor_page": "Chat",
                "report": DEFAULT_REPORT,
                "answer": None,
                "triage": None,
                "search_performed": False,
                "clinic_view": "list",
                "map_focus_id": None,
                "consent": False,
            }
        )
        state["triage_conversation"] = [
            new_message(
                MessageAuthor.AI,
                "Assistente de pré-triagem",
                INITIAL_AI_MESSAGE,
            )
        ]
        st.session_state.demo = state
    return st.session_state.demo


def reset_demo() -> None:
    st.session_state.clear()
    st.rerun()


def go_to_tutor(page: str) -> None:
    state["area"] = "Área do tutor"
    state["tutor_page"] = page
    st.rerun()


def go_to_clinic(clinic_id: str | None = None) -> None:
    if clinic_id:
        state["dashboard_clinic_id"] = clinic_id
    state["area"] = "Área da clínica"
    st.rerun()


def render_demo_banner() -> None:
    st.markdown(
        """
        <div class="demo-banner"><strong>Ambiente demonstrativo.</strong>
        Localização, clínicas, distância, tempo, avaliações e disponibilidade são
        simulados. Não há comunicação externa, reserva ou envio de dados reais.</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.title("VetAI Demo")
        st.caption("Protótipo acadêmico de pré-triagem e encaminhamento")

        area = st.selectbox(
            "Área",
            ["Área do tutor", "Área da clínica"],
            index=0 if state["area"] == "Área do tutor" else 1,
        )
        state["area"] = area

        if area == "Área do tutor":
            page = st.pills(
                "Navegação do tutor",
                ["Chat", "Clínicas próximas"],
                default=state["tutor_page"],
                required=True,
                width="stretch",
            )
            state["tutor_page"] = page or "Chat"
        else:
            clinic_ids = [clinic.id for clinic in CLINICS]
            selected = state.get("dashboard_clinic_id", clinic_ids[0])
            if selected not in clinic_ids:
                selected = clinic_ids[0]
            state["dashboard_clinic_id"] = st.selectbox(
                "Clínica atualmente selecionada",
                clinic_ids,
                index=clinic_ids.index(selected),
                format_func=lambda item: get_clinic(item).name,
            )
            st.caption("Cada painel mostra somente os casos enviados à sua unidade.")

        st.divider()
        st.subheader("Animal da demonstração")
        st.write(f"**{DEMO_PET.name}** · {DEMO_PET.species}")
        st.caption(f"{DEMO_PET.breed} · {DEMO_PET.age} · {DEMO_PET.weight}")
        triage = state.get("triage")
        if triage:
            st.write(f"**Pré-triagem simulada:** {triage.classification.value}")
        selected_clinic = get_clinic(state.get("selected_clinic_id"))
        st.write(
            f"**Clínica escolhida:** {selected_clinic.name}"
            if selected_clinic
            else "**Clínica escolhida:** nenhuma"
        )
        st.divider()
        if st.button("Reiniciar demonstração", width="stretch"):
            reset_demo()


def render_message(message: Message) -> None:
    role = "user" if message.author_type == MessageAuthor.TUTOR else "assistant"
    avatars = {
        MessageAuthor.TUTOR: "👤",
        MessageAuthor.AI: "🤖",
        MessageAuthor.CLINIC: "🏥",
        MessageAuthor.SYSTEM: "ℹ️",
    }
    with st.chat_message(role, avatar=avatars[message.author_type]):
        st.caption(f"{message.author_name} · {message.created_at:%d/%m/%Y %H:%M}")
        st.markdown(message.content)


def submit_report() -> None:
    report = st.session_state.get("demo_report_input", "").strip() or DEFAULT_REPORT
    state["report"] = report
    state["triage_conversation"].append(
        new_message(MessageAuthor.TUTOR, DEMO_TUTOR.name, report)
    )
    state["triage_conversation"].append(
        new_message(
            MessageAuthor.AI,
            "Assistente de pré-triagem",
            "Obrigado pelo relato. O Thor está ofegante ou parece respirar com dificuldade?",
        )
    )
    state["flow_stage"] = "question"


def answer_triage(answer: str) -> None:
    state["answer"] = answer
    state["triage_conversation"].append(
        new_message(MessageAuthor.TUTOR, DEMO_TUTOR.name, answer)
    )

    if answer == "Sim":
        classification = Classification.EMERGENCY
        signs = ("Respiração acelerada", "Ofegância confirmada", "Cansaço", "Recusa alimentar")
        rationale = (
            "A confirmação de alteração respiratória, combinada ao relato, indica "
            "necessidade de avaliação veterinária imediata no cenário demonstrativo."
        )
        guidance = EMERGENCY_GUIDANCE
        response = (
            "A **pré-triagem simulada** classificou o cenário como **Emergência**. "
            "Isso não é diagnóstico. Procure avaliação veterinária; você pode comparar "
            "clínicas fictícias e decidir explicitamente se deseja encaminhar o caso."
        )
        state["flow_stage"] = "triage_ready"
    elif answer == "Não":
        classification = Classification.NON_EMERGENCY
        signs = ("Cansaço", "Recusa alimentar")
        rationale = "Não houve confirmação de dificuldade respiratória neste cenário."
        guidance = NON_EMERGENCY_GUIDANCE
        response = (
            "A **pré-triagem simulada** classificou o cenário como **Não emergência**. "
            "Observe o animal e procure um veterinário se houver piora."
        )
        state["flow_stage"] = "closed"
    else:
        classification = Classification.UNCERTAIN
        signs = ("Respiração acelerada relatada", "Cansaço", "Recusa alimentar")
        rationale = "A informação disponível não permite classificar com segurança."
        guidance = NON_EMERGENCY_GUIDANCE
        response = (
            "A **pré-triagem simulada** permaneceu **Incerta**. Uma aplicação real faria "
            "novas perguntas; procure avaliação veterinária se estiver preocupado ou houver piora."
        )
        state["flow_stage"] = "closed"

    state["triage"] = Triage(
        original_report=state["report"],
        answers=(
            TriageAnswer(
                question="O animal está ofegante ou respirando com dificuldade?",
                answer=answer,
            ),
        ),
        classification=classification,
        signs=signs,
        rationale=rationale,
        guidance=guidance,
        caveats=TRIAGE_CAVEATS,
    )
    state["triage_conversation"].append(
        new_message(MessageAuthor.AI, "Assistente de pré-triagem", response)
    )


def render_tutor_chat() -> None:
    st.title("Chat do tutor")
    st.caption("Relato e pré-triagem acadêmica com dados fictícios")
    render_demo_banner()

    profile, history = st.columns([1, 2.2])
    with profile:
        with st.container(border=True):
            st.subheader(DEMO_PET.name)
            st.write(f"{DEMO_PET.species} · {DEMO_PET.breed}")
            st.write(f"{DEMO_PET.age} · {DEMO_PET.weight}")
            st.write("**Histórico relevante simulado**")
            for item in DEMO_PET.relevant_history:
                st.write(f"• {item}")
    with history:
        for message in state["triage_conversation"]:
            render_message(message)

        if state["flow_stage"] == "report":
            st.text_area(
                "Relato demonstrativo",
                value=state["report"],
                key="demo_report_input",
                height=130,
            )
            st.button("Enviar relato", type="primary", on_click=submit_report)
        elif state["flow_stage"] == "question":
            st.write("**Escolha uma resposta para a pergunta complementar:**")
            columns = st.columns(3)
            for column, answer in zip(columns, ("Sim", "Não", "Não sei")):
                column.button(
                    answer,
                    on_click=answer_triage,
                    args=(answer,),
                    type="primary" if answer == "Sim" else "secondary",
                    width="stretch",
                )
        elif state["flow_stage"] == "triage_ready":
            if st.button("Encontrar clínicas próximas", type="primary"):
                state["search_performed"] = True
                go_to_tutor("Clínicas próximas")
        elif state["flow_stage"] == "closed":
            st.info("O encaminhamento imediato não foi aberto neste cenário demonstrativo.")
        elif state["flow_stage"] == "referred":
            render_tutor_clinic_channel()


def map_selection_id(event) -> str | None:
    try:
        objects = event.selection.objects
        for selected_objects in objects.values():
            if selected_objects:
                return selected_objects[0].get("clinic_id")
    except (AttributeError, IndexError, TypeError):
        return None
    return None


def render_map(clinics: list[Clinic]) -> None:
    location = get_location()
    points = [
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "label": location["label"],
            "kind": "Tutor",
            "clinic_id": "",
            "color": [25, 100, 150, 230],
            "radius": 170,
        }
    ]
    points.extend(
        {
            "latitude": clinic.latitude,
            "longitude": clinic.longitude,
            "label": clinic.name,
            "kind": "Clínica fictícia",
            "clinic_id": clinic.id,
            "color": [17, 100, 102, 230],
            "radius": 130,
        }
        for clinic in clinics
    )
    frame = pd.DataFrame(points)

    if pdk is None:
        st.warning("PyDeck indisponível. Exibindo o fallback de mapa simples.")
        st.map(frame, latitude="latitude", longitude="longitude", size="radius")
    else:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=frame,
            get_position="[longitude, latitude]",
            get_fill_color="color",
            get_radius="radius",
            pickable=True,
        )
        event = st.pydeck_chart(
            pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                    latitude=location["latitude"],
                    longitude=location["longitude"],
                    zoom=13,
                ),
                layers=[layer],
                tooltip={"text": "{kind}: {label}"},
            ),
            on_select="rerun",
            selection_mode="single-object",
            key="demo_clinic_map",
        )
        selected_id = map_selection_id(event)
        if selected_id:
            state["selected_clinic_id"] = selected_id
            state["clinic_view"] = "detail"
            st.rerun()

    legend_a, legend_b = st.columns(2)
    legend_a.info("● Tutor — localização simulada")
    legend_b.success("● Clínica fictícia — dados simulados")
    marker = st.pills(
        "Selecionar um marcador do mapa",
        [clinic.id for clinic in clinics],
        format_func=lambda item: get_clinic(item).name,
        key="map_marker_fallback",
    )
    if marker and marker != state.get("map_focus_id"):
        state["map_focus_id"] = marker
        state["selected_clinic_id"] = marker
        state["clinic_view"] = "detail"
        st.rerun()


def render_clinic_card(clinic: Clinic) -> None:
    with st.container(border=True):
        st.markdown(f"<div class='clinic-card'><strong>{clinic.name}</strong></div>", unsafe_allow_html=True)
        st.caption("Dados simulados · Disponibilidade não confirmada")
        st.write(clinic.address)
        first, second = st.columns(2)
        first.metric("Distância estimada", f"{clinic.distance_km:.1f} km".replace(".", ","))
        second.metric("Tempo estimado", f"{clinic.eta_minutes} min")
        st.write(f"**24 horas:** {'Sim' if clinic.open_24h else 'Não'}")
        st.write(f"**Avaliação simulada:** {clinic.rating:.1f}/5 ({clinic.review_count} avaliações)")
        st.write(f"**Disponibilidade simulada:** {clinic.availability}")
        if st.button("Visualizar detalhes", key=f"details-{clinic.id}", width="stretch"):
            state["selected_clinic_id"] = clinic.id
            state["clinic_view"] = "detail"
            st.rerun()


def render_clinic_detail(clinic: Clinic) -> None:
    st.caption("Clínica fictícia · Dados simulados · Disponibilidade não confirmada")
    st.header(clinic.name)
    st.write(f"**Endereço fictício:** {clinic.address}")
    st.write(f"**Telefone fictício:** {clinic.phone}")
    st.write(f"**Horário declarado:** {clinic.opening_hours}")
    cols = st.columns(4)
    cols[0].metric("Distância estimada", f"{clinic.distance_km:.1f} km".replace(".", ","))
    cols[1].metric("Tempo estimado", f"{clinic.eta_minutes} min")
    cols[2].metric("Avaliação simulada", f"{clinic.rating:.1f}/5")
    cols[3].metric("Avaliações simuladas", clinic.review_count)
    st.write("**Estrutura ou serviços declarados:** " + " · ".join(clinic.services))
    st.write(f"**Disponibilidade simulada:** {clinic.availability}")
    st.write(f"**Última atualização simulada:** {clinic.last_updated:%d/%m/%Y %H:%M}")
    st.info(clinic.notes)

    primary, back, map_col = st.columns(3)
    if primary.button("Selecionar esta clínica", type="primary", width="stretch"):
        state["selected_clinic_id"] = clinic.id
        state["clinic_view"] = "review"
        state["consent"] = False
        st.session_state.pop("referral_consent_checkbox", None)
        st.rerun()
    if back.button("Voltar à lista", width="stretch"):
        state["clinic_view"] = "list"
        st.rerun()
    if map_col.button("Ver no mapa", width="stretch"):
        state["clinic_view"] = "list"
        state["map_focus_id"] = clinic.id
        st.rerun()

    copy_col, route_col = st.columns(2)
    if copy_col.button("Copiar endereço", width="stretch"):
        st.code(clinic.address, language=None)
        st.caption("Selecione e copie o endereço fictício acima.")
    if route_col.button("Abrir rota simulada", width="stretch"):
        st.warning(
            f"Rota demonstrativa: saída da localização simulada, chegada em "
            f"{clinic.eta_minutes} min. Nenhum aplicativo de navegação foi aberto."
        )


def render_share_review(clinic: Clinic) -> None:
    triage: Triage = state["triage"]
    st.header("Revisar encaminhamento simulado")
    st.caption(f"Destino escolhido pelo tutor: {clinic.name}")
    st.warning("Revise todos os dados. Nada será criado no feed antes do consentimento.")

    identity, animal = st.columns(2)
    with identity:
        st.subheader("Tutor")
        st.write(f"**Nome:** {DEMO_TUTOR.name}")
        st.write(f"**Telefone fictício:** {DEMO_TUTOR.phone}")
    with animal:
        st.subheader("Animal")
        st.write(f"**Nome:** {DEMO_PET.name}")
        st.write(f"**Espécie:** {DEMO_PET.species}")
        st.write(f"**Raça:** {DEMO_PET.breed}")
        st.write(f"**Idade:** {DEMO_PET.age}")
        st.write(f"**Peso:** {DEMO_PET.weight}")

    tabs = st.tabs(["Histórico", "Relato e respostas", "Pré-triagem", "Conversa completa"])
    with tabs[0]:
        for item in DEMO_PET.relevant_history:
            st.write(f"• {item}")
    with tabs[1]:
        st.write(f"**Relato original:** {triage.original_report}")
        for item in triage.answers:
            st.write(f"**Pergunta:** {item.question}")
            st.write(f"**Resposta:** {item.answer}")
    with tabs[2]:
        st.write(f"**Classificação:** {triage.classification.value} — pré-triagem simulada")
        st.write("**Sinais identificados:** " + ", ".join(triage.signs))
        st.write(f"**Justificativa:** {triage.rationale}")
        st.write("**Orientação já exibida:**")
        for item in triage.guidance:
            st.write(f"• {item}")
        for caveat in triage.caveats:
            st.caption(caveat)
        st.write(f"**Previsão simulada de chegada:** {clinic.eta_minutes} min após a confirmação")
    with tabs[3]:
        for message in state["triage_conversation"]:
            render_message(message)

    consent = st.checkbox(
        "Estou ciente de que esta é uma demonstração e autorizo o "
        "compartilhamento simulado destes dados com a clínica selecionada.",
        key="referral_consent_checkbox",
    )
    state["consent"] = consent
    send_col, cancel_col = st.columns(2)
    if send_col.button(
        "Concluir envio simulado",
        type="primary",
        disabled=not consent,
        width="stretch",
    ):
        try:
            case = create_referral(
                state["cases_by_clinic"],
                clinic_id=clinic.id,
                tutor=DEMO_TUTOR,
                pet=DEMO_PET,
                triage=triage,
                conversation=state["triage_conversation"],
                consent=consent,
                now=now(),
            )
        except ConsentRequiredError as error:
            st.error(str(error))
        else:
            state["referral_case_id"] = case.id
            state["selected_case_by_clinic"][clinic.id] = case.id
            state["flow_stage"] = "referred"
            state["clinic_view"] = "detail"
            go_to_tutor("Chat")
    if cancel_col.button("Cancelar e voltar ao chat", width="stretch"):
        state["selected_clinic_id"] = None
        state["clinic_view"] = "list"
        st.session_state.pop("referral_consent_checkbox", None)
        go_to_tutor("Chat")


def render_tutor_clinic_channel() -> None:
    clinic_id = state["selected_clinic_id"]
    case = find_case(state["cases_by_clinic"], clinic_id, state["referral_case_id"])
    clinic = get_clinic(clinic_id)
    st.success("Demonstração: nenhum dado foi enviado a uma clínica real.")
    st.subheader(f"Conversa humana simulada · {clinic.name}")
    st.caption("A IA não responde neste canal. As mensagens existem somente nesta sessão.")
    for message in case.messages:
        render_message(message)

    with st.form("tutor-clinic-message", clear_on_submit=True):
        content = st.text_area("Mensagem para a clínica", height=90)
        submitted = st.form_submit_button("Enviar mensagem manual", type="primary")
    if submitted:
        if content.strip():
            send_message(
                state["cases_by_clinic"],
                clinic_id=clinic_id,
                case_id=case.id,
                author_type=MessageAuthor.TUTOR,
                author_name=DEMO_TUTOR.name,
                content=content,
                now=now(),
            )
            st.rerun()
        else:
            st.warning("Digite uma mensagem antes de enviar.")
    if st.button("Abrir painel da clínica selecionada"):
        go_to_clinic(clinic_id)


def render_nearby_clinics() -> None:
    st.title("Clínicas próximas")
    st.caption("Comparação demonstrativa; a escolha é sempre explícita do tutor")
    render_demo_banner()

    if state.get("triage") is None or state["triage"].classification != Classification.EMERGENCY:
        st.info("Conclua primeiro o cenário de pré-triagem no chat para abrir a busca.")
        if st.button("Voltar ao chat"):
            go_to_tutor("Chat")
        return

    clinic = get_clinic(state.get("selected_clinic_id"))
    if state["clinic_view"] == "detail" and clinic:
        render_clinic_detail(clinic)
        return
    if state["clinic_view"] == "review" and clinic:
        render_share_review(clinic)
        return

    with st.container(border=True):
        search_text = st.text_input(
            "Buscar por nome, endereço ou estrutura simulada",
            placeholder="Ex.: imagem ou nome inexistente",
        )
        sort_col, open_col, available_col = st.columns(3)
        sort_label = sort_col.selectbox(
            "Ordenar por",
            ["Distância estimada", "Tempo estimado"],
        )
        open_only = open_col.checkbox("Somente atendimento 24 horas")
        available_only = available_col.checkbox("Somente disponibilidade simulada")
        if st.button("Atualizar busca simulada"):
            state["search_performed"] = True

    if not state["search_performed"]:
        st.info("Clique em “Atualizar busca simulada” para carregar as clínicas fictícias.")
        return

    with st.spinner("Consultando dados simulados de localização e clínicas..."):
        clinics = filter_clinics(
            list_clinics(),
            open_24h_only=open_only,
            available_only=available_only,
            sort_by="eta" if sort_label == "Tempo estimado" else "distance",
            query=search_text,
        )

    if not clinics:
        st.warning("Nenhuma clínica fictícia corresponde aos filtros selecionados.")
        st.caption("Remova um filtro para voltar a visualizar os dados simulados.")
        return

    map_col, list_col = st.columns([1.35, 1], gap="large")
    with map_col:
        st.subheader("Mapa simulado")
        render_map(clinics)
    with list_col:
        st.subheader(f"{len(clinics)} clínicas fictícias")
        for item in clinics:
            render_clinic_card(item)
    if st.button("Cancelar e voltar ao chat"):
        go_to_tutor("Chat")


def classification_label(classification: Classification) -> str:
    labels = {
        Classification.EMERGENCY: "Alerta — Emergência",
        Classification.NON_EMERGENCY: "Atenção — Não emergência",
        Classification.UNCERTAIN: "Revisar — Incerto",
    }
    return labels[classification]


def case_summary(case: Case) -> str:
    report = case.triage.original_report.strip()
    return report if len(report) <= 105 else report[:102].rstrip() + "…"


def render_case_queue(clinic_id: str, cases: list[Case]) -> Case | None:
    st.subheader("Fila de casos")
    classification_filter = st.selectbox(
        "Classificação",
        ["Todas"] + [item.value for item in Classification],
        key=f"class-filter-{clinic_id}",
    )
    status_filter = st.selectbox(
        "Status",
        ["Todos"] + [item.value for item in CaseStatus],
        key=f"status-filter-{clinic_id}",
    )
    order = st.selectbox(
        "Ordenação",
        ["Mais recentes", "Mais antigos"],
        key=f"order-filter-{clinic_id}",
    )
    classification = None if classification_filter == "Todas" else Classification(classification_filter)
    status = None if status_filter == "Todos" else CaseStatus(status_filter)
    filtered = filter_cases(
        cases,
        classification=classification,
        status=status,
        newest_first=order == "Mais recentes",
    )
    if not filtered:
        st.info("Nenhum caso desta clínica corresponde aos filtros.")
        return None

    visible_ids = [case.id for case in filtered]
    selected_id = state["selected_case_by_clinic"].get(clinic_id)
    if selected_id not in visible_ids:
        selected_id = visible_ids[0]
    selected_id = st.radio(
        "Selecionar caso",
        visible_ids,
        index=visible_ids.index(selected_id),
        format_func=lambda case_id: (
            f"{find_case(state['cases_by_clinic'], clinic_id, case_id).created_at:%H:%M} · "
            f"{find_case(state['cases_by_clinic'], clinic_id, case_id).pet.name} · "
            f"{find_case(state['cases_by_clinic'], clinic_id, case_id).status.value}"
        ),
        key=f"case-select-{clinic_id}",
        label_visibility="collapsed",
    )
    state["selected_case_by_clinic"][clinic_id] = selected_id
    selected = find_case(state["cases_by_clinic"], clinic_id, selected_id)
    with st.container(border=True):
        st.write(f"**{classification_label(selected.triage.classification)}**")
        st.write(f"**{selected.pet.name}** · {selected.pet.species} · {selected.status.value}")
        st.caption(
            f"Alerta {selected.created_at:%H:%M} · chegada simulada {selected.expected_arrival:%H:%M}"
        )
        st.write(case_summary(selected))
    return selected


def status_actions(case: Case) -> None:
    st.write("**Ações simuladas da equipe**")
    actions = [
        ("Reconhecer caso", CaseStatus.ACKNOWLEDGED),
        ("Aguardando o tutor", CaseStatus.ON_THE_WAY),
        ("Marcar em atendimento", CaseStatus.IN_CARE),
        ("Concluir", CaseStatus.COMPLETED),
        ("Cancelar", CaseStatus.CANCELLED),
    ]
    columns = st.columns(3)
    for index, (label, status) in enumerate(actions):
        if columns[index % 3].button(
            label,
            key=f"status-{case.id}-{status.value}",
            disabled=case.status == status,
            width="stretch",
        ):
            update_status(
                state["cases_by_clinic"],
                clinic_id=case.clinic_id,
                case_id=case.id,
                status=status,
                now=now(),
            )
            st.rerun()


def render_case_detail(case: Case, clinic: Clinic) -> None:
    st.subheader(f"Caso {case.id}")
    st.caption("Dados simulados · uso apenas acadêmico")
    status_actions(case)
    tabs = st.tabs(["Resumo", "Animal", "Tutor", "Triagem", "Conversa", "Eventos"])
    with tabs[0]:
        st.write(f"**Classificação:** {classification_label(case.triage.classification)} — pré-triagem simulada")
        st.write(f"**Status:** {case.status.value}")
        st.write(f"**Sinais identificados:** {', '.join(case.triage.signs)}")
        st.write(f"**Resumo do relato:** {case_summary(case)}")
        st.write(f"**Horário do alerta:** {case.created_at:%d/%m/%Y %H:%M}")
        st.write(f"**Previsão simulada de chegada:** {case.expected_arrival:%d/%m/%Y %H:%M}")
    with tabs[1]:
        st.write(f"**Nome:** {case.pet.name}")
        st.write(f"**Espécie:** {case.pet.species}")
        st.write(f"**Raça:** {case.pet.breed}")
        st.write(f"**Idade:** {case.pet.age}")
        st.write(f"**Peso:** {case.pet.weight}")
        st.write("**Histórico relevante:**")
        for item in case.pet.relevant_history:
            st.write(f"• {item}")
    with tabs[2]:
        st.write(f"**Nome:** {case.tutor.name}")
        st.write(f"**Telefone fictício:** {case.tutor.phone}")
    with tabs[3]:
        st.write(f"**Relato original:** {case.triage.original_report}")
        for answer in case.triage.answers:
            st.write(f"**Pergunta:** {answer.question}")
            st.write(f"**Resposta:** {answer.answer}")
        st.write(f"**Classificação:** {case.triage.classification.value} — pré-triagem simulada")
        st.write(f"**Justificativa:** {case.triage.rationale}")
        st.write("**Orientação apresentada:**")
        for item in case.triage.guidance:
            st.write(f"• {item}")
        st.write("**Ressalvas:**")
        for item in case.triage.caveats:
            st.write(f"• {item}")
    with tabs[4]:
        st.caption("Mensagens identificadas por autor e horário. A IA não participa após o envio.")
        for message in case.messages:
            render_message(message)
        with st.form(f"clinic-message-{case.id}", clear_on_submit=True):
            content = st.text_area("Mensagem manual ao tutor", height=85)
            submitted = st.form_submit_button("Enviar como equipe da clínica")
        if submitted:
            if content.strip():
                send_message(
                    state["cases_by_clinic"],
                    clinic_id=clinic.id,
                    case_id=case.id,
                    author_type=MessageAuthor.CLINIC,
                    author_name=clinic.name,
                    content=content,
                    now=now(),
                )
                st.rerun()
            else:
                st.warning("Digite uma mensagem antes de enviar.")
    with tabs[5]:
        for event in reversed(case.events):
            st.write(f"**{event.created_at:%d/%m/%Y %H:%M}** · {event.description}")


def render_clinic_dashboard() -> None:
    clinic_id = state.get("dashboard_clinic_id", CLINICS[0].id)
    clinic = get_clinic(clinic_id)
    cases = list_clinic_cases(state["cases_by_clinic"], clinic_id)
    st.title(clinic.name)
    st.caption(f"Dashboard demonstrativo · {clinic.address} · {clinic.phone}")
    render_demo_banner()

    metrics = dashboard_metrics(cases)
    metric_columns = st.columns(6)
    values = [
        ("Aguardando análise", metrics["waiting"]),
        ("Emergências prováveis", metrics["emergencies"]),
        ("Reconhecidos", metrics["acknowledged"]),
        ("A caminho", metrics["on_the_way"]),
        ("Concluídos", metrics["completed"]),
        ("Média até reconhecer", f"{metrics['average_recognition_minutes']:.1f} min".replace(".", ",")),
    ]
    for column, (label, value) in zip(metric_columns, values):
        column.metric(label, value, help="Métrica derivada somente do estado desta sessão.")

    if not cases:
        st.info(
            "Fila vazia para esta clínica. Casos enviados às outras unidades não aparecem aqui."
        )
        return

    queue_col, detail_col = st.columns([1, 2.1], gap="large")
    with queue_col:
        selected_case = render_case_queue(clinic_id, cases)
    with detail_col:
        if selected_case:
            render_case_detail(selected_case, clinic)
        else:
            st.info("Selecione filtros com resultados para abrir um caso.")


state = initialize_session()
if "cases_by_clinic" not in state:  # migração defensiva de sessão antiga
    state["cases_by_clinic"] = initial_case_store()
render_sidebar()

if state["area"] == "Área da clínica":
    render_clinic_dashboard()
elif state["tutor_page"] == "Clínicas próximas":
    render_nearby_clinics()
else:
    render_tutor_chat()
