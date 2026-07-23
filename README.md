# Organizador de Arquivos com Interface Gráfica (Python/Tkinter)

Este projeto consiste em um script Python que implementa um organizador de arquivos simples com uma interface gráfica (GUI) construída usando a biblioteca `tkinter`. O objetivo é ajudar a organizar arquivos dentro de um diretório selecionado, movendo-os automaticamente para subpastas baseadas na extensão de cada arquivo.

## Descrição

O script permite que o usuário selecione um diretório através de uma caixa de diálogo gráfica e, opcionalmente, informe um ano mínimo de modificação. A organização é feita criando dinamicamente subpastas com o nome da extensão de cada arquivo e movendo os arquivos correspondentes para essas pastas, resultando em um diretório mais limpo e organizado, agrupado por tipo.

## Estrutura do Projeto

O código é dividido em dois módulos para separar a lógica de negócio da interface gráfica (o que permite testar a lógica sem precisar abrir uma janela):

-   **`organizer_core.py`**: contém a função `organizar_arquivos(diretorio, ano_minimo=None)`, responsável por toda a lógica de organização de arquivos. Não depende de `tkinter` e é totalmente testável.
-   **`organizer.py`**: monta a interface gráfica (Tkinter) e chama `organizer_core.organizar_arquivos` quando o usuário clica em "Selecionar". É o ponto de entrada da aplicação.
-   **`tests/test_organizer_core.py`**: testes automatizados (`pytest`) cobrindo a lógica de organização.

## Bibliotecas Utilizadas

Todas as bibliotecas usadas fazem parte da biblioteca padrão do Python — não há dependências externas para rodar o organizador:

-   **`os`**: interação com o sistema de arquivos (`os.listdir`, `os.path.isfile`, `os.makedirs`, `os.path.join`, `os.replace`, etc.).
-   **`datetime`**: usado para obter o ano da última modificação de um arquivo, quando o filtro por ano é utilizado.
-   **`tkinter`**: biblioteca padrão para GUIs. Fornece `Tk`, `Canvas`, `Entry`, `Button`, `filedialog` e `messagebox`, usados na interface.

Para rodar os testes automatizados é necessário o `pytest` (veja `requirements-dev.txt`).

## Funcionalidades

1.  **Seleção de Diretório**: um botão abre uma caixa de diálogo nativa do sistema operacional para escolher a pasta a ser organizada.
2.  **Organização por Extensão**: cada arquivo é movido para uma subpasta nomeada com sua extensão (em minúsculas). Arquivos sem extensão (ou arquivos ocultos como `.env`) vão para uma pasta `sem_extensao`.
3.  **Criação Dinâmica de Pastas**: as subpastas de destino são criadas automaticamente conforme necessário.
4.  **Filtro por Ano (opcional)**: se um ano for informado no campo de entrada, arquivos cuja última modificação seja anterior a esse ano são ignorados (não são movidos, nem excluídos). Deixar o campo em branco organiza todos os arquivos, sem filtro.
5.  **Proteção contra sobrescrita**: se já existir um arquivo com o mesmo nome na pasta de destino, o arquivo movido é renomeado automaticamente (ex: `notas_1.txt`) em vez de sobrescrever o arquivo existente.
6.  **Feedback ao Usuário**: ao final, uma caixa de mensagem informa quantos arquivos foram organizados, quantos foram ignorados pelo filtro de ano e eventuais erros ocorridos (ex: permissão negada).

## Como Executar o Script

1.  **Requisitos**: tenha o Python 3 instalado. As bibliotecas `os`, `datetime` e `tkinter` já vêm com o Python (em algumas distribuições Linux, `tkinter` precisa ser instalado separadamente via gerenciador de pacotes do sistema, ex: `sudo apt install python3-tk`).
2.  **Executar pelo Terminal**: navegue até o diretório do projeto e rode:
    ```bash
    python3 organizer.py
    ```
3.  **Executar em uma IDE**: abra `organizer.py` e utilize a função de "Executar" da IDE.

## Como Rodar os Testes

Os testes cobrem a lógica de `organizer_core.py` (não abrem nenhuma janela gráfica, então funcionam em ambientes headless como CI):

```bash
pip install -r requirements-dev.txt
pytest -v
```

Os testes também rodam automaticamente via GitHub Actions a cada `push`/`pull request` (veja `.github/workflows/test.yml`).

## Licença

Projeto sob licença GNU GPL v3 (veja o arquivo `LICENSE`).
