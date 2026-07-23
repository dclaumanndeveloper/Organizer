import json
import os
from datetime import datetime

CATEGORIAS_PADRAO = {
    "imagens": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "tiff", "ico"],
    "documentos": ["pdf", "doc", "docx", "odt", "txt", "rtf", "md"],
    "planilhas": ["xls", "xlsx", "ods", "csv"],
    "apresentacoes": ["ppt", "pptx", "odp"],
    "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
    "video": ["mp4", "mov", "avi", "mkv", "wmv", "flv"],
    "compactados": ["zip", "rar", "7z", "tar", "gz"],
}


def expandir_categorias(categorias_por_grupo):
    """Converte {"categoria": [extensoes]} em {extensao: "categoria"}."""
    mapa = {}
    for categoria, extensoes in categorias_por_grupo.items():
        for extensao in extensoes:
            mapa[extensao.lower()] = categoria
    return mapa


def carregar_mapa_categorias(caminho_config=None):
    """Carrega um mapa extensao->categoria de um arquivo JSON.

    Se `caminho_config` for informado e existir, o JSON deve ter o formato
    {"categoria": ["ext1", "ext2", ...], ...}. Caso contrário, usa as
    categorias padrão embutidas (`CATEGORIAS_PADRAO`).
    """
    if caminho_config and os.path.exists(caminho_config):
        with open(caminho_config, "r", encoding="utf-8") as arquivo:
            categorias_por_grupo = json.load(arquivo)
    else:
        categorias_por_grupo = CATEGORIAS_PADRAO
    return expandir_categorias(categorias_por_grupo)


def _extensao_arquivo(nome_arquivo):
    base = os.path.basename(nome_arquivo)
    if base.startswith(".") or "." not in base.lstrip("."):
        return "sem_extensao"
    return base.rsplit(".", 1)[-1].lower()


def _pasta_destino(extensao, mapa_categorias):
    if extensao == "sem_extensao" or not mapa_categorias:
        return extensao
    return mapa_categorias.get(extensao, extensao)


def _ano_modificacao(caminho_arquivo):
    timestamp = os.path.getmtime(caminho_arquivo)
    return datetime.fromtimestamp(timestamp).year


def _destino_sem_colisao(caminho_destino, nomes_em_uso):
    if caminho_destino not in nomes_em_uso and not os.path.exists(caminho_destino):
        return caminho_destino

    pasta, nome = os.path.split(caminho_destino)
    base, ext = os.path.splitext(nome)
    contador = 1
    while True:
        novo_caminho = os.path.join(pasta, f"{base}_{contador}{ext}")
        if novo_caminho not in nomes_em_uso and not os.path.exists(novo_caminho):
            return novo_caminho
        contador += 1


def _diretorios_a_processar(diretorio_raiz, recursivo, pastas_reservadas):
    """Lista, de uma vez só, todas as pastas a organizar.

    Feito num único snapshot ANTES de mover qualquer arquivo, para que as
    pastas de destino criadas durante a organização (ex: "imagens",
    "documentos") nunca entrem nessa lista e não sejam reprocessadas na
    mesma execução.
    """
    if not recursivo:
        return [diretorio_raiz]

    diretorios = [diretorio_raiz]
    pilha = [diretorio_raiz]
    while pilha:
        atual = pilha.pop()
        try:
            entradas = os.listdir(atual)
        except OSError:
            continue
        for nome in entradas:
            if nome in pastas_reservadas:
                continue
            caminho = os.path.join(atual, nome)
            if os.path.isdir(caminho):
                diretorios.append(caminho)
                pilha.append(caminho)
    return diretorios


def organizar_arquivos(
    diretorio,
    ano_minimo=None,
    mapa_categorias=None,
    classificador_categoria=None,
    simular=False,
    recursivo=False,
    progresso_callback=None,
):
    """Organiza os arquivos de `diretorio` em subpastas por extensão ou categoria.

    - `ano_minimo`: se informado, arquivos modificados antes desse ano são
      ignorados (não são movidos).
    - `mapa_categorias`: dicionário extensao->categoria (ver
      `carregar_mapa_categorias`). Se informado, arquivos são agrupados por
      categoria (ex: "imagens") em vez de por extensão crua (ex: "png").
    - `classificador_categoria`: função opcional
      `(nome_arquivo, caminho_arquivo, extensao) -> categoria_ou_None`,
      chamada antes do mapa de categorias para cada arquivo. Se retornar uma
      categoria, ela tem prioridade sobre `mapa_categorias`; se retornar
      `None` ou lançar uma exceção, cai de volta para `mapa_categorias`/
      extensão. Usado para plugar classificação por IA sem acoplar esta
      função a nenhum provedor específico.
    - `simular`: se `True`, calcula o que seria feito sem mover nenhum
      arquivo nem criar pastas (modo de pré-visualização).
    - `recursivo`: se `True`, organiza também os arquivos de subpastas
      (cada subpasta ganha suas próprias pastas de destino, dentro dela
      mesma). Pastas cujo nome coincida com uma categoria/`"sem_extensao"`
      não são percorridas, para não reprocessar pastas de destino já
      criadas em execuções anteriores.
    - `progresso_callback`: chamado a cada arquivo processado como
      `progresso_callback(indice, total, nome_arquivo, status, pasta_destino)`,
      onde `status` é "movido", "ignorado" ou "erro". `nome_arquivo` e
      `pasta_destino` são relativos a `diretorio` (podem incluir subpastas
      quando `recursivo=True`).

    Retorna um dicionário com as estatísticas da execução:
    {"movidos": int, "ignorados": int, "erros": [str, ...]}
    """
    if not diretorio or not os.path.isdir(diretorio):
        raise NotADirectoryError(f"Diretório inválido: {diretorio!r}")

    stats = {"movidos": 0, "ignorados": 0, "erros": []}

    pastas_reservadas = set(mapa_categorias.values()) if mapa_categorias else set()
    pastas_reservadas.add("sem_extensao")

    diretorios = _diretorios_a_processar(diretorio, recursivo, pastas_reservadas)

    arquivos_por_pasta = {}
    total = 0
    for pasta in diretorios:
        nomes = [
            nome
            for nome in os.listdir(pasta)
            if os.path.isfile(os.path.join(pasta, nome))
        ]
        arquivos_por_pasta[pasta] = nomes
        total += len(nomes)

    destinos_reservados = set()
    indice = 0

    for pasta_atual in diretorios:
        for nome_arquivo in arquivos_por_pasta[pasta_atual]:
            indice += 1
            caminho_origem = os.path.join(pasta_atual, nome_arquivo)
            nome_exibicao = os.path.relpath(caminho_origem, diretorio)

            if ano_minimo is not None:
                try:
                    if _ano_modificacao(caminho_origem) < ano_minimo:
                        stats["ignorados"] += 1
                        if progresso_callback is not None:
                            progresso_callback(
                                indice, total, nome_exibicao, "ignorado", None
                            )
                        continue
                except OSError as exc:
                    stats["erros"].append(f"{nome_exibicao}: {exc}")
                    if progresso_callback is not None:
                        progresso_callback(indice, total, nome_exibicao, "erro", None)
                    continue

            extensao = _extensao_arquivo(nome_arquivo)
            categoria = None
            if classificador_categoria is not None and extensao != "sem_extensao":
                try:
                    categoria = classificador_categoria(
                        nome_arquivo, caminho_origem, extensao
                    )
                except Exception:
                    categoria = None

            pasta_destino_nome = categoria or _pasta_destino(extensao, mapa_categorias)
            pasta_destino = os.path.join(pasta_atual, pasta_destino_nome)
            status = "movido"

            try:
                caminho_destino = _destino_sem_colisao(
                    os.path.join(pasta_destino, nome_arquivo), destinos_reservados
                )
                destinos_reservados.add(caminho_destino)
                if not simular:
                    os.makedirs(pasta_destino, exist_ok=True)
                    os.replace(caminho_origem, caminho_destino)
                stats["movidos"] += 1
            except OSError as exc:
                stats["erros"].append(f"{nome_exibicao}: {exc}")
                status = "erro"

            if progresso_callback is not None:
                pasta_destino_exibicao = os.path.relpath(pasta_destino, diretorio)
                progresso_callback(
                    indice, total, nome_exibicao, status, pasta_destino_exibicao
                )

    return stats
