import json
import os
import time

import pytest

from organizer_core import (
    carregar_mapa_categorias,
    carregar_regras,
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


def test_nao_recursivo_ignora_arquivos_em_subpastas(tmp_path):
    _criar_arquivo(tmp_path, "a.txt")
    subpasta = tmp_path / "sub"
    subpasta.mkdir()
    _criar_arquivo(subpasta, "b.txt")

    stats = organizar_arquivos(str(tmp_path))

    assert stats["movidos"] == 1
    assert os.listdir(subpasta) == ["b.txt"]


def test_recursivo_organiza_arquivos_em_subpastas(tmp_path):
    _criar_arquivo(tmp_path, "a.txt")
    subpasta = tmp_path / "sub"
    subpasta.mkdir()
    _criar_arquivo(subpasta, "b.txt")

    stats = organizar_arquivos(str(tmp_path), recursivo=True)

    assert stats["movidos"] == 2
    assert os.listdir(tmp_path / "txt") == ["a.txt"]
    assert os.listdir(subpasta / "txt") == ["b.txt"]


def test_recursivo_nao_reprocessa_pasta_de_categoria_do_mesmo_run(tmp_path):
    _criar_arquivo(tmp_path, "foto.jpg")
    mapa = carregar_mapa_categorias()

    stats = organizar_arquivos(str(tmp_path), mapa_categorias=mapa, recursivo=True)

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "imagens") == ["foto.jpg"]
    assert not os.path.exists(tmp_path / "imagens" / "imagens")


def test_recursivo_no_segundo_run_nao_reorganiza_pasta_ja_criada(tmp_path):
    _criar_arquivo(tmp_path, "foto.jpg")
    mapa = carregar_mapa_categorias()

    organizar_arquivos(str(tmp_path), mapa_categorias=mapa, recursivo=True)
    stats_segundo_run = organizar_arquivos(
        str(tmp_path), mapa_categorias=mapa, recursivo=True
    )

    assert stats_segundo_run["movidos"] == 0
    assert os.listdir(tmp_path / "imagens") == ["foto.jpg"]


def test_progresso_callback_usa_caminho_relativo_em_modo_recursivo(tmp_path):
    subpasta = tmp_path / "sub"
    subpasta.mkdir()
    _criar_arquivo(subpasta, "nota.txt")
    chamadas = []

    organizar_arquivos(
        str(tmp_path),
        recursivo=True,
        progresso_callback=lambda indice, total, nome, status, pasta: chamadas.append(
            (nome, pasta)
        ),
    )

    assert chamadas == [(os.path.join("sub", "nota.txt"), os.path.join("sub", "txt"))]


def test_carregar_regras_sem_arquivo_retorna_vazio(tmp_path):
    assert carregar_regras(str(tmp_path / "nao_existe.json")) == []


def test_carregar_regras_le_arquivo(tmp_path):
    caminho = tmp_path / "regras.json"
    caminho.write_text(
        json.dumps([{"padrao": "(?i)fatura", "categoria": "financeiro"}])
    )

    regras = carregar_regras(str(caminho))

    assert len(regras) == 1
    assert regras[0][1] == "financeiro"
    assert regras[0][0].search("FATURA_boleto.pdf")


def test_regra_por_nome_tem_prioridade_sobre_categoria_e_extensao(tmp_path):
    _criar_arquivo(tmp_path, "fatura_junho.pdf")
    regras = carregar_regras_de_lista([{"padrao": "(?i)fatura", "categoria": "financeiro"}])

    stats = organizar_arquivos(
        str(tmp_path), mapa_categorias=carregar_mapa_categorias(), regras=regras
    )

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "financeiro") == ["fatura_junho.pdf"]


def test_regra_por_nome_tem_prioridade_sobre_classificador_ia(tmp_path):
    _criar_arquivo(tmp_path, "fatura_junho.pdf")
    regras = carregar_regras_de_lista([{"padrao": "(?i)fatura", "categoria": "financeiro"}])

    stats = organizar_arquivos(
        str(tmp_path),
        regras=regras,
        classificador_categoria=lambda nome, caminho, extensao: "outros",
    )

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "financeiro") == ["fatura_junho.pdf"]


def test_sem_match_de_regra_cai_para_categoria(tmp_path):
    _criar_arquivo(tmp_path, "ferias.pdf")
    regras = carregar_regras_de_lista([{"padrao": "(?i)fatura", "categoria": "financeiro"}])

    stats = organizar_arquivos(
        str(tmp_path), mapa_categorias=carregar_mapa_categorias(), regras=regras
    )

    assert stats["movidos"] == 1
    assert os.listdir(tmp_path / "documentos") == ["ferias.pdf"]


def test_detectar_duplicados_move_arquivo_repetido_para_pasta_propria(tmp_path):
    _criar_arquivo(tmp_path, "a.txt", conteudo="mesmo conteudo")
    _criar_arquivo(tmp_path, "b.txt", conteudo="mesmo conteudo")
    _criar_arquivo(tmp_path, "c.txt", conteudo="conteudo diferente")

    stats = organizar_arquivos(str(tmp_path), detectar_duplicados=True)

    assert stats["duplicados"] == 1
    assert stats["movidos"] == 2
    duplicados = os.listdir(tmp_path / "duplicados")
    assert len(duplicados) == 1 and duplicados[0] in {"a.txt", "b.txt"}
    restante = duplicados[0]
    assert set(os.listdir(tmp_path / "txt")) == {"a.txt", "b.txt", "c.txt"} - {restante}


def test_sem_detectar_duplicados_nao_ha_pasta_duplicados(tmp_path):
    _criar_arquivo(tmp_path, "a.txt", conteudo="mesmo conteudo")
    _criar_arquivo(tmp_path, "b.txt", conteudo="mesmo conteudo")

    stats = organizar_arquivos(str(tmp_path))

    assert stats["duplicados"] == 0
    assert not os.path.exists(tmp_path / "duplicados")
    assert set(os.listdir(tmp_path / "txt")) == {"a.txt", "b.txt"}


def test_stats_movimentos_lista_origem_e_destino_reais(tmp_path):
    _criar_arquivo(tmp_path, "foto.jpg")

    stats = organizar_arquivos(str(tmp_path))

    assert len(stats["movimentos"]) == 1
    movimento = stats["movimentos"][0]
    assert movimento["origem"] == str(tmp_path / "foto.jpg")
    assert movimento["destino"] == str(tmp_path / "jpg" / "foto.jpg")


def test_stats_movimentos_vazio_em_modo_simular(tmp_path):
    _criar_arquivo(tmp_path, "foto.jpg")

    stats = organizar_arquivos(str(tmp_path), simular=True)

    assert stats["movimentos"] == []


def carregar_regras_de_lista(lista):
    import re

    return [(re.compile(item["padrao"]), item["categoria"]) for item in lista]
