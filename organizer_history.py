from __future__ import annotations

import json
import os
import time
from typing import Any

Movimento = dict[str, str]
Execucao = dict[str, Any]

NOME_ARQUIVO_HISTORICO = "historico.json"


def caminho_historico_padrao() -> str:
    return os.path.join(
        os.path.expanduser("~"), ".organizador_arquivos", NOME_ARQUIVO_HISTORICO
    )


def carregar_historico(caminho: str | None = None) -> list[Execucao]:
    """Carrega a lista de execuções registradas (mais antiga primeiro).

    Retorna uma lista vazia se o arquivo não existir ou estiver
    corrompido — nunca lança exceção.
    """
    caminho = caminho or caminho_historico_padrao()
    if not os.path.exists(caminho):
        return []
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (OSError, ValueError):
        return []
    return conteudo if isinstance(conteudo, list) else []


def _salvar_historico(historico: list[Execucao], caminho: str) -> None:
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, indent=2, ensure_ascii=False)


def registrar_operacao(movimentos: list[Movimento], caminho: str | None = None) -> None:
    """Registra uma nova execução no histórico.

    `movimentos` é a lista de {"origem": ..., "destino": ...} retornada por
    `organizar_arquivos` em `stats["movimentos"]`. Não faz nada se a lista
    estiver vazia (nada foi realmente movido).
    """
    if not movimentos:
        return

    caminho = caminho or caminho_historico_padrao()
    historico = carregar_historico(caminho)
    historico.append({"timestamp": time.time(), "movimentos": movimentos})
    _salvar_historico(historico, caminho)


def desfazer_ultima_operacao(caminho: str | None = None) -> dict[str, Any]:
    """Reverte a última execução registrada, movendo os arquivos de volta.

    A entrada é removida do histórico mesmo que alguns arquivos não possam
    ser revertidos (ex: já foram movidos/apagados manualmente pelo
    usuário) — esses casos aparecem em `stats["erros"]`.

    Levanta `ValueError` se não houver nenhuma execução registrada.
    Retorna {"revertidos": int, "erros": [str, ...]}.
    """
    caminho = caminho or caminho_historico_padrao()
    historico = carregar_historico(caminho)
    if not historico:
        raise ValueError("Não há nenhuma organização registrada para desfazer.")

    ultima_execucao = historico.pop()
    stats: dict[str, Any] = {"revertidos": 0, "erros": []}

    for movimento in reversed(ultima_execucao["movimentos"]):
        origem = movimento["origem"]
        destino = movimento["destino"]

        if not os.path.exists(destino):
            stats["erros"].append(
                f"{destino}: arquivo não encontrado (já deve ter sido movido "
                "ou apagado manualmente)"
            )
            continue
        if os.path.exists(origem):
            stats["erros"].append(
                f"{origem}: já existe um arquivo nesse local, pulando"
            )
            continue

        try:
            pasta_origem = os.path.dirname(origem)
            if pasta_origem:
                os.makedirs(pasta_origem, exist_ok=True)
            os.replace(destino, origem)
            stats["revertidos"] += 1
        except OSError as exc:
            stats["erros"].append(f"{destino}: {exc}")

    _salvar_historico(historico, caminho)
    return stats
