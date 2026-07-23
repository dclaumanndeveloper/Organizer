import os

from organizer_config import (
    carregar_config,
    carregar_perfil,
    excluir_perfil,
    listar_perfis,
    salvar_config,
    salvar_perfil,
)


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


def test_listar_perfis_sem_arquivo_retorna_vazio(tmp_path):
    caminho = tmp_path / "perfis.json"

    assert listar_perfis(str(caminho)) == {}


def test_listar_perfis_com_json_invalido_retorna_vazio(tmp_path):
    caminho = tmp_path / "perfis.json"
    caminho.write_text("isso nao e json valido {{{")

    assert listar_perfis(str(caminho)) == {}


def test_listar_perfis_com_json_que_nao_e_objeto_retorna_vazio(tmp_path):
    caminho = tmp_path / "perfis.json"
    caminho.write_text("[1, 2, 3]")

    assert listar_perfis(str(caminho)) == {}


def test_salvar_e_carregar_perfil_round_trip(tmp_path):
    caminho = tmp_path / "perfis.json"
    dados = {"ultimo_diretorio": "/home/usuario/fotos", "simular": False}

    salvar_perfil("trabalho", dados, str(caminho))

    assert carregar_perfil("trabalho", str(caminho)) == dados
    assert listar_perfis(str(caminho)) == {"trabalho": dados}


def test_salvar_perfil_cria_diretorio_pai(tmp_path):
    caminho = tmp_path / "subpasta" / "perfis.json"

    salvar_perfil("pessoal", {"ano_minimo": "2019"}, str(caminho))

    assert os.path.exists(caminho)
    assert carregar_perfil("pessoal", str(caminho)) == {"ano_minimo": "2019"}


def test_salvar_perfil_nao_afeta_outros_perfis(tmp_path):
    caminho = tmp_path / "perfis.json"
    salvar_perfil("a", {"simular": True}, str(caminho))
    salvar_perfil("b", {"simular": False}, str(caminho))

    assert listar_perfis(str(caminho)) == {
        "a": {"simular": True},
        "b": {"simular": False},
    }


def test_salvar_perfil_sobrescreve_perfil_existente(tmp_path):
    caminho = tmp_path / "perfis.json"
    salvar_perfil("trabalho", {"simular": True}, str(caminho))
    salvar_perfil("trabalho", {"simular": False}, str(caminho))

    assert carregar_perfil("trabalho", str(caminho)) == {"simular": False}


def test_carregar_perfil_inexistente_retorna_none(tmp_path):
    caminho = tmp_path / "perfis.json"

    assert carregar_perfil("nao_existe", str(caminho)) is None


def test_excluir_perfil_existente(tmp_path):
    caminho = tmp_path / "perfis.json"
    salvar_perfil("trabalho", {"simular": True}, str(caminho))

    assert excluir_perfil("trabalho", str(caminho)) is True
    assert listar_perfis(str(caminho)) == {}


def test_excluir_perfil_inexistente_retorna_false(tmp_path):
    caminho = tmp_path / "perfis.json"

    assert excluir_perfil("nao_existe", str(caminho)) is False
