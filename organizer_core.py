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


def organizar_arquivos(
    diretorio,
    ano_minimo=None,
    mapa_categorias=None,
    classificador_categoria=None,
    simular=False,
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
    - `progresso_callback`: chamado a cada arquivo processado como
      `progresso_callback(indice, total, nome_arquivo, status, pasta_destino)`,
      onde `status` é "movido", "ignorado" ou "erro".

    Retorna um dicionário com as estatísticas da execução:
    {"movidos": int, "ignorados": int, "erros": [str, ...]}
    """
    if not diretorio or not os.path.isdir(diretorio):
        raise NotADirectoryError(f"Diretório inválido: {diretorio!r}")

    stats = {"movidos": 0, "ignorados": 0, "erros": []}

    nomes_arquivos = [
        nome
        for nome in os.listdir(diretorio)
        if os.path.isfile(os.path.join(diretorio, nome))
    ]
    total = len(nomes_arquivos)
    destinos_reservados = set()

    for indice, nome_arquivo in enumerate(nomes_arquivos, start=1):
        caminho_origem = os.path.join(diretorio, nome_arquivo)

        if ano_minimo is not None:
            try:
                if _ano_modificacao(caminho_origem) < ano_minimo:
                    stats["ignorados"] += 1
                    if progresso_callback is not None:
                        progresso_callback(indice, total, nome_arquivo, "ignorado", None)
                    continue
            except OSError as exc:
                stats["erros"].append(f"{nome_arquivo}: {exc}")
                if progresso_callback is not None:
                    progresso_callback(indice, total, nome_arquivo, "erro", None)
                continue

        extensao = _extensao_arquivo(nome_arquivo)
        categoria = None
        if classificador_categoria is not None and extensao != "sem_extensao":
            try:
                categoria = classificador_categoria(nome_arquivo, caminho_origem, extensao)
            except Exception:
                categoria = None

        pasta_destino_nome = categoria or _pasta_destino(extensao, mapa_categorias)
        pasta_destino = os.path.join(diretorio, pasta_destino_nome)
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
            stats["erros"].append(f"{nome_arquivo}: {exc}")
            status = "erro"

        if progresso_callback is not None:
            progresso_callback(indice, total, nome_arquivo, status, pasta_destino_nome)

    return stats
