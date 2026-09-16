"""Fonte única dos dados fictícios usados pelo protótipo."""

from datetime import datetime
from zoneinfo import ZoneInfo

from mock.domain import Clinic, Pet, Tutor


DEMO_TIMEZONE = ZoneInfo("America/Sao_Paulo")

DEMO_LOCATION = {
    "label": "Localização simulada do tutor",
    "latitude": -23.6939,
    "longitude": -46.5654,
}

DEMO_TUTOR = Tutor(name="João Exemplo", phone="(11) 90000-0001")

DEMO_PET = Pet(
    name="Thor",
    species="Cão",
    breed="Bulldog francês",
    age="8 anos",
    weight="12,4 kg",
    relevant_history=(
        "Histórico de intolerância ao calor",
        "Episódios anteriores de tosse após esforço",
        "Vacinação informada como em dia",
        "Sem alergias medicamentosas registradas na demonstração",
    ),
)

DEFAULT_REPORT = (
    "Meu cachorro Thor está estranho desde hoje cedo. Ele está muito quieto, "
    "parece cansado, não quis comer direito e agora está deitado respirando "
    "mais rápido. Estou preocupado porque isso não é normal para ele."
)

INITIAL_AI_MESSAGE = (
    "Olá! Esta é uma demonstração de pré-triagem veterinária. Já tenho o "
    "perfil fictício do Thor. Descreva o que está acontecendo para iniciar "
    "o cenário simulado."
)

EMERGENCY_GUIDANCE = (
    "Mantenha o animal em local fresco, calmo e ventilado.",
    "Evite esforço físico durante o deslocamento.",
    "Não ofereça medicamentos por conta própria.",
    "Não force água ou alimento se houver desconforto.",
    "Procure avaliação de um médico-veterinário o quanto antes.",
)

NON_EMERGENCY_GUIDANCE = (
    "Mantenha o animal em ambiente calmo, fresco e ventilado.",
    "Ofereça água em pequenas quantidades, sem forçar.",
    "Observe apetite, disposição e surgimento de novos sinais.",
    "Procure atendimento se houver piora ou dificuldade respiratória.",
)

TRIAGE_CAVEATS = (
    "Pré-triagem simulada: não é diagnóstico e não substitui avaliação veterinária.",
    "Nenhuma medicação é prescrita neste protótipo.",
)


def _demo_time(hour: int, minute: int) -> datetime:
    return datetime(2026, 9, 14, hour, minute, tzinfo=DEMO_TIMEZONE)


CLINICS: tuple[Clinic, ...] = (
    Clinic(
        id="vitalvet-demo",
        name="Hospital Veterinário VitalVet Demo",
        address="Avenida Demonstração, 1200 — Bairro Modelo",
        latitude=-23.6889,
        longitude=-46.5577,
        distance_km=1.4,
        eta_minutes=6,
        open_24h=True,
        phone="(11) 90000-0101",
        rating=4.8,
        review_count=184,
        services=("Atendimento geral", "Oxigenioterapia", "Internação"),
        availability="Equipe disponível (simulado)",
        last_updated=_demo_time(14, 32),
        opening_hours="24 horas (informação simulada)",
        notes="Estrutura e capacidade não foram confirmadas externamente.",
    ),
    Clinic(
        id="animalcare-demo",
        name="Clínica AnimalCare Fictícia",
        address="Rua das Patas Imaginárias, 85 — Vila Exemplo",
        latitude=-23.7015,
        longitude=-46.5591,
        distance_km=2.1,
        eta_minutes=9,
        open_24h=True,
        phone="(11) 90000-0202",
        rating=4.6,
        review_count=96,
        services=("Atendimento geral", "Exames rápidos", "Observação"),
        availability="Aguardando confirmação (simulado)",
        last_updated=_demo_time(14, 25),
        opening_hours="24 horas (informação simulada)",
        notes="Disponibilidade exibida apenas para demonstrar o filtro.",
    ),
    Clinic(
        id="petlife-demo",
        name="Centro Veterinário PetLife Cenário",
        address="Alameda do Protótipo, 410 — Jardim Fictício",
        latitude=-23.6994,
        longitude=-46.5799,
        distance_km=3.3,
        eta_minutes=13,
        open_24h=False,
        phone="(11) 90000-0303",
        rating=4.7,
        review_count=121,
        services=("Atendimento geral", "Imagem", "Monitoramento"),
        availability="Equipe disponível (simulado)",
        last_updated=_demo_time(14, 18),
        opening_hours="Todos os dias, 08h–22h (informação simulada)",
        notes="Horário, avaliação e serviços são inteiramente fictícios.",
    ),
)

REQUIRED_CLINIC_FIELDS = (
    "id",
    "name",
    "address",
    "latitude",
    "longitude",
    "distance_km",
    "eta_minutes",
    "open_24h",
    "phone",
    "rating",
    "review_count",
    "services",
    "availability",
    "last_updated",
    "opening_hours",
    "notes",
)
