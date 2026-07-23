IDIOMA_PADRAO = "pt"

IDIOMAS_DISPONIVEIS = {"pt": "Português", "en": "English", "es": "Español"}

_TEXTOS = {
    "titulo_janela": {
        "pt": "Organizador de Arquivos",
        "en": "File Organizer",
        "es": "Organizador de Archivos",
    },
    "subtitulo": {
        "pt": "Selecione uma pasta para organizar os arquivos por tipo automaticamente.",
        "en": "Select a folder to automatically organize its files by type.",
        "es": "Selecciona una carpeta para organizar los archivos por tipo automáticamente.",
    },
    "rotulo_idioma": {"pt": "Idioma", "en": "Language", "es": "Idioma"},
    "rotulo_pasta": {
        "pt": "Pasta selecionada",
        "en": "Selected folder",
        "es": "Carpeta seleccionada",
    },
    "pasta_nao_selecionada": {
        "pt": "Nenhuma pasta selecionada ainda",
        "en": "No folder selected yet",
        "es": "Ninguna carpeta seleccionada todavía",
    },
    "rotulo_ano": {
        "pt": "Ano mínimo de modificação (opcional)",
        "en": "Minimum modification year (optional)",
        "es": "Año mínimo de modificación (opcional)",
    },
    "ajuda_ano": {
        "pt": "Arquivos modificados antes desse ano serão ignorados. "
        "Deixe em branco para organizar tudo.",
        "en": "Files modified before this year will be skipped. "
        "Leave blank to organize everything.",
        "es": "Los archivos modificados antes de ese año serán ignorados. "
        "Deja en blanco para organizar todo.",
    },
    "check_simular": {
        "pt": "Simular (não mover arquivos, só mostrar o que aconteceria)",
        "en": "Simulate (don't move files, just show what would happen)",
        "es": "Simular (no mover archivos, solo mostrar qué pasaría)",
    },
    "check_categorias": {
        "pt": "Agrupar por categoria (Imagens, Documentos, ...) em vez de extensão",
        "en": "Group by category (Images, Documents, ...) instead of extension",
        "es": "Agrupar por categoría (Imágenes, Documentos, ...) en vez de extensión",
    },
    "check_ia": {
        "pt": "Usar IA local (Ollama) para sugerir a categoria de cada arquivo",
        "en": "Use local AI (Ollama) to suggest each file's category",
        "es": "Usar IA local (Ollama) para sugerir la categoría de cada archivo",
    },
    "check_recursivo": {
        "pt": "Organizar subpastas também (recursivo)",
        "en": "Organize subfolders too (recursive)",
        "es": "Organizar también las subcarpetas (recursivo)",
    },
    "check_duplicados": {
        "pt": "Detectar arquivos duplicados (mesmo conteúdo)",
        "en": "Detect duplicate files (same content)",
        "es": "Detectar archivos duplicados (mismo contenido)",
    },
    "check_regras": {
        "pt": "Usar regras personalizadas por nome (regras.json)",
        "en": "Use custom rules by filename (regras.json)",
        "es": "Usar reglas personalizadas por nombre (regras.json)",
    },
    "check_monitorar": {
        "pt": "Monitorar a pasta continuamente (a cada {intervalo}s)",
        "en": "Monitor the folder continuously (every {intervalo}s)",
        "es": "Monitorear la carpeta continuamente (cada {intervalo}s)",
    },
    "botao_organizar": {
        "pt": "Selecionar pasta e organizar",
        "en": "Select folder and organize",
        "es": "Seleccionar carpeta y organizar",
    },
    "botao_organizando": {
        "pt": "Organizando...",
        "en": "Organizing...",
        "es": "Organizando...",
    },
    "botao_parar_monitoramento": {
        "pt": "Parar monitoramento",
        "en": "Stop monitoring",
        "es": "Detener monitoreo",
    },
    "botao_desfazer": {
        "pt": "Desfazer última organização",
        "en": "Undo last organization",
        "es": "Deshacer última organización",
    },
    "rotulo_resultado": {"pt": "Resultado", "en": "Result", "es": "Resultado"},
    "resultado_inicial": {
        "pt": "Os resultados da organização aparecerão aqui.",
        "en": "The organization results will appear here.",
        "es": "Los resultados de la organización aparecerán aquí.",
    },
    "aviso_ollama_indisponivel": {
        "pt": "Ollama não está disponível em localhost:11434. Continuando sem "
        "classificação por IA (usando extensão/categoria padrão).",
        "en": "Ollama is not available at localhost:11434. Continuing without "
        "AI classification (using default extension/category).",
        "es": "Ollama no está disponible en localhost:11434. Continuando sin "
        "clasificación por IA (usando extensión/categoría predeterminada).",
    },
    "erro_ano_invalido": {
        "pt": "Ano inválido. Informe um número (ex: 2020) ou deixe o campo em branco.",
        "en": "Invalid year. Enter a number (e.g. 2020) or leave the field blank.",
        "es": "Año inválido. Ingresa un número (ej: 2020) o deja el campo en blanco.",
    },
    "ciclo_pulado": {
        "pt": "Ciclo pulado: {mensagem}",
        "en": "Cycle skipped: {mensagem}",
        "es": "Ciclo omitido: {mensagem}",
    },
    "erro_generico": {"pt": "Erro: {erro}", "en": "Error: {erro}", "es": "Error: {erro}"},
    "status_movido": {
        "pt": "{verbo} para {pasta}/",
        "en": "{verbo} to {pasta}/",
        "es": "{verbo} a {pasta}/",
    },
    "status_duplicado": {
        "pt": "duplicado, {verbo} para {pasta}/",
        "en": "duplicate, {verbo} to {pasta}/",
        "es": "duplicado, {verbo} a {pasta}/",
    },
    "status_ignorado": {
        "pt": "ignorado (filtro de ano)",
        "en": "skipped (year filter)",
        "es": "ignorado (filtro de año)",
    },
    "status_erro": {
        "pt": "erro ao processar",
        "en": "error processing",
        "es": "error al procesar",
    },
    "verbo_seria_movido": {
        "pt": "seria movido",
        "en": "would be moved",
        "es": "sería movido",
    },
    "verbo_movido": {"pt": "movido", "en": "moved", "es": "movido"},
    "monitoramento_iniciado": {
        "pt": "Monitoramento iniciado em {diretorio} (a cada {intervalo}s). "
        "Clique no botão novamente para parar.",
        "en": "Monitoring started on {diretorio} (every {intervalo}s). "
        "Click the button again to stop.",
        "es": "Monitoreo iniciado en {diretorio} (cada {intervalo}s). "
        "Haz clic en el botón de nuevo para detener.",
    },
    "monitoramento_interrompido": {
        "pt": "Monitoramento interrompido.",
        "en": "Monitoring stopped.",
        "es": "Monitoreo detenido.",
    },
    "nenhum_arquivo_encontrado": {
        "pt": "Nenhum arquivo encontrado na pasta.",
        "en": "No files found in the folder.",
        "es": "No se encontraron archivos en la carpeta.",
    },
    "resumo_organizados": {
        "pt": "{n} arquivo(s) {verbo}.",
        "en": "{n} file(s) {verbo}.",
        "es": "{n} archivo(s) {verbo}.",
    },
    "verbo_seriam_organizados": {
        "pt": "seria(m) organizado(s)",
        "en": "would be organized",
        "es": "sería(n) organizado(s)",
    },
    "verbo_organizados_sucesso": {
        "pt": "organizado(s) com sucesso",
        "en": "organized successfully",
        "es": "organizado(s) con éxito",
    },
    "resumo_duplicados": {
        "pt": '{n} arquivo(s) duplicado(s) movido(s) para "duplicados/".',
        "en": '{n} duplicate file(s) moved to "duplicados/".',
        "es": '{n} archivo(s) duplicado(s) movido(s) a "duplicados/".',
    },
    "resumo_ignorados": {
        "pt": "{n} arquivo(s) ignorado(s) pelo filtro de ano.",
        "en": "{n} file(s) skipped by the year filter.",
        "es": "{n} archivo(s) ignorado(s) por el filtro de año.",
    },
    "resumo_erros_titulo": {
        "pt": "{n} erro(s):",
        "en": "{n} error(s):",
        "es": "{n} error(es):",
    },
    "aviso_erros": {
        "pt": "Organização concluída com erros. Veja os detalhes na janela.",
        "en": "Organization finished with errors. See details in the window.",
        "es": "Organización terminada con errores. Consulta los detalles en la ventana.",
    },
    "info_simulacao": {
        "pt": 'Simulação concluída. Desmarque "Simular" e organize novamente '
        "para mover os arquivos de verdade.",
        "en": 'Simulation finished. Uncheck "Simulate" and organize again to '
        "actually move the files.",
        "es": 'Simulación terminada. Desmarca "Simular" y organiza de nuevo '
        "para mover los archivos de verdad.",
    },
    "info_sucesso": {
        "pt": "Arquivos organizados com sucesso!",
        "en": "Files organized successfully!",
        "es": "¡Archivos organizados con éxito!",
    },
    "revertido_resumo": {
        "pt": "{n} arquivo(s) revertido(s) para o local original.",
        "en": "{n} file(s) reverted to their original location.",
        "es": "{n} archivo(s) revertido(s) a su ubicación original.",
    },
    "aviso_desfazer_erros": {
        "pt": "Desfeito com alguns erros. Veja os detalhes na janela.",
        "en": "Undone with some errors. See details in the window.",
        "es": "Deshecho con algunos errores. Consulta los detalles en la ventana.",
    },
    "info_desfazer_sucesso": {
        "pt": "Última organização desfeita com sucesso!",
        "en": "Last organization undone successfully!",
        "es": "¡Última organización deshecha con éxito!",
    },
    "titulo_organizador": {"pt": "Organizador", "en": "Organizer", "es": "Organizador"},
}


def t(idioma, chave, **kwargs):
    """Traduz `chave` para `idioma`, com fallback para IDIOMA_PADRAO.

    Se a chave não existir, devolve a própria chave (nunca lança exceção -
    uma tradução faltando não deveria quebrar a interface). Aceita
    interpolação via `str.format(**kwargs)`.
    """
    traducoes_chave = _TEXTOS.get(chave)
    if traducoes_chave is None:
        return chave
    texto = traducoes_chave.get(idioma) or traducoes_chave.get(IDIOMA_PADRAO, chave)
    return texto.format(**kwargs) if kwargs else texto
