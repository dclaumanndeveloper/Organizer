import os

from organizer_config import carregar_config, salvar_config


def test_carregar_config_sem_arquivo_retorna_vazio(tmp_path):
    caminho = tmp_path / "config.json"

    assert carregar_config(str(caminho)) == {}


def test_carregar_config_com_json_invalido_retorna_vazio(tmp_path):
    caminho = tmp_path / "config.json"
    caminho.write_text("isso nao e json valido {{{")

    assert carregar_config(str(caminho)) == {}


def test_carregar_config_com_json_que_nao_e_objeto_retorna_vazio(tmp_path):
    caminho = tmp_path / "config.json"
    caminho.write_text("[1, 2, 3]")

    assert carregar_config(str(caminho)) == {}


def test_salvar_e_carregar_config_round_trip(tmp_path):
    caminho = tmp_path / "config.json"
    config = {"ultimo_diretorio": "/home/usuario/downloads", "simular": True}

    salvar_config(config, str(caminho))

    assert carregar_config(str(caminho)) == config


def test_salvar_config_cria_diretorio_pai(tmp_path):
    caminho = tmp_path / "subpasta" / "config.json"

    salvar_config({"ano_minimo": "2020"}, str(caminho))

    assert os.path.exists(caminho)
    assert carregar_config(str(caminho)) == {"ano_minimo": "2020"}
