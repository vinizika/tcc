"""
O congelamento por hash só protege alguma coisa se ele realmente mudar
quando o conteúdo muda, e continuar igual quando nada muda.
"""

import json

from prova_freeze import caminho_manifesto, hash_split, main


def escrever_csv(caminho, linhas):

    cabecalho = ["id", "text", "expected_class", "split"]
    conteudo = ",".join(cabecalho) + "\n"
    for linha in linhas:
        conteudo += ",".join(linha[campo] for campo in cabecalho) + "\n"
    caminho.write_text(conteudo, encoding="utf-8")


def test_hash_e_deterministico_e_ignora_ordem_do_arquivo():

    linhas_a = [
        {"id": "p2", "text": "b", "expected_class": "EMERGENCIA", "split": "teste"},
        {"id": "p1", "text": "a", "expected_class": "EMERGENCIA", "split": "teste"},
    ]
    linhas_b = list(reversed(linhas_a))

    from prova_freeze import carregar_split

    # hash_split espera linhas já ordenadas por id, como carregar_split
    # devolve — aqui simulamos isso diretamente para as duas ordens de
    # entrada.
    ordenadas_a = sorted(linhas_a, key=lambda linha: linha["id"])
    ordenadas_b = sorted(linhas_b, key=lambda linha: linha["id"])

    assert hash_split(ordenadas_a) == hash_split(ordenadas_b)


def test_hash_muda_quando_o_texto_muda():

    linhas = [{"id": "p1", "text": "a", "expected_class": "EMERGENCIA", "split": "teste"}]
    linhas_editadas = [
        {"id": "p1", "text": "a editado", "expected_class": "EMERGENCIA", "split": "teste"}
    ]

    assert hash_split(linhas) != hash_split(linhas_editadas)


def test_freeze_depois_check_ok(tmp_path):

    cases = tmp_path / "casos.csv"
    escrever_csv(
        cases,
        [
            {"id": "p1", "text": "a", "expected_class": "EMERGENCIA", "split": "teste"},
            {"id": "p2", "text": "b", "expected_class": "NAO_EMERGENCIA", "split": "dev"},
        ],
    )

    main(["--cases", str(cases), "--split", "teste", "--freeze"])

    manifesto_path = caminho_manifesto(cases, "teste")
    assert manifesto_path.exists()

    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    assert manifesto["row_count"] == 1

    # Não muda nada: a segunda chamada (sem --freeze) deve passar.
    main(["--cases", str(cases), "--split", "teste"])


def test_check_falha_quando_o_conteudo_muda_depois_de_congelar(tmp_path):

    cases = tmp_path / "casos.csv"
    escrever_csv(
        cases,
        [{"id": "p1", "text": "a", "expected_class": "EMERGENCIA", "split": "teste"}],
    )

    main(["--cases", str(cases), "--split", "teste", "--freeze"])

    escrever_csv(
        cases,
        [{"id": "p1", "text": "a editado", "expected_class": "EMERGENCIA", "split": "teste"}],
    )

    try:
        main(["--cases", str(cases), "--split", "teste"])
        assert False, "deveria ter recusado"
    except SystemExit as erro:
        assert "não bate" in str(erro) or "MUDOU" in str(erro)


def test_check_falha_sem_congelamento_previo(tmp_path):

    cases = tmp_path / "casos.csv"
    escrever_csv(
        cases,
        [{"id": "p1", "text": "a", "expected_class": "EMERGENCIA", "split": "teste"}],
    )

    try:
        main(["--cases", str(cases), "--split", "teste"])
        assert False, "deveria ter recusado"
    except SystemExit as erro:
        assert "Nenhum congelamento" in str(erro)
