import json
import os
import time

import pytest

from organizer_core import (
    carregar_mapa_categorias,
    expandir_categorias,
    organizar_arquivos,
)


def _criar_arquivo(diretorio, nome, conteudo="conteudo"):
    caminho = os.path.join(diretorio, nome)
    with open(caminho, "w") as arquivo:
        arquivo.write(conteudo)
    return caminho


def test_organiza_arquivos_por_extensao(tmp_path):
    _criar_arquivo(tmp_path, "foto.png")
    _criar_arquivo(tmp_path, "documento.pdf")
    _criar_arquivo(tmp_path, "outro.PNG")

    stats = organizar_arquivos(str(tmp_path))

    assert stats["movidos"] == 3
    assert stats["erros"] == []
    assert set(os.listdir(tmp_path)) == {"png", "pdf"}
    assert set(os.listdir(tmp_path / "png")) == {"foto.png", "outro.PNG"}
    assert os.listdir(tmp_path / "pdf") == ["documento.pdf"]


def test_arquivo_sem_extensao_vai_para_pasta_propria(tmp_path):
    _criar_arquivo(tmp_path, "LEIAME")

    stats = organizar_arquivos(str(tmp_path))

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "sem_extensao") == ["LEIAME"]


def test_arquivo_oculto_nao_vira_nome_de_pasta_gigante(tmp_path):
    _criar_arquivo(tmp_path, ".env")

    stats = organizar_arquivos(str(tmp_path))

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "sem_extensao") == [".env"]


def test_diretorio_invalido_gera_erro(tmp_path):
    with pytest.raises(NotADirectoryError):
        organizar_arquivos(str(tmp_path / "nao_existe"))


def test_diretorio_vazio_gera_erro(tmp_path):
    with pytest.raises(NotADirectoryError):
        organizar_arquivos("")


def test_colisao_de_nomes_nao_sobrescreve_arquivo_existente(tmp_path):
    pasta_txt = tmp_path / "txt"
    pasta_txt.mkdir()
    (pasta_txt / "notas.txt").write_text("original")
    _criar_arquivo(tmp_path, "notas.txt", conteudo="novo")

    stats = organizar_arquivos(str(tmp_path))

    assert stats["movidos"] == 1
    assert stats["erros"] == []
    arquivos = set(os.listdir(pasta_txt))
    assert "notas.txt" in arquivos
    assert any(nome.startswith("notas_") for nome in arquivos)
    assert (pasta_txt / "notas.txt").read_text() == "original"


def test_filtro_por_ano_ignora_arquivos_antigos(tmp_path):
    caminho = _criar_arquivo(tmp_path, "antigo.txt")
    timestamp_antigo = time.mktime((2015, 1, 1, 0, 0, 0, 0, 0, 0))
    os.utime(caminho, (timestamp_antigo, timestamp_antigo))

    stats = organizar_arquivos(str(tmp_path), ano_minimo=2020)

    assert stats["movidos"] == 0
    assert stats["ignorados"] == 1
    assert os.path.exists(caminho)


def test_filtro_por_ano_move_arquivos_recentes(tmp_path):
    _criar_arquivo(tmp_path, "recente.txt")

    stats = organizar_arquivos(str(tmp_path), ano_minimo=2000)

    assert stats["movidos"] == 1
    assert stats["ignorados"] == 0


def test_progresso_callback_e_chamado_para_cada_arquivo(tmp_path):
    _criar_arquivo(tmp_path, "a.txt")
    _criar_arquivo(tmp_path, "b.txt")
    chamadas = []

    stats = organizar_arquivos(
        str(tmp_path),
        progresso_callback=lambda indice, total, nome, status, pasta: chamadas.append(
            (indice, total, nome, status, pasta)
        ),
    )

    assert stats["movidos"] == 2
    assert len(chamadas) == 2
    assert {c[1] for c in chamadas} == {2}
    assert {c[3] for c in chamadas} == {"movido"}
    assert {c[4] for c in chamadas} == {"txt"}
    assert {c[0] for c in chamadas} == {1, 2}


def test_progresso_callback_reporta_ignorado(tmp_path):
    caminho = _criar_arquivo(tmp_path, "antigo.txt")
    timestamp_antigo = time.mktime((2015, 1, 1, 0, 0, 0, 0, 0, 0))
    os.utime(caminho, (timestamp_antigo, timestamp_antigo))
    chamadas = []

    organizar_arquivos(
        str(tmp_path),
        ano_minimo=2020,
        progresso_callback=lambda indice, total, nome, status, pasta: chamadas.append(
            status
        ),
    )

    assert chamadas == ["ignorado"]


def test_expandir_categorias_inverte_o_mapa():
    mapa = expandir_categorias({"imagens": ["jpg", "PNG"], "documentos": ["pdf"]})

    assert mapa == {"jpg": "imagens", "png": "imagens", "pdf": "documentos"}


def test_carregar_mapa_categorias_usa_padrao_sem_config():
    mapa = carregar_mapa_categorias()

    assert mapa["png"] == "imagens"
    assert mapa["pdf"] == "documentos"


def test_carregar_mapa_categorias_le_arquivo_customizado(tmp_path):
    caminho_config = tmp_path / "categorias.json"
    caminho_config.write_text(json.dumps({"projetos": ["py", "js"]}))

    mapa = carregar_mapa_categorias(str(caminho_config))

    assert mapa == {"py": "projetos", "js": "projetos"}


def test_organiza_por_categoria_quando_mapa_e_informado(tmp_path):
    _criar_arquivo(tmp_path, "foto.jpg")
    _criar_arquivo(tmp_path, "relatorio.pdf")
    mapa = carregar_mapa_categorias()

    stats = organizar_arquivos(str(tmp_path), mapa_categorias=mapa)

    assert stats["movidos"] == 2
    assert set(os.listdir(tmp_path)) == {"imagens", "documentos"}
    assert os.listdir(tmp_path / "imagens") == ["foto.jpg"]
    assert os.listdir(tmp_path / "documentos") == ["relatorio.pdf"]


def test_modo_simular_nao_move_nenhum_arquivo(tmp_path):
    caminho = _criar_arquivo(tmp_path, "foto.jpg")
    mapa = carregar_mapa_categorias()

    stats = organizar_arquivos(str(tmp_path), mapa_categorias=mapa, simular=True)

    assert stats["movidos"] == 1
    assert os.path.exists(caminho)
    assert not os.path.exists(tmp_path / "imagens")
    assert os.listdir(tmp_path) == ["foto.jpg"]


def test_classificador_categoria_tem_prioridade_sobre_mapa(tmp_path):
    _criar_arquivo(tmp_path, "fatura.pdf")

    stats = organizar_arquivos(
        str(tmp_path),
        mapa_categorias=carregar_mapa_categorias(),
        classificador_categoria=lambda nome, caminho, extensao: "financeiro",
    )

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "financeiro") == ["fatura.pdf"]


def test_classificador_categoria_com_erro_cai_para_extensao(tmp_path):
    _criar_arquivo(tmp_path, "fatura.pdf")

    def classificador_com_erro(nome, caminho, extensao):
        raise RuntimeError("falha simulada de rede")

    stats = organizar_arquivos(
        str(tmp_path), classificador_categoria=classificador_com_erro
    )

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "pdf") == ["fatura.pdf"]
