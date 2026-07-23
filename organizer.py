import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import organizer_ai
import organizer_history
from organizer_config import carregar_config, salvar_config
from organizer_core import carregar_mapa_categorias, carregar_regras, organizar_arquivos

BG_COLOR = "#FAFBFF"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1E1E1E"
MUTED_COLOR = "#6B6B6B"
PRIMARY_COLOR = "#4C5FD5"
PRIMARY_HOVER = "#3B4BC0"

CAMINHO_CATEGORIAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "categorias.json"
)
CAMINHO_REGRAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "regras.json"
)


class OrganizadorApp:
    LARGURA = 560
    ALTURA = 560

    def __init__(self, window):
        self.window = window
        config = carregar_config()
        self.ultimo_diretorio = config.get("ultimo_diretorio") or None
        self._ano_inicial = config.get("ano_minimo", "")
        self.var_simular = tk.BooleanVar(value=config.get("simular", False))
        self.var_categorias = tk.BooleanVar(value=config.get("categorias", False))
        self.var_ia = tk.BooleanVar(value=config.get("ia", False))
        self.var_recursivo = tk.BooleanVar(value=config.get("recursivo", False))
        self.var_duplicados = tk.BooleanVar(value=config.get("duplicados", False))
        self.var_regras = tk.BooleanVar(value=config.get("regras", False))

        self._configurar_janela()
        self._configurar_estilos()
        self._construir_layout()

    def _configurar_janela(self):
        self.window.title("Organizador de Arquivos")
        self.window.configure(bg=BG_COLOR)
        self.window.minsize(480, 500)
        self._centralizar_janela()

    def _centralizar_janela(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.LARGURA // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.ALTURA // 2)
        self.window.geometry(f"{self.LARGURA}x{self.ALTURA}+{x}+{y}")

    def _configurar_estilos(self):
        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_COLOR)
        style.configure(
            "Title.TLabel",
            background=BG_COLOR,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=BG_COLOR,
            foreground=MUTED_COLOR,
            font=("Segoe UI", 10),
        )
        style.configure(
            "FieldLabel.TLabel",
            background=BG_COLOR,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background=BG_COLOR,
            foreground=MUTED_COLOR,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Directory.TLabel",
            background=CARD_COLOR,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 9),
            padding=8,
        )
        style.configure("Check.TCheckbutton", background=BG_COLOR, font=("Segoe UI", 9))
        style.configure(
            "Primary.TButton",
            background=PRIMARY_COLOR,
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", PRIMARY_HOVER), ("pressed", PRIMARY_HOVER)],
        )

    def _construir_layout(self):
        container = ttk.Frame(self.window, style="App.TFrame", padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container, text="Organizador de Arquivos", style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            container,
            text="Selecione uma pasta para organizar os arquivos por tipo automaticamente.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 20))

        ttk.Label(
            container, text="Pasta selecionada", style="FieldLabel.TLabel"
        ).pack(anchor="w")
        dir_frame = ttk.Frame(container, style="Card.TFrame")
        dir_frame.pack(fill="x", pady=(6, 16))
        texto_diretorio_inicial = "Nenhuma pasta selecionada ainda"
        if self.ultimo_diretorio and os.path.isdir(self.ultimo_diretorio):
            texto_diretorio_inicial = self.ultimo_diretorio
        self.label_diretorio = ttk.Label(
            dir_frame,
            text=texto_diretorio_inicial,
            style="Directory.TLabel",
        )
        self.label_diretorio.pack(fill="x")

        ttk.Label(
            container,
            text="Ano mínimo de modificação (opcional)",
            style="FieldLabel.TLabel",
        ).pack(anchor="w")
        self.entry_ano = ttk.Entry(container, font=("Segoe UI", 10))
        self.entry_ano.pack(fill="x", pady=(6, 4))
        if self._ano_inicial:
            self.entry_ano.insert(0, self._ano_inicial)
        ttk.Label(
            container,
            text="Arquivos modificados antes desse ano serão ignorados. "
            "Deixe em branco para organizar tudo.",
            style="Muted.TLabel",
            wraplength=500,
        ).pack(anchor="w", pady=(0, 12))

        opcoes_frame = ttk.Frame(container, style="App.TFrame")
        opcoes_frame.pack(fill="x", pady=(0, 16))
        ttk.Checkbutton(
            opcoes_frame,
            text="Simular (não mover arquivos, só mostrar o que aconteceria)",
            variable=self.var_simular,
            style="Check.TCheckbutton",
        ).pack(anchor="w")
        ttk.Checkbutton(
            opcoes_frame,
            text="Agrupar por categoria (Imagens, Documentos, ...) em vez de extensão",
            variable=self.var_categorias,
            style="Check.TCheckbutton",
        ).pack(anchor="w")
        ttk.Checkbutton(
            opcoes_frame,
            text="Usar IA local (Ollama) para sugerir a categoria de cada arquivo",
            variable=self.var_ia,
            style="Check.TCheckbutton",
        ).pack(anchor="w")
        ttk.Checkbutton(
            opcoes_frame,
            text="Organizar subpastas também (recursivo)",
            variable=self.var_recursivo,
            style="Check.TCheckbutton",
        ).pack(anchor="w")
        ttk.Checkbutton(
            opcoes_frame,
            text="Detectar arquivos duplicados (mesmo conteúdo)",
            variable=self.var_duplicados,
            style="Check.TCheckbutton",
        ).pack(anchor="w")
        ttk.Checkbutton(
            opcoes_frame,
            text="Usar regras personalizadas por nome (regras.json)",
            variable=self.var_regras,
            style="Check.TCheckbutton",
        ).pack(anchor="w")

        botoes_frame = ttk.Frame(container, style="App.TFrame")
        botoes_frame.pack(fill="x", pady=(0, 12))
        self.botao_organizar = ttk.Button(
            botoes_frame,
            text="Selecionar pasta e organizar",
            style="Primary.TButton",
            command=self._selecionar_e_organizar,
        )
        self.botao_organizar.pack(side="left")
        self.botao_desfazer = ttk.Button(
            botoes_frame,
            text="Desfazer última organização",
            command=self._desfazer_ultima_organizacao,
        )
        self.botao_desfazer.pack(side="left", padx=(8, 0))
        self._atualizar_estado_botao_desfazer()

        self.progress = ttk.Progressbar(container, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 20))

        ttk.Label(container, text="Resultado", style="FieldLabel.TLabel").pack(
            anchor="w"
        )
        resultado_frame = ttk.Frame(container, style="Card.TFrame")
        resultado_frame.pack(fill="both", expand=True, pady=(6, 0))

        self.texto_resultado = tk.Text(
            resultado_frame,
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            relief="flat",
            font=("Segoe UI", 9),
            wrap="word",
            height=8,
            state="disabled",
            padx=10,
            pady=10,
        )
        scrollbar = ttk.Scrollbar(
            resultado_frame, command=self.texto_resultado.yview
        )
        self.texto_resultado.configure(yscrollcommand=scrollbar.set)
        self.texto_resultado.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._limpar_resultado("Os resultados da organização aparecerão aqui.")

    def _limpar_resultado(self, texto=""):
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.delete("1.0", "end")
        if texto:
            self.texto_resultado.insert("1.0", texto)
        self.texto_resultado.configure(state="disabled")

    def _adicionar_linha_resultado(self, linha):
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.insert("end", linha + "\n")
        self.texto_resultado.see("end")
        self.texto_resultado.configure(state="disabled")

    def _preparar_categorias_e_classificador(self):
        mapa_categorias = None
        if self.var_categorias.get() or self.var_ia.get():
            mapa_categorias = carregar_mapa_categorias(CAMINHO_CATEGORIAS)

        classificador = None
        if self.var_ia.get():
            if not organizer_ai.ollama_disponivel():
                messagebox.showwarning(
                    "Organizador",
                    "Ollama não está disponível em localhost:11434. "
                    "Continuando sem classificação por IA (usando "
                    "extensão/categoria padrão).",
                )
            else:
                categorias_disponiveis = sorted(set(mapa_categorias.values()))

                def classificador(nome_arquivo, caminho_arquivo, extensao):
                    return organizer_ai.classificar_arquivo(
                        nome_arquivo,
                        caminho_arquivo,
                        extensao,
                        categorias_disponiveis,
                    )

        return mapa_categorias, classificador

    def _atualizar_estado_botao_desfazer(self):
        tem_historico = bool(organizer_history.carregar_historico())
        self.botao_desfazer.configure(
            state="normal" if tem_historico else "disabled"
        )

    def _desfazer_ultima_organizacao(self):
        try:
            stats = organizer_history.desfazer_ultima_operacao()
        except ValueError as exc:
            messagebox.showinfo("Organizador", str(exc))
            return

        self._limpar_resultado()
        self._adicionar_linha_resultado(
            f"{stats['revertidos']} arquivo(s) revertido(s) para o local original."
        )
        if stats["erros"]:
            self._adicionar_linha_resultado(f"{len(stats['erros'])} erro(s):")
            for erro in stats["erros"]:
                self._adicionar_linha_resultado(f"  - {erro}")
            messagebox.showwarning(
                "Organizador",
                "Desfeito com alguns erros. Veja os detalhes na janela.",
            )
        else:
            messagebox.showinfo("Organizador", "Última organização desfeita com sucesso!")

        self._atualizar_estado_botao_desfazer()

    def _selecionar_e_organizar(self):
        diretorio = filedialog.askdirectory(
            initialdir=self.ultimo_diretorio or os.path.expanduser("~")
        )
        if not diretorio:
            return

        self.ultimo_diretorio = diretorio
        self.label_diretorio.configure(text=diretorio)

        ano_texto = self.entry_ano.get().strip()
        ano_minimo = None
        if ano_texto:
            try:
                ano_minimo = int(ano_texto)
            except ValueError:
                messagebox.showerror(
                    "Organizador",
                    "Ano inválido. Informe um número (ex: 2020) ou deixe o "
                    "campo em branco.",
                )
                return

        mapa_categorias, classificador = self._preparar_categorias_e_classificador()
        simular = self.var_simular.get()
        recursivo = self.var_recursivo.get()
        detectar_duplicados = self.var_duplicados.get()
        regras = carregar_regras(CAMINHO_REGRAS) if self.var_regras.get() else None

        salvar_config(
            {
                "ultimo_diretorio": diretorio,
                "ano_minimo": ano_texto,
                "simular": simular,
                "categorias": self.var_categorias.get(),
                "ia": self.var_ia.get(),
                "recursivo": recursivo,
                "duplicados": detectar_duplicados,
                "regras": self.var_regras.get(),
            }
        )

        self.botao_organizar.configure(state="disabled", text="Organizando...")
        self.progress.configure(value=0, maximum=1)
        self._limpar_resultado()
        self.window.update_idletasks()

        verbo = "seria movido" if simular else "movido"

        def registrar_progresso(indice, total, nome_arquivo, status, pasta_destino):
            self.progress.configure(maximum=total, value=indice)
            descricao = {
                "movido": f"{verbo} para {pasta_destino}/",
                "duplicado": f"duplicado, {verbo} para {pasta_destino}/",
                "ignorado": "ignorado (filtro de ano)",
                "erro": "erro ao processar",
            }[status]
            self._adicionar_linha_resultado(
                f"[{indice}/{total}] {nome_arquivo} - {descricao}"
            )
            self.window.update_idletasks()

        try:
            stats = organizar_arquivos(
                diretorio,
                ano_minimo,
                mapa_categorias=mapa_categorias,
                classificador_categoria=classificador,
                regras=regras,
                detectar_duplicados=detectar_duplicados,
                simular=simular,
                recursivo=recursivo,
                progresso_callback=registrar_progresso,
            )
        except NotADirectoryError as exc:
            messagebox.showerror("Organizador", str(exc))
            return
        finally:
            self.botao_organizar.configure(
                state="normal", text="Selecionar pasta e organizar"
            )

        organizer_history.registrar_operacao(stats["movimentos"])
        self._atualizar_estado_botao_desfazer()
        self._mostrar_resultado(stats, simular)

    def _mostrar_resultado(self, stats, simular):
        if (
            stats["movidos"] == stats["duplicados"] == stats["ignorados"] == 0
            and not stats["erros"]
        ):
            self._adicionar_linha_resultado("Nenhum arquivo encontrado na pasta.")
            messagebox.showinfo("Organizador", "Nenhum arquivo encontrado na pasta.")
            return

        verbo = "seria(m) organizado(s)" if simular else "organizado(s) com sucesso"
        linhas = ["", f"{stats['movidos']} arquivo(s) {verbo}."]
        if stats["duplicados"]:
            linhas.append(
                f"{stats['duplicados']} arquivo(s) duplicado(s) movido(s) para "
                "\"duplicados/\"."
            )
        if stats["ignorados"]:
            linhas.append(
                f"{stats['ignorados']} arquivo(s) ignorado(s) pelo filtro de ano."
            )
        if stats["erros"]:
            linhas.append(f"{len(stats['erros'])} erro(s):")
            linhas.extend(f"  - {erro}" for erro in stats["erros"])

        for linha in linhas:
            self._adicionar_linha_resultado(linha)

        if stats["erros"]:
            messagebox.showwarning(
                "Organizador",
                "Organização concluída com erros. Veja os detalhes na janela.",
            )
        elif simular:
            messagebox.showinfo(
                "Organizador",
                "Simulação concluída. Desmarque \"Simular\" e organize "
                "novamente para mover os arquivos de verdade.",
            )
        else:
            messagebox.showinfo("Organizador", "Arquivos organizados com sucesso!")


def main():
    window = tk.Tk()
    OrganizadorApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
