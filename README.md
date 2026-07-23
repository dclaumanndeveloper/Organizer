# Organizador de Arquivos com Interface Gráfica (Python/Tkinter)

Este projeto consiste em um script Python que implementa um organizador de arquivos com uma interface gráfica (GUI) construída usando a biblioteca `tkinter`. O objetivo é ajudar a organizar arquivos dentro de um diretório selecionado, movendo-os automaticamente para subpastas por extensão, por categoria, ou por sugestão de uma IA local (Ollama).

## Descrição

O script permite que o usuário selecione um diretório através de uma caixa de diálogo gráfica e, opcionalmente, informe um ano mínimo de modificação. A organização é feita criando dinamicamente subpastas e movendo os arquivos correspondentes para elas, resultando em um diretório mais limpo e organizado. Um modo de simulação permite ver o que aconteceria antes de mover qualquer arquivo de verdade.

## Estrutura do Projeto

O código é dividido em módulos para separar a lógica de negócio da interface gráfica (o que permite testar a lógica sem precisar abrir uma janela) e para manter a integração opcional com IA isolada do restante:

-   **`organizer_core.py`**: contém a função `organizar_arquivos(...)`, responsável por toda a lógica de organização de arquivos (extensão, categorias, filtro por ano, simulação). Não depende de `tkinter` nem de rede, e é totalmente testável.
-   **`organizer_ai.py`**: integração opcional com um servidor [Ollama](https://ollama.com) local, usada para sugerir a categoria de um arquivo a partir do nome (e de um trecho do conteúdo, para arquivos de texto). Não é importado por `organizer_core.py` — é passado a ele como uma função de callback (`classificador_categoria`), então o núcleo da aplicação não sabe nada sobre Ollama.
-   **`organizer.py`**: monta a interface gráfica (Tkinter), lê as opções escolhidas pelo usuário e chama `organizer_core.organizar_arquivos`. É o ponto de entrada da aplicação.
-   **`organizer_config.py`**: carrega/salva o último perfil de uso (pasta, ano, checkboxes) em `~/.organizador_arquivos/config.json`, para que a interface abra já preenchida com as últimas opções usadas.
-   **`organizer_history.py`**: registra cada organização (lista de origem/destino de cada arquivo movido) em `~/.organizador_arquivos/historico.json` e sabe desfazer a última execução, movendo os arquivos de volta. Assim como `organizer_ai.py`, não é acoplado ao núcleo — `organizer_core.organizar_arquivos` apenas devolve a lista de movimentos em `stats["movimentos"]`.
-   **`organizer_i18n.py`**: dicionário de traduções (Português, English, Español) e a função `t(idioma, chave, **kwargs)` usada por toda a interface. Nenhuma lógica de UI aqui — só texto.
-   **`categorias.json`**: mapa de categorias (`{"categoria": ["ext1", "ext2", ...]}`) usado quando o agrupamento por categoria está ativado. Editável pelo usuário para customizar as categorias.
-   **`regras.json`**: lista de regras de categorização por nome de arquivo (regex), usada quando "Usar regras personalizadas" está ativado. Vazia (`[]`) por padrão — editável pelo usuário.
-   **`tests/`**: testes automatizados (`pytest`) cobrindo `organizer_core.py`, `organizer_config.py`, `organizer_history.py`, `organizer_i18n.py` e `organizer_ai.py` (este último com o Ollama mockado, sem precisar de um servidor real rodando), além da UI (`organizer.py`) em `tests/test_organizer_ui.py`.

## Bibliotecas Utilizadas

Rodar o organizador não requer nenhuma dependência externa — tudo usa a biblioteca padrão do Python:

-   **`os`**: interação com o sistema de arquivos.
-   **`datetime`**: obter o ano da última modificação de um arquivo (filtro por ano).
-   **`json`**: carregar o mapa de categorias (`categorias.json`).
-   **`urllib.request`**: fazer as chamadas HTTP ao servidor Ollama local (sem precisar de bibliotecas como `requests`).
-   **`tkinter`**: biblioteca padrão para GUIs.

Para rodar os testes automatizados ou empacotar a aplicação como executável é necessário instalar as dependências de desenvolvimento (veja `requirements-dev.txt`).

## Funcionalidades

1.  **Seleção de Diretório**: um botão abre uma caixa de diálogo nativa do sistema operacional para escolher a pasta a ser organizada.
2.  **Organização por Extensão** (padrão): cada arquivo é movido para uma subpasta nomeada com sua extensão (em minúsculas). Arquivos sem extensão (ou ocultos, como `.env`) vão para uma pasta `sem_extensao`.
3.  **Organização por Categoria** (opcional): ao marcar "Agrupar por categoria", arquivos são agrupados em pastas temáticas (`imagens`, `documentos`, `planilhas`, `apresentacoes`, `audio`, `video`, `compactados`, ...) definidas em `categorias.json`, em vez de uma pasta por extensão.
4.  **Classificação por IA local (Ollama)** (opcional): ao marcar "Usar IA local (Ollama)", cada arquivo é enviado (nome + um trecho do conteúdo, para arquivos de texto) a um modelo rodando localmente via [Ollama](https://ollama.com), que sugere a categoria mais adequada dentre as definidas em `categorias.json`. Se o Ollama não estiver disponível em `localhost:11434`, ou a resposta do modelo não for reconhecida, a aplicação avisa o usuário e cai automaticamente de volta para a classificação por categoria/extensão — a IA nunca é obrigatória nem bloqueia o uso do programa.
5.  **Modo de Simulação** (opcional): ao marcar "Simular", a aplicação mostra exatamente o que aconteceria (quais arquivos seriam movidos e para onde) sem mover nenhum arquivo nem criar nenhuma pasta. Útil para revisar antes de organizar de verdade.
6.  **Criação Dinâmica de Pastas**: as subpastas de destino são criadas automaticamente conforme necessário (exceto em modo de simulação).
7.  **Filtro por Ano (opcional)**: se um ano for informado no campo de entrada, arquivos cuja última modificação seja anterior a esse ano são ignorados (não são movidos, nem excluídos).
8.  **Proteção contra sobrescrita**: se já existir um arquivo com o mesmo nome na pasta de destino, o arquivo movido é renomeado automaticamente (ex: `notas_1.txt`) em vez de sobrescrever o arquivo existente.
9.  **Progresso em tempo real**: uma barra de progresso e um log mostram cada arquivo conforme é processado (`[2/5] foto.png - movido para imagens/`), além do resumo final.
10. **Organização Recursiva** (opcional): ao marcar "Organizar subpastas também", cada subpasta encontrada também é organizada, ganhando suas próprias pastas de destino dentro dela mesma (os arquivos não são movidos para fora de onde estão, só agrupados no lugar). Pastas cujo nome já é uma categoria/extensão conhecida (ex: `imagens`, `sem_extensao`, `duplicados`) não são percorridas novamente, para evitar reprocessar pastas de destino criadas em execuções anteriores.
11. **Perfil Salvo**: a última pasta selecionada, o ano informado e todas as opções marcadas são lembradas entre uma execução e outra, em `~/.organizador_arquivos/config.json`.
12. **Desfazer Última Organização**: um botão "Desfazer última organização" reverte todos os arquivos movidos na última execução para o local original. Fica desabilitado quando não há nada para desfazer, e continua funcionando mesmo depois de fechar e reabrir o programa (o histórico fica salvo em `~/.organizador_arquivos/historico.json`). Se um arquivo revertido já não existir mais no destino, ou já existir um arquivo com esse nome na origem, o desfazer pula esse arquivo e avisa, sem apagar nada.
13. **Detecção de Duplicados** (opcional): ao marcar "Detectar arquivos duplicados", cada arquivo tem seu hash (SHA-256) calculado; se o conteúdo já foi visto nesta mesma execução, o arquivo vai para uma pasta `duplicados` em vez de sua categoria normal. Arquivos duplicados nunca são apagados, só isolados para revisão manual.
14. **Regras Personalizadas por Nome** (opcional): ao marcar "Usar regras personalizadas", cada arquivo é testado contra os padrões (regex) definidos em `regras.json`; o primeiro padrão que der match define a categoria do arquivo, com prioridade sobre a categoria por extensão e sobre a sugestão da IA.
15. **Monitoramento Contínuo** (opcional): ao marcar "Monitorar a pasta continuamente" e clicar no botão, a pasta escolhida é organizada imediatamente e depois, a cada 30 segundos, o organizador roda de novo automaticamente nela (com as mesmas opções), pegando arquivos novos sem precisar clicar de novo. Nenhuma caixa de mensagem aparece durante os ciclos automáticos (só o log é atualizado), para não interromper o uso do computador repetidamente. O botão vira "Parar monitoramento" enquanto ativo; clicar nele de novo (ou desmarcar a caixa) interrompe.
16. **Interface em Português, English ou Español**: um seletor de idioma no topo da janela troca todos os textos da interface na hora (título, botões, checkboxes, mensagens de resultado), sem precisar reiniciar o programa. A escolha é lembrada entre execuções, em `~/.organizador_arquivos/config.json`. Português é o idioma padrão.

## Como Executar o Script

1.  **Requisitos**: tenha o Python 3 instalado. `tkinter` já vem com o Python na maioria das instalações (em algumas distribuições Linux precisa ser instalado separadamente, ex: `sudo apt install python3-tk`).
2.  **Executar pelo Terminal**: navegue até o diretório do projeto e rode:
    ```bash
    python3 organizer.py
    ```
3.  **Executar em uma IDE**: abra `organizer.py` e utilize a função de "Executar" da IDE.

### Usando a classificação por IA (opcional)

A classificação por IA é totalmente opcional e roda localmente — nenhum arquivo é enviado para a nuvem:

1.  Instale o [Ollama](https://ollama.com/download) e baixe um modelo (ex: `ollama pull llama3.2`).
2.  Certifique-se de que o servidor está rodando (`ollama serve`, geralmente já roda como serviço após a instalação) e acessível em `http://localhost:11434`.
3.  Na interface do organizador, marque "Usar IA local (Ollama) para sugerir a categoria de cada arquivo".

Se o Ollama não estiver rodando, o organizador simplesmente avisa e usa a classificação por categoria/extensão normalmente.

## Personalizando as Categorias

Edite o arquivo `categorias.json` para adicionar, remover ou renomear categorias:

```json
{
  "imagens": ["jpg", "jpeg", "png", "gif"],
  "documentos": ["pdf", "doc", "docx"],
  "financeiro": ["ofx", "xlsx"]
}
```

Essas categorias são usadas tanto pelo agrupamento manual quanto como opções que a IA pode escolher.

## Regras Personalizadas por Nome

Edite o arquivo `regras.json` para definir categorias com base no nome do arquivo, não só na extensão:

```json
[
  {"padrao": "(?i)fatura|boleto|nota_fiscal", "categoria": "financeiro"},
  {"padrao": "(?i)contrato", "categoria": "juridico"}
]
```

Cada `padrao` é uma expressão regular (case-insensitive com `(?i)`) testada contra o nome do arquivo; a primeira que der match define a categoria. Regras têm prioridade sobre a IA e sobre `categorias.json`.

## Empacotando como Executável (PyInstaller)

Para distribuir o organizador sem exigir que o usuário final tenha Python instalado:

```bash
pip install -r requirements-dev.txt
pyinstaller --onefile --windowed --name organizador organizer.py
```

O executável gerado fica em `dist/organizador` (ou `dist/organizador.exe` no Windows). No macOS, use `pyinstaller --windowed --name organizador organizer.py` (sem `--onefile`) para gerar um bundle `.app` de verdade em `dist/organizador.app`, em vez de um binário solto. As pastas `build/`, `dist/` e o arquivo `*.spec` gerados pelo PyInstaller já estão no `.gitignore` e não devem ser commitados.

### Releases automatizados

Em vez de gerar o executável manualmente, o workflow `.github/workflows/release.yml` builda e publica automaticamente os artefatos das três plataformas sempre que uma tag no formato `vX.Y.Z` é enviada ao repositório (ou é disparado manualmente pela aba Actions, usando o input `versao_teste` como nome da tag):

```bash
git tag v1.0.0
git push origin v1.0.0
```

Isso dispara uma matrix de build (rodando os testes antes de empacotar, em cada plataforma) e cria uma *release* em modo rascunho no GitHub com os artefatos anexados:

- `organizador-linux`: executável único (`--onefile`).
- `organizador-windows.exe`: executável único (`--onefile`).
- `organizador-macos.zip`: bundle `.app` de verdade (gerado sem `--onefile`, para que o Finder o reconheça como um aplicativo), compactado com `ditto` (preserva metadados do macOS melhor que `zip`).

A release fica em rascunho, pronta para revisão e publicação manual.

**Nota sobre assinatura de código**: nenhum dos artefatos é assinado digitalmente (não há certificado de desenvolvedor configurado). Isso significa que o Windows Defender SmartScreen e o Gatekeeper do macOS provavelmente vão avisar que o app é de "desenvolvedor desconhecido" no primeiro uso — no macOS, é necessário clicar com o botão direito no `.app` e escolher "Abrir" (em vez de dar duplo-clique) para contornar isso. Instaladores nativos completos (NSIS/Inno Setup no Windows, `.deb`/AppImage no Linux) e assinatura de código ainda não foram implementados — ficam como possíveis melhorias futuras.

## Como Rodar os Testes

A suíte cobre `organizer_core.py`, `organizer_config.py`, `organizer_ai.py` (com o Ollama mockado) e também `organizer.py` (a UI Tkinter, em `tests/test_organizer_ui.py`), simulando cliques e verificando o estado da janela:

```bash
pip install -r requirements-dev.txt
pytest -v
```

Os testes de UI usam `pytest.importorskip("tkinter")` — se o `tkinter` não estiver instalado no ambiente, eles são pulados automaticamente em vez de falhar, então `pytest -v` funciona tanto em máquinas sem `tkinter` quanto em CI.

Os testes também rodam automaticamente via GitHub Actions a cada `push`/`pull request`, em Linux, Windows e macOS (matrix de CI em `.github/workflows/test.yml`) — já que esta é uma aplicação desktop distribuída para as três plataformas. No job Linux, o CI instala `xvfb` e `python3-tk` e roda a suíte com `xvfb-run` (display virtual), garantindo que os testes de UI também rodem de verdade lá, não só sejam pulados.

## Qualidade de Código (lint, formatação e tipos)

O projeto usa [`ruff`](https://docs.astral.sh/ruff/) (lint), [`black`](https://black.readthedocs.io/) (formatação) e [`mypy`](https://mypy-lang.org/) (checagem estática de tipos), configurados em `pyproject.toml`. Um job `lint` separado no CI (`.github/workflows/test.yml`) roda os três a cada `push`/`pull request`. `mypy` checa todos os módulos `organizer_*.py`/`organizer.py` (não os testes, que usam mocks extensivamente e gerariam ruído).

Para rodar localmente antes de commitar:

```bash
pip install -r requirements-dev.txt
ruff check .
black --check .   # ou "black ." para formatar automaticamente
mypy .
```

## Licença

Projeto sob licença GNU GPL v3 (veja o arquivo `LICENSE`).
