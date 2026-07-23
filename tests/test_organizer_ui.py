import os
from unittest.mock import patch

import pytest

tk = pytest.importorskip("tkinter")

import organizer_config  # noqa: E402
import organizer_history  # noqa: E402
from organizer import OrganizadorApp  # noqa: E402


def _criar_arquivo(diretorio, nome, conteudo="conteudo"):
    caminho = os.path.join(diretorio, nome)
    with open(caminho, "w") as arquivo:
        arquivo.write(conteudo)
    return caminho


@pytest.fixture(scope="session")
def tk_root():
    # Um unico Tk() por sessao: criar/destruir varias raizes Tk no mesmo
    # processo quebra o Tcl em alguns SOs (ex: Windows), entao cada teste
    # usa uma Toplevel nova sobre esta mesma raiz em vez de um Tk() novo.
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def app(tmp_path, monkeypatch, tk_root):
    # Isola config/historico apontando as funcoes "caminho padrao" para
    # dentro de tmp_path, em vez de depender da variavel de ambiente HOME:
    # no Windows, os.path.expanduser("~") usa USERPROFILE (nao HOME), entao
    # monkeypatch.setenv("HOME", ...) nao isola nada la e os testes vazam
    # estado real entre si via ~/.organizador_arquivos.
    monkeypatch.setattr(
        organizer_config,
        "caminho_config_padrao",
        lambda: str(tmp_path / "config.json"),
    )
    monkeypatch.setattr(
        organizer_history,
        "caminho_historico_padrao",
        lambda: str(tmp_path / "historico.json"),
    )
    monkeypatch.setattr(
        organizer_config,
        "caminho_perfis_padrao",
        lambda: str(tmp_path / "perfis.json"),
    )
    window = tk.Toplevel(tk_root)
    aplicativo = OrganizadorApp(window)
    window.update()
    yield aplicativo
    window.destroy()


def test_janela_constroi_com_widgets_esperados(app):
    assert app.label_diretorio.cget("text") == "Nenhuma pasta selecionada ainda"
    assert app.botao_organizar.cget("text") == "Selecionar pasta e organizar"
    assert app.progress["value"] == 0


def test_organizar_atualiza_progresso_e_resultado(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")
    _criar_arquivo(pasta, "relatorio.pdf")

    with (
        patch("organizer.filedialog") as mock_fd,
        patch("organizer.messagebox") as mock_msgbox,
    ):
        mock_fd.askdirectory.return_value = str(pasta)
        app._selecionar_e_organizar()

    assert app.progress["value"] == 2
    assert app.progress["maximum"] == 2
    resultado = app.texto_resultado.get("1.0", "end")
    assert "foto.jpg" in resultado
    assert "relatorio.pdf" in resultado
    assert mock_msgbox.showinfo.called
    assert sorted(os.listdir(pasta)) == ["jpg", "pdf"]


def test_simular_nao_move_arquivos(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_simular.set(True)
        app._selecionar_e_organizar()

    assert os.listdir(pasta) == ["foto.jpg"]


def test_ano_invalido_mostra_erro(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with (
        patch("organizer.filedialog") as mock_fd,
        patch("organizer.messagebox") as mock_msgbox,
    ):
        mock_fd.askdirectory.return_value = str(pasta)
        app.entry_ano.delete(0, "end")
        app.entry_ano.insert(0, "nao-e-um-ano")
        app._selecionar_e_organizar()

    assert mock_msgbox.showerror.called
    assert os.listdir(pasta) == ["foto.jpg"]


def test_botao_desfazer_comeca_desabilitado(app):
    assert str(app.botao_desfazer.cget("state")) == "disabled"


def test_desfazer_reverte_ultima_organizacao(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app._selecionar_e_organizar()

    assert str(app.botao_desfazer.cget("state")) == "normal"
    assert os.listdir(pasta) == ["jpg"]

    with patch("organizer.messagebox") as mock_msgbox:
        app._desfazer_ultima_organizacao()

    assert os.path.exists(pasta / "foto.jpg")
    assert mock_msgbox.showinfo.called
    assert str(app.botao_desfazer.cget("state")) == "disabled"


def test_detectar_duplicados_move_para_pasta_duplicados(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "a.txt", conteudo="repetido")
    _criar_arquivo(pasta, "b.txt", conteudo="repetido")

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_duplicados.set(True)
        app._selecionar_e_organizar()

    assert os.path.isdir(pasta / "duplicados")
    assert len(os.listdir(pasta / "duplicados")) == 1


def test_regras_personalizadas_tem_prioridade(app, tmp_path, monkeypatch):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "fatura_junho.pdf")

    caminho_regras = tmp_path / "regras.json"
    caminho_regras.write_text('[{"padrao": "(?i)fatura", "categoria": "financeiro"}]')
    monkeypatch.setattr("organizer.CAMINHO_REGRAS", str(caminho_regras))

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_regras.set(True)
        app._selecionar_e_organizar()

    assert os.listdir(pasta / "financeiro") == ["fatura_junho.pdf"]


def test_iniciar_monitoramento_organiza_na_hora_e_agenda_proximo_ciclo(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_monitorar.set(True)
        app._selecionar_e_organizar()

    assert app.monitorando is True
    assert app._id_agendamento_monitoramento is not None
    assert app.botao_organizar.cget("text") == "Parar monitoramento"
    assert os.listdir(pasta) == ["jpg"]

    app._parar_monitoramento()


def test_clicar_botao_durante_monitoramento_para_sem_reabrir_dialogo(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_monitorar.set(True)
        app._selecionar_e_organizar()

        mock_fd.reset_mock()
        app._selecionar_e_organizar()

        assert not mock_fd.askdirectory.called

    assert app.monitorando is False
    assert app._id_agendamento_monitoramento is None
    assert app.botao_organizar.cget("text") == "Selecionar pasta e organizar"


def test_desmarcar_checkbox_monitorar_para_monitoramento_ativo(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_monitorar.set(True)
        app._selecionar_e_organizar()

    app.var_monitorar.set(False)
    app._ao_alternar_checkbox_monitorar()

    assert app.monitorando is False
    assert app._id_agendamento_monitoramento is None


def test_ciclo_de_monitoramento_silencioso_nao_abre_messagebox(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with (
        patch("organizer.filedialog") as mock_fd,
        patch("organizer.messagebox") as mock_msgbox,
    ):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_monitorar.set(True)
        app._selecionar_e_organizar()

        assert not mock_msgbox.showinfo.called
        assert not mock_msgbox.showwarning.called
        assert not mock_msgbox.showerror.called

    app._parar_monitoramento()


def test_idioma_padrao_e_portugues(app):
    assert app.idioma == "pt"
    assert app.botao_organizar.cget("text") == "Selecionar pasta e organizar"


def test_trocar_idioma_atualiza_textos_estaticos(app):
    app._trocar_idioma("en")

    assert app.rotulo_titulo.cget("text") == "File Organizer"
    assert app.botao_organizar.cget("text") == "Select folder and organize"
    assert app.botao_desfazer.cget("text") == "Undo last organization"
    assert app.check_simular.cget("text").startswith("Simulate")
    assert app.label_diretorio.cget("text") == "No folder selected yet"


def test_trocar_idioma_preserva_pasta_ja_selecionada(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app._selecionar_e_organizar()

    app._trocar_idioma("es")

    assert app.label_diretorio.cget("text") == str(pasta)


def test_trocar_idioma_preserva_texto_do_botao_durante_monitoramento(app, tmp_path):
    pasta = tmp_path / "arquivos"
    pasta.mkdir()
    _criar_arquivo(pasta, "foto.jpg")

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox"):
        mock_fd.askdirectory.return_value = str(pasta)
        app.var_monitorar.set(True)
        app._selecionar_e_organizar()

    app._trocar_idioma("en")

    assert app.botao_organizar.cget("text") == "Stop monitoring"
    app._parar_monitoramento()


def test_trocar_idioma_persiste_escolha_no_config(app, tmp_path):
    app._trocar_idioma("es")

    from organizer_config import carregar_config

    assert carregar_config(str(tmp_path / "config.json"))["idioma"] == "es"


def test_salvar_perfil_sem_nome_mostra_aviso(app):
    app.combo_perfil.set("")

    with patch("organizer.messagebox") as mock_msgbox:
        app._salvar_perfil_atual()

        assert mock_msgbox.showwarning.called


def test_salvar_perfil_persiste_e_atualiza_combobox(app, tmp_path):
    app.var_simular.set(True)
    app.entry_ano.insert(0, "2021")
    app.combo_perfil.set("trabalho")

    with patch("organizer.messagebox"):
        app._salvar_perfil_atual()

    from organizer_config import carregar_perfil

    perfil = carregar_perfil("trabalho", str(tmp_path / "perfis.json"))
    assert perfil is not None
    assert perfil["simular"] is True
    assert perfil["ano_minimo"] == "2021"
    assert "trabalho" in app.combo_perfil.cget("values")


def test_selecionar_perfil_aplica_configuracoes_salvas(app, tmp_path):
    pasta = tmp_path / "fotos"
    pasta.mkdir()
    app.var_duplicados.set(True)
    app.entry_ano.insert(0, "2018")
    app.ultimo_diretorio = str(pasta)
    app.combo_perfil.set("fotos_perfil")
    with patch("organizer.messagebox"):
        app._salvar_perfil_atual()

    # Reseta o estado da UI antes de recarregar o perfil, para garantir
    # que os valores vieram mesmo do perfil salvo.
    app.var_duplicados.set(False)
    app.entry_ano.delete(0, "end")
    app.label_diretorio.configure(text="")

    app.combo_perfil.set("fotos_perfil")
    app._carregar_perfil_selecionado()

    assert app.var_duplicados.get() is True
    assert app.entry_ano.get() == "2018"
    assert app.label_diretorio.cget("text") == str(pasta)


def test_excluir_perfil_inexistente_mostra_aviso(app):
    app.combo_perfil.set("nao_existe")

    with patch("organizer.messagebox") as mock_msgbox:
        app._excluir_perfil_atual()

        assert mock_msgbox.showinfo.called


def test_excluir_perfil_existente_remove_da_lista(app, tmp_path):
    app.combo_perfil.set("temporario")
    with patch("organizer.messagebox"):
        app._salvar_perfil_atual()
        assert "temporario" in app.combo_perfil.cget("values")

        app._excluir_perfil_atual()

    from organizer_config import carregar_perfil

    assert carregar_perfil("temporario", str(tmp_path / "perfis.json")) is None
    assert "temporario" not in app.combo_perfil.cget("values")
