"""
Cadastro de tutor e pet, na sidebar.

Sem login (decisão registrada em evidencias/ryu/2026-09-13-05-cadastro-de-
tutor-pet-e-historico.md — fase de desenvolvimento): o "cadastro" aqui só
cria o tutor no Supabase e guarda o id na sessão do navegador. Fechou a
aba, perdeu o id — é o suficiente para testar a integração hoje.

`active_pet_id`, quando existe, viaja em toda mensagem do chat
(components/chat.py) e enriquece o prompt de triagem com o cadastro do
animal (PetResponse.to_triage_context, no backend).
"""

import streamlit as st

from services.api import create_pet, create_tutor, list_tutor_pets


def _tri_state(label: str, key: str):
    """Selectbox de três estados: devolve True, False ou None ("não sei")."""

    opcao = st.selectbox(label, ["Não sei", "Sim", "Não"], key=key)

    return {"Sim": True, "Não": False, "Não sei": None}[opcao]


def _render_cadastro_tutor():

    st.subheader("Seu cadastro")

    st.caption(
        "Sem senha por enquanto — é só para o sistema saber quem é o tutor "
        "e qual pet está sendo atendido."
    )

    with st.form("form_tutor"):

        nome = st.text_input("Seu nome")
        telefone = st.text_input("Telefone (opcional)")
        email = st.text_input("E-mail (opcional)")

        enviado = st.form_submit_button("Criar cadastro")

    if not enviado:
        return

    if not nome.strip():
        st.error("Informe seu nome.")
        return

    try:
        tutor = create_tutor(nome.strip(), telefone.strip() or None, email.strip() or None)
    except Exception as erro:
        st.error(f"Não foi possível criar o cadastro: {erro}")
        return

    st.session_state.tutor_id = tutor["id"]
    st.session_state.tutor_name = tutor["name"]
    st.rerun()


def _render_cadastro_pet(tutor_id: str):

    with st.expander("➕ Cadastrar um pet"):

        with st.form("form_pet"):

            nome = st.text_input("Nome do pet")

            especie = st.radio(
                "Espécie",
                ["cao", "gato"],
                format_func=lambda v: "Cão" if v == "cao" else "Gato",
                horizontal=True,
            )

            raca = st.text_input("Raça (opcional)")

            sexo = st.selectbox(
                "Sexo",
                ["Não informado", "macho", "femea"],
                format_func=lambda v: (
                    "Macho" if v == "macho"
                    else "Fêmea" if v == "femea"
                    else "Não informado"
                ),
            )

            castrado = _tri_state("Castrado(a)?", "castrado_novo_pet")

            nascimento = st.date_input(
                "Data de nascimento (opcional, ajuda a estimar a idade)",
                value=None,
            )

            peso = st.number_input(
                "Peso aproximado, em kg (opcional)",
                min_value=0.0,
                max_value=150.0,
                value=0.0,
                step=0.5,
            )

            vacinacao = _tri_state("Vacinação em dia?", "vacinacao_novo_pet")

            condicoes = st.text_area(
                "Condições crônicas conhecidas (opcional)",
                placeholder="ex.: cardiopata, diabético...",
            )

            enviado = st.form_submit_button("Salvar pet")

        if not enviado:
            return

        if not nome.strip():
            st.error("Informe o nome do pet.")
            return

        try:
            pet = create_pet(
                tutor_id,
                name=nome.strip(),
                species=especie,
                breed=raca.strip() or None,
                sex=None if sexo == "Não informado" else sexo,
                neutered=castrado,
                birth_date=nascimento.isoformat() if nascimento else None,
                weight_kg=peso if peso > 0 else None,
                vaccination_up_to_date=vacinacao,
                chronic_conditions=condicoes.strip() or None,
            )
        except Exception as erro:
            st.error(f"Não foi possível cadastrar o pet: {erro}")
            return

        st.session_state.active_pet_id = pet["id"]
        st.session_state.pets_cache = None
        st.success(f"{pet['name']} cadastrado!")
        st.rerun()


def render_tutor_and_pet():

    if "tutor_id" not in st.session_state:
        st.session_state.tutor_id = None

    if "active_pet_id" not in st.session_state:
        st.session_state.active_pet_id = None

    if not st.session_state.tutor_id:
        _render_cadastro_tutor()
        return

    st.caption(
        f"Tutor: **{st.session_state.get('tutor_name') or st.session_state.tutor_id}**"
    )

    if st.session_state.get("pets_cache") is None:
        try:
            st.session_state.pets_cache = list_tutor_pets(st.session_state.tutor_id)
        except Exception as erro:
            st.error(f"Não foi possível carregar os pets: {erro}")
            st.session_state.pets_cache = []

    pets = st.session_state.pets_cache

    if pets:

        nomes_por_id = {pet["id"]: pet["name"] for pet in pets}
        ids = list(nomes_por_id.keys())

        indice_atual = (
            ids.index(st.session_state.active_pet_id)
            if st.session_state.active_pet_id in ids
            else 0
        )

        pet_selecionado = st.selectbox(
            "Pet sendo atendido agora",
            options=ids,
            index=indice_atual,
            format_func=lambda pid: nomes_por_id[pid],
        )

        st.session_state.active_pet_id = pet_selecionado

    else:
        st.info("Nenhum pet cadastrado ainda.")

    _render_cadastro_pet(st.session_state.tutor_id)
