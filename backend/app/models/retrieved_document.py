from dataclasses import dataclass


@dataclass
class RetrievedDocument:

    id: str

    chunk_id: str

    title: str

    content: str

    source: str

    score: float

    # Procedencia do trecho, vinda dos metadados da ingestao. Nao vai ao
    # prompt: serve para dizer DE QUAL documento o trecho saiu, que e o que
    # a regua de recuperacao precisa para julgar se a busca trouxe o
    # protocolo certo. O titulo nao serve para isso porque e texto livre e
    # muda quando o documento e reescrito.
    #
    # Com default vazio de proposito: quem constroi o objeto sem eles (os
    # dubles dos testes, por exemplo) continua funcionando.
    topic: str = ""

    source_file: str = ""