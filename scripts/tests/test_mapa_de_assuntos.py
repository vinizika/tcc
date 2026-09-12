"""
Testes do mapa de assuntos.

O mapa é editado à mão, por três pessoas e por um agente, e alimenta o
`compare` da régua. Estes testes existem para que a disciplina não dependa
de ninguém lembrar: se um id deixar de casar com o metadado `topic` da base,
ou se um par de confusão apontar para uma linha que não existe, a suíte
avisa antes de alguém medir cobertura errado.
"""

import csv
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
CURADORIA = RAIZ / "data" / "curadoria"
MAPA = CURADORIA / "mapa-de-assuntos.csv"
REFERENCIAS = CURADORIA / "referencias.md"
VOCABULARIO = CURADORIA / "vocabulario-dataset1.csv"
DOENCAS = CURADORIA / "doencas-dataset2.csv"
CASOS_DA_REGUA = RAIZ / "data" / "retrieval" / "cases.csv"
DOCUMENTOS = RAIZ / "backend" / "data" / "documents"

COLUNAS = [
    "id", "quadro", "sistema", "especie", "classe", "urgencia",
    "sinais_que_o_tutor_relata", "discriminador", "par_de_confusao",
    "motivo", "referencias", "prioridade", "etapa", "cobertura",
    "validacao", "observacoes",
]

SISTEMAS = {
    "digestivo", "respiratorio", "urinario", "neurologico", "pele_e_ouvido",
    "olhos", "musculoesqueletico_e_trauma", "toxicologico", "cardiovascular",
    "reprodutivo", "metabolico", "ambiental", "neonatos_e_idosos",
}
COBERTURAS = {
    "sem_documento", "sintetico", "fonte_enviada", "fonte_aprovada", "indexada",
}

# Só as colunas que a etapa 1 precisa ter escritas. A etapa 2 existe para dar
# visão de escopo, e seus campos de texto se preenchem quando ela chegar.
TEXTO_DA_ETAPA_1 = ["sinais_que_o_tutor_relata", "discriminador"]


def ler(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


@pytest.fixture(scope="module")
def mapa():
    return ler(MAPA)


@pytest.fixture(scope="module")
def ids(mapa):
    return {linha["id"] for linha in mapa}


# ----------------------------------------------------------------------
# Forma do arquivo
# ----------------------------------------------------------------------


def test_colunas_sao_exatamente_as_combinadas(mapa):
    """
    O `compare` da régua vai ler este arquivo por nome de coluna. Acrescentar
    coluna é seguro; renomear ou remover quebra do outro lado em silêncio.
    """

    assert list(mapa[0]) == COLUNAS


def test_ids_sao_unicos_e_em_formato_de_topic(mapa):
    """
    O id **é** o `topic` da ficha JSON do documento. Se divergir no formato,
    a cobertura passa a comparar maçã com laranja.
    """

    identificadores = [linha["id"] for linha in mapa]

    assert len(identificadores) == len(set(identificadores))
    for identificador in identificadores:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", identificador), identificador


def test_vocabularios_fechados(mapa):

    for linha in mapa:
        assert linha["sistema"] in SISTEMAS, linha["id"]
        assert linha["especie"] in {"cao", "gato", "ambos"}, linha["id"]
        assert linha["classe"] in {"emergencia", "pode_esperar"}, linha["id"]
        assert linha["urgencia"] in {"imediato", "ate_24h", "rotina"}, linha["id"]
        assert linha["prioridade"] in {"A", "B", "C"}, linha["id"]
        assert linha["etapa"] in {"1", "2"}, linha["id"]
        assert linha["cobertura"] in COBERTURAS, linha["id"]


def test_validacao_registra_quem_validou_e_quando(mapa):
    """
    "Validada" sem nome e data não é validação, é lembrança. O formato
    `validada:<nome>:<DD/MM>` obriga a dizer quem assinou.
    """

    for linha in mapa:
        estado = linha["validacao"]
        if estado in {"rascunho", "contestada"}:
            continue
        assert re.fullmatch(r"validada:[a-zà-ú ]+:\d{2}/\d{2}", estado), linha["id"]


# ----------------------------------------------------------------------
# Coerência clínica interna
# ----------------------------------------------------------------------


def test_classe_segue_a_regra_de_colapso(mapa):
    """
    A régua tem três níveis e o sistema decide entre dois. A conversão é
    fixa: `imediato` vira emergência, e o resto pode aguardar uma consulta
    comum — que é o que o prompt do classificador chama de NAO_EMERGENCIA.
    Sem esta trava, a mesma linha poderia ser lida de dois jeitos.
    """

    for linha in mapa:
        esperada = "emergencia" if linha["urgencia"] == "imediato" else "pode_esperar"
        assert linha["classe"] == esperada, linha["id"]


def test_par_de_confusao_aponta_para_linha_existente(mapa, ids):
    """
    O par é o que liga um quadro grave à sua gêmea leve. Um id solto aqui
    significa que alguém renomeou uma linha e o par ficou órfão.
    """

    for linha in mapa:
        for par in filter(None, linha["par_de_confusao"].split(";")):
            assert par in ids, f"{linha['id']} aponta para {par}"


def test_par_de_confusao_atravessa_as_classes(mapa):
    """
    Um par só ensina alguma coisa quando liga lados opostos: emergência com
    "pode esperar". Dois quadros graves emparelhados não separam nada.
    """

    classe = {linha["id"]: linha["classe"] for linha in mapa}

    for linha in mapa:
        for par in filter(None, linha["par_de_confusao"].split(";")):
            assert classe[par] != linha["classe"], f"{linha['id']} ~ {par}"


def test_toda_linha_tem_referencia_ou_declara_a_lacuna(mapa):
    """
    Linha sem fonte é opinião. `SEM_FONTE` é permitido porque declarar a
    lacuna é melhor que inventar referência — mas ele fica visível num
    `grep`, o que uma referência vaga não ficaria.
    """

    texto = REFERENCIAS.read_text(encoding="utf-8")
    conhecidas = set(re.findall(r"\*\*(R\d{2})\*\*", texto))

    assert len(conhecidas) >= 30

    for linha in mapa:
        citadas = list(filter(None, linha["referencias"].split(";")))
        assert citadas, linha["id"]
        for referencia in citadas:
            if referencia == "SEM_FONTE":
                continue
            assert referencia in conhecidas, f"{linha['id']}: {referencia}"


# ----------------------------------------------------------------------
# Encaixe com o que já existe
# ----------------------------------------------------------------------


def test_todo_documento_da_base_tem_linha_no_mapa(ids):
    """
    O mapa mede cobertura. Um documento indexado que não esteja aqui é uma
    cobertura que ninguém pediu — e provavelmente um assunto que o time
    esqueceu de decidir se quer.
    """

    for ficha in DOCUMENTOS.glob("*.json"):
        topico = json.loads(ficha.read_text(encoding="utf-8")).get("topic", "")
        if topico and topico != "not_informed":
            assert topico in ids, f"{ficha.name}: {topico}"


def test_todo_protocolo_esperado_pela_regua_tem_linha_no_mapa(ids):
    """
    A régua de recuperação julga a busca por `topic`. Se um alvo dela não
    estiver no mapa, o `compare` nunca vai conseguir dizer que aquele
    assunto passou a ter documento.
    """

    for caso in ler(CASOS_DA_REGUA):
        for topico in filter(None, caso["expected_topics"].split(";")):
            assert topico in ids, f"{caso['id']}: {topico}"


# ----------------------------------------------------------------------
# A etapa 1
# ----------------------------------------------------------------------


def test_etapa_1_tem_o_tamanho_que_o_backlog_pediu(mapa):
    """
    O B-50 pedia de 20 a 25 linhas na primeira etapa; a revisão crítica de
    12/09 subiu o teto, porque a pesquisa mostrou apresentações de alta
    frequência que não cabiam em 25 — colapso com gengiva pálida, apatia,
    parvovirose, o par ocular e a permetrina em gato. Muito menos não cobre
    o que a prova pergunta; muito mais não cabe em três semanas com
    validação clínica.
    """

    etapa1 = [linha for linha in mapa if linha["etapa"] == "1"]

    assert 20 <= len(etapa1) <= 35


def test_etapa_1_esta_escrita_por_inteiro(mapa):

    for linha in mapa:
        if linha["etapa"] != "1":
            continue
        for coluna in TEXTO_DA_ETAPA_1:
            assert linha[coluna].strip(), f"{linha['id']}: {coluna} vazio"


def test_etapa_1_cobre_os_dois_lados(mapa):
    """
    Uma etapa só de emergências devolveria o problema do B-03: a base fica
    com um lado só, e o modelo não tem como aprender que existe caso leve.
    """

    etapa1 = [linha for linha in mapa if linha["etapa"] == "1"]
    leves = [linha for linha in etapa1 if linha["classe"] == "pode_esperar"]

    assert len(leves) >= 8


def test_todo_sistema_da_etapa_1_tem_um_quadro_leve(mapa):
    """
    O critério do B-03, literal: ao menos um quadro de não emergência por
    sistema orgânico frequente. Aplicado só à etapa 1, que é a que vai virar
    documento primeiro.
    """

    etapa1 = [linha for linha in mapa if linha["etapa"] == "1"]
    com_leve = {
        linha["sistema"] for linha in etapa1 if linha["classe"] == "pode_esperar"
    }
    exigidos = {
        "digestivo", "respiratorio", "urinario", "neurologico",
        "pele_e_ouvido", "musculoesqueletico_e_trauma", "reprodutivo",
    }

    assert exigidos <= com_leve, exigidos - com_leve


def test_toda_emergencia_da_etapa_1_diz_o_que_separa_do_par(mapa):
    """
    O discriminador é a pergunta que separa o quadro da sua gêmea leve. É o
    que o documento da base precisa responder e o que o relato da prova
    precisa conter — e é a parte que se perde se ninguém escrever.
    """

    for linha in mapa:
        if linha["etapa"] == "1" and linha["classe"] == "emergencia":
            assert "?" in linha["discriminador"], linha["id"]


# ----------------------------------------------------------------------
# Checagem cruzada com os datasets
# ----------------------------------------------------------------------


def test_todo_sinal_do_dataset_cai_em_alguma_linha_ou_e_inespecifico(ids):
    """
    Critério de fechamento do B-50. Um termo que não cai em lugar nenhum e
    não foi marcado como inespecífico é um assunto que a prova pergunta e a
    base não cobre — exatamente o bloqueio que o mapa existe para fechar.
    """

    linhas = ler(VOCABULARIO)

    assert len(linhas) == 194

    for linha in linhas:
        destino = linha["ids_do_mapa"]
        if destino == "inespecifico":
            assert linha["nota"].strip(), f"{linha['termo']}: inespecífico sem motivo"
            continue
        for alvo in filter(None, destino.split(";")):
            assert alvo in ids, f"{linha['termo']}: {alvo}"


def test_toda_doenca_do_dataset2_tem_linha_ou_motivo_para_ficar_de_fora(ids):

    linhas = ler(DOENCAS)

    assert len(linhas) == 48

    for linha in linhas:
        if linha["id_do_mapa"] == "excluida":
            assert linha["motivo"].strip(), f"{linha['doenca']}: excluída sem motivo"
            continue
        assert linha["id_do_mapa"] in ids, linha["doenca"]


def test_os_cinco_sintomas_leves_do_conjunto_nao_viraram_regra_no_mapa(ids):
    """
    Os cinco termos que definem a classe leve do conjunto de avaliação são a
    chave de resposta da prova atual ([B-05]). Eles podem aparecer no
    vocabulário — é para isso que ele serve —, mas nenhuma linha do mapa
    pode ter sido criada só para eles, senão a base passa a acertar a prova
    por construção.
    """

    vocabulario = {linha["termo"]: linha["ids_do_mapa"] for linha in ler(VOCABULARIO)}
    leves = [
        "Eye Discharge", "Nasal Discharge", "Skin Lesions", "Sneezing", "Lameness",
    ]

    alvos = set()
    for termo in leves:
        assert termo in vocabulario, termo
        alvos |= set(filter(None, vocabulario[termo].split(";")))

    # Cada um deles cai numa linha que existe por mérito clínico próprio, e
    # que atende a mais de um termo do vocabulário.
    for alvo in alvos:
        quantos = sum(
            1 for destino in vocabulario.values()
            if alvo in destino.split(";")
        )
        assert quantos > 1, f"{alvo} existe só para um termo da prova"
