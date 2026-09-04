# Higiene do repositório e ambiente de desenvolvimento

**Data:** 03/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 1
**Commits:** [`bc14293`](https://github.com/vinizika/tcc/commit/bc14293) · [`d654555`](https://github.com/vinizika/tcc/commit/d654555)

## O que foi feito

Três coisas, todas de infraestrutura, nenhuma tocando a lógica do produto:

1. **Tirei do controle de versão 41 arquivos gerados automaticamente** —
   40 arquivos `.pyc` (cache compilado que o Python cria sozinho) e um
   `.DS_Store` (metadado do Finder do macOS). Eles continuam no disco de todo
   mundo: apenas deixaram de ser versionados. Os dois áudios de teste em
   `backend/uploads/` foram mantidos no repositório por decisão do time.
2. **Deixei o projeto subir em uma máquina nova.** Um clone limpo não subia:
   o `docker-compose.yml` exigia um arquivo `.env` que não existe no
   repositório e não tinha modelo. Agora o `.env` é opcional, existe um
   `.env.example` documentado e o endereço do Ollama é injetado pelo compose.
3. **Habilitei GPU como opção**, em um arquivo de override separado
   (`docker-compose.gpu.yml`), mais um `.dockerignore` para a imagem parar de
   copiar `.venv`, banco vetorial e uploads.

Também criei o diário do trilho registrando o estado inicial (esse conteúdo
agora vive nesta pasta de evidências).

## Por quê

**Sobre os arquivos gerados.** Os `.pyc` são binários que mudam a cada
execução, em cada máquina. Com três pessoas commitando, dois binários
diferentes no mesmo caminho é conflito de merge garantido — em arquivos sem
nenhum valor. O tamanho do problema aparece no histórico: **14 commits do
projeto já mexeram em `.pyc`**, e o commit do HyDE
([`2d6be8c`](https://github.com/vinizika/tcc/commit/2d6be8c)) tinha **17
arquivos `.pyc` em 22** — o trabalho real eram 5 arquivos, afogados no resto.
Isso também deixa os diffs ilegíveis, e esses commits são parte do material do
TCC.

Vale registrar que **a limpeza já tinha sido tentada**: o commit
[`aa1c88e`](https://github.com/vinizika/tcc/commit/aa1c88e) adicionou
`__pycache__/` ao `.gitignore`. Não bastou, porque **o `.gitignore` só vale
para arquivos que o Git ainda não rastreia** — uma vez versionado, o arquivo
continua sendo acompanhado. Faltava o `git rm --cached`, que é o que fecha o
ciclo. Por isso 5 commits posteriores ainda carregaram `.pyc`.

**Sobre a GPU.** A medição de latência registrada pelo time era de ~3,5 minutos
por requisição em CPU. Com 98 relatos por rodada de avaliação, uma medição
levaria mais de 5 horas — o que inviabiliza o ciclo "mudo algo, meço, comparo"
que o trilho B2 precisa ter para chegar ao Marco 1 com números.

## Resultado esperado

- Nenhum arquivo gerado versionado, sem perder nada do disco.
- Um clone limpo sobe com `docker compose up` sem passo manual escondido.
- Com a GPU ativa, a chamada ao modelo cair de minutos para segundos.

## Resultado obtido

| Verificação | Resultado |
|---|---|
| Artefatos gerados ainda versionados | **0** (eram 41) |
| Áudios de teste preservados | 2 |
| Arquivos `.pyc` intactos no disco | 43 |
| `docker compose config` sem `.env` | OK (antes falhava) |
| API respondendo | `{"status":"ok"}` |
| Frontend | HTTP 200 |
| Modelo carregado | **100% GPU** (`ollama ps`) |

Atingido. O modelo roda inteiramente na RTX 4060; a primeira chamada levou 44s
porque inclui carregar 2,6 GB na memória da placa — as seguintes não pagam
esse custo.

**Efeito colateral não previsto:** o Docker Desktop desta máquina estava
quebrado desde 28/04, com arquivos de socket órfãos que o Windows se recusava
a apagar por qualquer via (`Remove-Item`, prefixo `\\?\`, `fsutil`). A solução
foi renomear as pastas de runtime (`AppData\Local\Docker\run` e
`AppData\Local\docker-secrets-engine`), que o Docker recria limpas. Registrado
aqui porque pode acontecer com os outros: **não usar "Reset to factory
defaults"**, que apaga imagens e volumes de todos os projetos.

## O que mudou no repositório

**Commit [`bc14293`](https://github.com/vinizika/tcc/commit/bc14293)** — higiene e ambiente:

| Arquivo | Mudança |
|---|---|
| 40 `.pyc` + `data/.DS_Store` | removidos do índice do Git (mantidos no disco) |
| `.gitignore` | ignora rodadas descartáveis de avaliação; comentário explicando por que os dois áudios seguem versionados |
| `backend/.dockerignore` | **novo** — imagem para de copiar `.venv`, banco Chroma e uploads |
| `.env.example` | **novo** — configuração documentada |
| `docker-compose.yml` | `.env` opcional; `OLLAMA_HOST` injetado no backend |
| `docker-compose.gpu.yml` | **novo** — override opcional para GPU NVIDIA |
| `README.md` | seção de Docker Compose, incluindo o `ollama pull` que faltava |
| `scripts/requirements.txt` | **novo** — dependências dos scripts |

**Commit [`d654555`](https://github.com/vinizika/tcc/commit/d654555)** — diário
do trilho com o estado inicial e as duas limitações descritas abaixo.

## Duas limitações registradas nesta rodada

Encontradas ao revisar os dados, e que afetam a leitura dos próximos números:

1. **Rótulo e origem estão confundidos no conjunto de avaliação.** Nas 98
   linhas Dog/Cat, as 71 emergências são todas `original` e as 27 não
   emergências são todas `llm_data_augmentation`. Ou seja: o recall de não
   emergência mede o quanto o modelo reconhece o vocabulário dos 5 sintomas
   leves usados na geração sintética, e não a capacidade geral de distinguir
   gravidade. Não invalida a métrica, mas precisa estar dito no artigo — e as
   próximas rodadas vão reportar as métricas separadas por origem.
2. **A base está em português e os relatos de avaliação em inglês.** Os
   relatos são montados como "Animal: Dog. Sintomas observados: Fever,
   Vomiting...", enquanto os 7 protocolos indexados são texto em português.
   Isso tende a limitar o ganho do RAG na primeira medição ponta a ponta, por
   um motivo de recuperação e não de geração. O runner vai registrar o score
   máximo da recuperação em cada linha para que isso apareça como evidência.

## Próximo passo

Centralizar a configuração do modelo (endereço e nome estavam escritos à mão em
quatro arquivos, o que fazia o projeto funcionar em Docker **ou** local, nunca
nos dois) e então substituir a geração simulada pela classificação real
ancorada nos documentos.
