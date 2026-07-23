import os

import pytest

from organizer_history import (
    carregar_historico,
    desfazer_ultima_operacao,
    registrar_operacao,
)


def _criar_arquivo(caminho, conteudo="conteudo"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w") as arquivo:
        arquivo.write(conteudo)


def test_carregar_historico_sem_arquivo_retorna_vazio(tmp_path):
    assert carregar_historico(str(tmp_path / "historico.json")) == []


def test_registrar_nao_salva_nada_se_movimentos_vazio(tmp_path):
    caminho = tmp_path / "historico.json"

    registrar_operacao([], str(caminho))

    assert not os.path.exists(caminho)


def test_registrar_e_carregar_round_trip(tmp_path):
    caminho = tmp_path / "historico.json"
    movimentos = [{"origem": "/a/foto.jpg", "destino": "/a/imagens/foto.jpg"}]

    registrar_operacao(movimentos, str(caminho))
    historico = carregar_historico(str(caminho))

    assert len(historico) == 1
    assert historico[0]["movimentos"] == movimentos
    assert "timestamp" in historico[0]


def test_desfazer_sem_historico_gera_erro(tmp_path):
    with pytest.raises(ValueError):
        desfazer_ultima_operacao(str(tmp_path / "historico.json"))


def test_desfazer_move_arquivos_de_volta(tmp_path):
    caminho_historico = tmp_path / "historico.json"
    origem = tmp_path / "foto.jpg"
    destino = tmp_path / "imagens" / "foto.jpg"
    _criar_arquivo(str(destino))

    registrar_operacao(
        [{"origem": str(origem), "destino": str(destino)}], str(caminho_historico)
    )
    stats = desfazer_ultima_operacao(str(caminho_historico))

    assert stats["revertidos"] == 1
    assert stats["erros"] == []
    assert os.path.exists(origem)
    assert not os.path.exists(destino)
    assert carregar_historico(str(caminho_historico)) == []


def test_desfazer_reporta_erro_se_destino_nao_existe_mais(tmp_path):
    caminho_historico = tmp_path / "historico.json"
    origem = tmp_path / "foto.jpg"
    destino = tmp_path / "imagens" / "foto.jpg"  # nunca criado

    registrar_operacao(
        [{"origem": str(origem), "destino": str(destino)}], str(caminho_historico)
    )
    stats = desfazer_ultima_operacao(str(caminho_historico))

    assert stats["revertidos"] == 0
    assert len(stats["erros"]) == 1
    assert carregar_historico(str(caminho_historico)) == []


def test_desfazer_reporta_erro_se_origem_ja_existe(tmp_path):
    caminho_historico = tmp_path / "historico.json"
    origem = tmp_path / "foto.jpg"
    destino = tmp_path / "imagens" / "foto.jpg"
    _criar_arquivo(str(origem), conteudo="ja existia")
    _criar_arquivo(str(destino), conteudo="movido")

    registrar_operacao(
        [{"origem": str(origem), "destino": str(destino)}], str(caminho_historico)
    )
    stats = desfazer_ultima_operacao(str(caminho_historico))

    assert stats["revertidos"] == 0
    assert len(stats["erros"]) == 1
    assert origem.read_text() == "ja existia"
    assert destino.read_text() == "movido"


def test_desfazer_so_afeta_a_ultima_execucao(tmp_path):
    caminho_historico = tmp_path / "historico.json"
    origem1 = tmp_path / "a.txt"
    destino1 = tmp_path / "txt" / "a.txt"
    _criar_arquivo(str(destino1))
    origem2 = tmp_path / "b.txt"
    destino2 = tmp_path / "txt" / "b.txt"
    _criar_arquivo(str(destino2))

    registrar_operacao(
        [{"origem": str(origem1), "destino": str(destino1)}], str(caminho_historico)
    )
    registrar_operacao(
        [{"origem": str(origem2), "destino": str(destino2)}], str(caminho_historico)
    )

    stats = desfazer_ultima_operacao(str(caminho_historico))

    assert stats["revertidos"] == 1
    assert os.path.exists(origem2)
    assert not os.path.exists(destino2)
    assert not os.path.exists(origem1)
    assert os.path.exists(destino1)
    assert len(carregar_historico(str(caminho_historico))) == 1
