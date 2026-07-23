import json
import os

NOME_ARQUIVO_CONFIG = "config.json"


def caminho_config_padrao():
    return os.path.join(
        os.path.expanduser("~"), ".organizador_arquivos", NOME_ARQUIVO_CONFIG
    )


def carregar_config(caminho=None):
    """Carrega as últimas opções usadas (pasta, ano, checkboxes).

    Retorna um dicionário vazio se o arquivo não existir ou estiver
    corrompido — nunca lança exceção, já que perder um perfil salvo não
    deveria impedir o uso do programa.
    """
    caminho = caminho or caminho_config_padrao()
    if not os.path.exists(caminho):
        return {}
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (OSError, ValueError):
        return {}
    return conteudo if isinstance(conteudo, dict) else {}


def salvar_config(config, caminho=None):
    caminho = caminho or caminho_config_padrao()
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(config, arquivo, indent=2, ensure_ascii=False)
