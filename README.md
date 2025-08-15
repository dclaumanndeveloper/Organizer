# Organizador de Arquivos com Interface Gráfica (Python/Tkinter)

Este projeto consiste em um script Python que implementa um organizador de arquivos simples com uma interface gráfica (GUI) construída usando a biblioteca `tkinter`. O objetivo é ajudar a organizar arquivos dentro de um diretório selecionado, movendo-os automaticamente para subpastas baseadas na extensão de cada arquivo.

## Descrição

O script permite que o usuário selecione um diretório através de uma caixa de diálogo gráfica. Uma vez selecionado, o script processa os arquivos dentro deste diretório (atualmente, sem filtro por ano implementado ativamente). A organização é realizada criando dinamicamente subpastas com o nome da extensão de cada arquivo e movendo os arquivos correspondentes para essas pastas. Isso resulta em um diretório mais limpo e organizado, agrupando arquivos por tipo.

## Bibliotecas Utilizadas

-   **`os`**: Essencial para interagir com o sistema de arquivos do sistema operacional. Utilizado para listar arquivos (`os.listdir`), verificar a existência de diretórios (`os.path.exists`), criar diretórios (`os.mkdir`), mudar o diretório de trabalho (`os.chdir`), obter o diretório de trabalho atual (`os.getcwd`), unir caminhos de arquivo e diretório (`os.path.join`), e mover/renomear arquivos (`os.replace`).
-   **`time`**: Usado para funcionalidades relacionadas a tempo. (Atualmente, o uso direto via `os.path.getmtime` está comentado no código).
-   **`datetime`**: Usado para manipular objetos de data e hora, particularmente para formatar timestamps (`datetime.fromtimestamp`, `strftime`). (Atualmente, o uso para filtragem por ano está comentado).
-   **`tkinter`**: A biblioteca padrão do Python para criar interfaces gráficas. Fornece os widgets necessários para a janela principal, áreas de desenho, campos de entrada, botões, caixas de diálogo de seleção de arquivo/diretório e caixas de mensagem.
    -   `Tk`: A classe principal para a janela da aplicação.
    -   `Canvas`: Usado para desenhar formas e textos na janela.
    -   `Entry`: Campo de texto onde o usuário pode inserir informações (como o ano para filtro).
    -   `Button`: Elementos clicáveis para executar ações.
    -   `PhotoImage`: Usado para lidar com imagens. (Atualmente, o uso para botões está comentado).
    -   `filedialog`: Módulo para abrir caixas de diálogo padrão do sistema para seleção de arquivos e diretórios.
    -   `messagebox`: Módulo para exibir caixas de mensagem (informação, aviso, erro).
    -   `ttk.Label`: Widget para exibir texto ou imagens. (Atualmente não utilizado explicitamente, mas pode ser usado em uma versão com `ttk`).
    -   `ttk.OptionMenu`: Widget para criar um menu drop-down. (Atualmente não utilizado).

## Funcionalidades

1.  **Seleção de Diretório**: A interface gráfica inclui um botão que, quando clicado, abre uma caixa de diálogo nativa do sistema operacional, permitindo ao usuário navegar e selecionar a pasta que deseja organizar.
2.  **Organização por Extensão**: A lógica principal do script itera sobre todos os arquivos no diretório selecionado. Para cada arquivo, ele extrai a extensão (a parte após o último ponto no nome do arquivo). Em seguida, ele move o arquivo para uma subpasta dentro do mesmo diretório selecionado, cujo nome é a extensão do arquivo. Se a subpasta para uma determinada extensão ainda não existir, ela é criada automaticamente antes que o arquivo seja movido.
3.  **Criação Dinâmica de Pastas**: O script verifica a existência de uma pasta com o nome da extensão antes de tentar mover um arquivo para ela. Isso garante que todas as extensões de arquivo encontradas no diretório selecionado terão sua pasta correspondente criada para a organização.
4.  **Interface Gráfica (GUI)**: O script cria uma janela com título, um campo para inserir um ano (atualmente para filtro, mas a lógica de filtro está comentada), um rótulo instruindo o usuário e botões para acionar a seleção do diretório e o processo de organização. A interface é definida com dimensões fixas e uma cor de fundo específica.
5.  **Feedback ao Usuário**: Após a conclusão do processo de organização, uma caixa de mensagem é exibida para informar ao usuário que os arquivos foram organizados com sucesso.

## Estrutura do Código

1.  **Importações**: As bibliotecas e módulos necessários (`os`, `time`, `datetime`, `tkinter` e seus submódulos) são importados no início do script.
2.  **Função `organizar_arquivo(diretorio, ano)`**:
    *   Recebe o caminho do diretório e o ano (do campo de entrada da GUI) como argumentos.
    *   Muda o diretório de trabalho atual para o `diretorio` fornecido usando `os.chdir()`.
    *   Inicializa um contador `count` (atualmente não utilizado para exibição ou lógica).
    *   Obtém uma lista de todos os itens no diretório, filtra apenas os arquivos (`os.path.isfile`) e (atualmente) converte seus nomes para letras minúsculas.
    *   Cria um conjunto (`set`) contendo todas as extensões únicas encontradas nos arquivos listados. Isso garante que cada tipo de extensão será processado apenas uma vez para a criação de pastas.
    *   Itera sobre cada `tipo` (extensão) no conjunto de `tipos`:
        *   Verifica se um diretório com o nome dessa extensão já existe usando `os.path.exists()`.
        *   Se não existir, cria o diretório usando `os.mkdir()`.
    *   Itera sobre cada `arquivo` na lista de arquivos:
        *   Extrai a extensão do arquivo dividindo o nome do arquivo pelo ponto e pegando a última parte (`arquivo.split(".")[-1]`).
        *   Define o caminho completo de origem (`de`) e destino (`para`) do arquivo usando `os.path.join()` para garantir que os caminhos sejam construídos corretamente para o sistema operacional atual.
        *   Move o arquivo da origem para o destino usando `os.replace()`. `os.replace` é atômico e moverá ou renomeará o arquivo.
        *   Incrementa o contador `count`.
    *   Após organizar todos os arquivos, exibe uma caixa de mensagem informativa usando `messagebox.showinfo()`.
3.  **Função `selecionar_arquivo(ano)`**:
    *   Recebe o ano (do campo de entrada da GUI) como argumento.
    *   Abre uma caixa de diálogo de seleção de diretório usando `filedialog.askdirectory()`.
    *   Se um diretório for selecionado (`folder_selected` não for vazio), chama a função `organizar_arquivo` passando o diretório selecionado e o ano (atualmente não usado ativamente na lógica de organização). Note que a conversão para inteiro `int(ano)` pode causar erro se o campo estiver vazio ou não for um número.
4.  **Configuração da Interface Gráfica**:
    *   Cria a instância principal da janela (`window = Tk()`).
    *   Configura o título da janela (`window.title()`), o tamanho (`window.geometry()`) e a cor de fundo (`window.configure(bg=...)`).
    *   Cria um widget `Canvas` para servir como área de desenho para outros elementos visuais.
    *   Posiciona o `Canvas` na janela.
    *   Desenha um retângulo no `Canvas` (provavelmente para estilizar a área de entrada do ano).
    *   Adiciona texto ao `Canvas` para o título da aplicação e a instrução sobre o ano.
    *   Cria um widget `Entry` para a entrada do ano, configura seu estilo e o posiciona na janela.
    *   Cria dois widgets `Button`.
        *   O primeiro botão (`button_1`) é configurado com o texto "Selecionar", sem borda ou highlight. Seu comando é um `lambda` que chama `selecionar_arquivo` passando o conteúdo atual do `entry_1`.
        *   O segundo botão (`button_2`) também é configurado com o texto "Selecionar" e sem borda ou highlight, mas não tem um comando associado visivelmente no código fornecido, nem está posicionado na janela. Ele parece ser redundante ou incompleto.
    *   Posiciona o `button_1` na janela.
    *   Impede que a janela seja redimensionada pelo usuário (`window.resizable(False, False)`).
    *   Inicia o loop principal da interface gráfica (`window.mainloop()`), que aguarda eventos do usuário (como cliques de botão) e atualiza a GUI.

## Como Executar o Script

1.  **Requisitos**: Certifique-se de ter o Python instalado em seu sistema. As bibliotecas `os`, `time`, `datetime` e `tkinter` geralmente vêm instaladas por padrão com o Python.
2.  **Salvar o Código**: Salve o código fornecido em um arquivo com a extensão `.py` (por exemplo, `organizador.py`).
3.  **Executar pelo Terminal**: Abra um terminal ou prompt de comando, navegue até o diretório onde você salvou o arquivo e execute o comando:
4. **Executar em um Ambiente de Desenvolvimento (IDE)**: A maioria das IDEs modernas permite executar arquivos Python diretamente. Abra o arquivo organizador.py na sua IDE e utilize a função de "Executar" (geralmente um ícone de triângulo verde).

Ao executar o script, a janela do organizador de arquivos será exibida.


## Possíveis Melhorias e Funcionalidades Futuras:

* **Ativar o Filtro por Ano:** Descomentar e refinar a lógica de filtragem por ano baseada na data de modificação do arquivo. Pode ser útil adicionar uma opção na GUI para habilitar ou desabilitar este filtro.

* **Tratamento de Erros:** Implementar tratamento de erros para casos como:
  * O usuário não selecionar um diretório.
  * Permissões de escrita insuficientes no diretório selecionado.
  * Erros ao mover arquivos.


* **Feedback de Progresso:** Para diretórios com muitos arquivos, seria útil fornecer um feedback visual do progresso da organização (por exemplo, uma barra de progresso ou exibindo o nome do arquivo que está sendo processado).

* **Opções de Organização:** Adicionar mais opções de organização, como por data de criação, tamanho do arquivo, ou permitir que o usuário especifique as regras de organização (por exemplo, agrupar PDFs e DOCs na mesma pasta "Documentos").


* **Personalização da Interface:** Permitir que o usuário personalize a aparência da janela.

* ** Log de Atividades:** Registrar as ações realizadas (quais arquivos foram movidos, para onde) em um arquivo de log.

* **Tratar Arquivos sem Extensão:** Decidir como lidar com arquivos que não possuem extensão. Atualmente, eles podem causar um erro ou ser agrupados de forma 
inesperada.

## Licença:

Projeto sob licença GNU



