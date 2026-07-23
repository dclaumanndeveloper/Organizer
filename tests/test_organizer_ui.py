import os
from unittest.mock import MagicMock, patch

import pytest

tk = pytest.importorskip("tkinter")

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
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    os.makedirs(tmp_path / "home", exist_ok=True)
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

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox") as mock_msgbox:
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

    with patch("organizer.filedialog") as mock_fd, patch("organizer.messagebox") as mock_msgbox:
        mock_fd.askdirectory.return_value = str(pasta)
        app.entry_ano.delete(0, "end")
        app.entry_ano.insert(0, "nao-e-um-ano")
        app._selecionar_e_organizar()

    assert mock_msgbox.showerror.called
    assert os.listdir(pasta) == ["foto.jpg"]
