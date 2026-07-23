import os
from datetime import datetime


def _extensao_arquivo(nome_arquivo):
    base = os.path.basename(nome_arquivo)
    if base.startswith(".") or "." not in base.lstrip("."):
        return "sem_extensao"
    return base.rsplit(".", 1)[-1].lower()


def _ano_modificacao(caminho_arquivo):
    timestamp = os.path.getmtime(caminho_arquivo)
    return datetime.fromtimestamp(timestamp).year


def _destino_sem_colisao(caminho_destino):
    if not os.path.exists(caminho_destino):
        return caminho_destino

    pasta, nome = os.path.split(caminho_destino)
    base, ext = os.path.splitext(nome)
    contador = 1
    while True:
        novo_caminho = os.path.join(pasta, f"{base}_{contador}{ext}")
        if not os.path.exists(novo_caminho):
            return novo_caminho
        contador += 1


def organizar_arquivos(diretorio, ano_minimo=None, progresso_callback=None):
    """Organiza os arquivos de `diretorio` em subpastas por extensão.

    Se `ano_minimo` for informado, arquivos cuja última modificação seja
    anterior a esse ano são ignorados (não são movidos).

    Se `progresso_callback` for informado, é chamado a cada arquivo
    processado como `progresso_callback(indice, total, nome_arquivo, status)`,
    onde `status` é uma das strings "movido", "ignorado" ou "erro".

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

    for indice, nome_arquivo in enumerate(nomes_arquivos, start=1):
        caminho_origem = os.path.join(diretorio, nome_arquivo)
        status = "movido"

        if ano_minimo is not None:
            try:
                if _ano_modificacao(caminho_origem) < ano_minimo:
                    stats["ignorados"] += 1
                    if progresso_callback is not None:
                        progresso_callback(indice, total, nome_arquivo, "ignorado")
                    continue
            except OSError as exc:
                stats["erros"].append(f"{nome_arquivo}: {exc}")
                if progresso_callback is not None:
                    progresso_callback(indice, total, nome_arquivo, "erro")
                continue

        pasta_destino = os.path.join(diretorio, _extensao_arquivo(nome_arquivo))

        try:
            os.makedirs(pasta_destino, exist_ok=True)
            caminho_destino = _destino_sem_colisao(
                os.path.join(pasta_destino, nome_arquivo)
            )
            os.replace(caminho_origem, caminho_destino)
            stats["movidos"] += 1
        except OSError as exc:
            stats["erros"].append(f"{nome_arquivo}: {exc}")
            status = "erro"

        if progresso_callback is not None:
            progresso_callback(indice, total, nome_arquivo, status)

    return stats
