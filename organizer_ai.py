from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Sequence

HOST_PADRAO = "http://localhost:11434"
MODELO_PADRAO = "llama3.2"
TIMEOUT_PADRAO = 3

EXTENSOES_TEXTO = {"txt", "md", "csv", "log", "json", "py", "js", "yml", "yaml"}
TAMANHO_TRECHO = 500


def ollama_disponivel(host: str = HOST_PADRAO, timeout: int = TIMEOUT_PADRAO) -> bool:
    """Verifica se um servidor Ollama está acessível em `host`."""
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=timeout):
            return True
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _trecho_conteudo(caminho_arquivo: str, extensao: str) -> str:
    if extensao not in EXTENSOES_TEXTO:
        return ""
    try:
        with open(caminho_arquivo, encoding="utf-8", errors="ignore") as arquivo:
            return arquivo.read(TAMANHO_TRECHO)
    except OSError:
        return ""


def classificar_arquivo(
    nome_arquivo: str,
    caminho_arquivo: str,
    extensao: str,
    categorias_disponiveis: Sequence[str],
    host: str = HOST_PADRAO,
    modelo: str = MODELO_PADRAO,
    timeout: int = TIMEOUT_PADRAO,
) -> str | None:
    """Pede a um modelo local (via Ollama) para escolher a melhor categoria.

    Retorna o nome de uma das `categorias_disponiveis` ou `None` se o
    Ollama não estiver disponível, a chamada falhar, ou a resposta não
    corresponder a nenhuma categoria conhecida (nesses casos o chamador
    deve cair de volta para a classificação por extensão).
    """
    if not categorias_disponiveis:
        return None

    trecho = _trecho_conteudo(caminho_arquivo, extensao)
    prompt = (
        "Classifique o arquivo abaixo em UMA das categorias a seguir, "
        "respondendo APENAS com o nome exato da categoria escolhida, "
        "sem explicações e sem pontuação.\n\n"
        f"Categorias possíveis: {', '.join(categorias_disponiveis)}\n"
        f"Nome do arquivo: {nome_arquivo}\n"
    )
    if trecho:
        prompt += f"Trecho do conteúdo: {trecho}\n"

    corpo = json.dumps({"model": modelo, "prompt": prompt, "stream": False}).encode(
        "utf-8"
    )
    requisicao = urllib.request.Request(
        f"{host}/api/generate",
        data=corpo,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
            corpo_resposta = json.loads(resposta.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return None

    resposta_texto = corpo_resposta.get("response", "").strip().lower()
    for categoria in categorias_disponiveis:
        if categoria.lower() in resposta_texto:
            return categoria
    return None
