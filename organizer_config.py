from __future__ import annotations

import json
import os
from typing import Any

NOME_ARQUIVO_CONFIG = "config.json"
NOME_ARQUIVO_PERFIS = "perfis.json"


def caminho_config_padrao() -> str:
    return os.path.join(
        os.path.expanduser("~"), ".organizador_arquivos", NOME_ARQUIVO_CONFIG
    )


def carregar_config(caminho: str | None = None) -> dict[str, Any]:
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


def salvar_config(config: dict[str, Any], caminho: str | None = None) -> None:
    caminho = caminho or caminho_config_padrao()
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(config, arquivo, indent=2, ensure_ascii=False)


def caminho_perfis_padrao() -> str:
    return os.path.join(
        os.path.expanduser("~"), ".organizador_arquivos", NOME_ARQUIVO_PERFIS
    )


def listar_perfis(caminho: str | None = None) -> dict[str, Any]:
    """Carrega todos os perfis salvos, indexados por nome.

    Retorna um dicionário vazio se o arquivo não existir ou estiver
    corrompido — nunca lança exceção, pelo mesmo motivo de `carregar_config`.
    """
    caminho = caminho or caminho_perfis_padrao()
    if not os.path.exists(caminho):
        return {}
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (OSError, ValueError):
        return {}
    return conteudo if isinstance(conteudo, dict) else {}


def salvar_perfil(nome: str, dados: dict[str, Any], caminho: str | None = None) -> None:
    caminho = caminho or caminho_perfis_padrao()
    perfis = listar_perfis(caminho)
    perfis[nome] = dados
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(perfis, arquivo, indent=2, ensure_ascii=False)


def carregar_perfil(nome: str, caminho: str | None = None) -> dict[str, Any] | None:
    perfis = listar_perfis(caminho)
    perfil = perfis.get(nome)
    return perfil if isinstance(perfil, dict) else None


def excluir_perfil(nome: str, caminho: str | None = None) -> bool:
    caminho = caminho or caminho_perfis_padrao()
    perfis = listar_perfis(caminho)
    if nome not in perfis:
        return False
    del perfis[nome]
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(perfis, arquivo, indent=2, ensure_ascii=False)
    return True
