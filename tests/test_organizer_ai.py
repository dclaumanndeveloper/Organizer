import json
import urllib.error
from unittest.mock import MagicMock, patch

from organizer_ai import classificar_arquivo, ollama_disponivel


def test_ollama_indisponivel_quando_conexao_falha():
    with patch(
        "organizer_ai.urllib.request.urlopen",
        side_effect=urllib.error.URLError("recusado"),
    ):
        assert ollama_disponivel(host="http://localhost:1", timeout=1) is False


def test_ollama_disponivel_quando_responde():
    with patch("organizer_ai.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = MagicMock()
        assert ollama_disponivel() is True


def test_classificar_arquivo_retorna_none_sem_categorias():
    assert classificar_arquivo("a.txt", "/tmp/a.txt", "txt", []) is None


def test_classificar_arquivo_retorna_none_quando_ollama_falha():
    with patch(
        "organizer_ai.urllib.request.urlopen",
        side_effect=urllib.error.URLError("recusado"),
    ):
        resultado = classificar_arquivo(
            "fatura.pdf", "/tmp/fatura.pdf", "pdf", ["financeiro", "outros"]
        )
    assert resultado is None


def test_classificar_arquivo_retorna_categoria_valida(tmp_path):
    caminho = tmp_path / "fatura.pdf"
    caminho.write_text("conteudo")

    resposta_mock = MagicMock()
    resposta_mock.read.return_value = json.dumps({"response": "Financeiro"}).encode(
        "utf-8"
    )
    resposta_mock.__enter__.return_value = resposta_mock

    with patch("organizer_ai.urllib.request.urlopen", return_value=resposta_mock):
        resultado = classificar_arquivo(
            "fatura.pdf", str(caminho), "pdf", ["financeiro", "outros"]
        )

    assert resultado == "financeiro"


def test_classificar_arquivo_retorna_none_para_resposta_desconhecida(tmp_path):
    caminho = tmp_path / "fatura.pdf"
    caminho.write_text("conteudo")

    resposta_mock = MagicMock()
    resposta_mock.read.return_value = json.dumps({"response": "sei la"}).encode("utf-8")
    resposta_mock.__enter__.return_value = resposta_mock

    with patch("organizer_ai.urllib.request.urlopen", return_value=resposta_mock):
        resultado = classificar_arquivo(
            "fatura.pdf", str(caminho), "pdf", ["financeiro", "outros"]
        )

    assert resultado is None


def test_classificar_arquivo_inclui_trecho_de_texto(tmp_path):
    caminho = tmp_path / "notas.txt"
    caminho.write_text("reuniao de projeto amanha")

    resposta_mock = MagicMock()
    resposta_mock.read.return_value = json.dumps({"response": "trabalho"}).encode(
        "utf-8"
    )
    resposta_mock.__enter__.return_value = resposta_mock

    prompts_enviados = []

    def fake_urlopen(requisicao, timeout=None):
        prompts_enviados.append(json.loads(requisicao.data.decode("utf-8"))["prompt"])
        return resposta_mock

    with patch("organizer_ai.urllib.request.urlopen", side_effect=fake_urlopen):
        classificar_arquivo("notas.txt", str(caminho), "txt", ["trabalho", "pessoal"])

    assert "reuniao de projeto amanha" in prompts_enviados[0]
