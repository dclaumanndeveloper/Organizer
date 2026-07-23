from organizer_i18n import IDIOMAS_DISPONIVEIS, t


def test_traducao_pt_padrao():
    assert t("pt", "botao_organizar") == "Selecionar pasta e organizar"


def test_traducao_ingles():
    assert t("en", "botao_organizar") == "Select folder and organize"


def test_traducao_espanhol():
    assert t("es", "botao_organizar") == "Seleccionar carpeta y organizar"


def test_traducao_com_interpolacao():
    texto = t("en", "resumo_organizados", n=3, verbo="moved")
    assert texto == "3 file(s) moved."


def test_chave_desconhecida_devolve_a_propria_chave():
    assert t("pt", "chave_que_nao_existe") == "chave_que_nao_existe"


def test_idioma_desconhecido_cai_para_padrao():
    assert t("fr", "botao_organizar") == "Selecionar pasta e organizar"


def test_todas_as_chaves_tem_as_tres_traducoes():
    from organizer_i18n import _TEXTOS

    idiomas_esperados = set(IDIOMAS_DISPONIVEIS.keys())
    for chave, traducoes in _TEXTOS.items():
        assert set(traducoes.keys()) == idiomas_esperados, chave
        for idioma, texto in traducoes.items():
            assert texto.strip(), f"{chave}/{idioma} esta vazio"
