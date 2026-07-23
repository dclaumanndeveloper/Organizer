import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from organizer_core import organizar_arquivos

BG_COLOR = "#FAFBFF"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1E1E1E"
MUTED_COLOR = "#6B6B6B"
PRIMARY_COLOR = "#4C5FD5"
PRIMARY_HOVER = "#3B4BC0"


class OrganizadorApp:
    LARGURA = 560
    ALTURA = 520

    def __init__(self, window):
        self.window = window
        self._configurar_janela()
        self._configurar_estilos()
        self._construir_layout()

    def _configurar_janela(self):
        self.window.title("Organizador de Arquivos")
        self.window.configure(bg=BG_COLOR)
        self.window.minsize(480, 460)
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
        self.label_diretorio = ttk.Label(
            dir_frame,
            text="Nenhuma pasta selecionada ainda",
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
        ttk.Label(
            container,
            text="Arquivos modificados antes desse ano serão ignorados. "
            "Deixe em branco para organizar tudo.",
            style="Muted.TLabel",
            wraplength=500,
        ).pack(anchor="w", pady=(0, 20))

        self.botao_organizar = ttk.Button(
            container,
            text="Selecionar pasta e organizar",
            style="Primary.TButton",
            command=self._selecionar_e_organizar,
        )
        self.botao_organizar.pack(anchor="w", pady=(0, 20))

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

        self._escrever_resultado("Os resultados da organização aparecerão aqui.")

    def _escrever_resultado(self, texto):
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.delete("1.0", "end")
        self.texto_resultado.insert("1.0", texto)
        self.texto_resultado.configure(state="disabled")

    def _selecionar_e_organizar(self):
        diretorio = filedialog.askdirectory()
        if not diretorio:
            return

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

        self.botao_organizar.configure(state="disabled", text="Organizando...")
        self.window.update_idletasks()
        try:
            stats = organizar_arquivos(diretorio, ano_minimo)
        except NotADirectoryError as exc:
            messagebox.showerror("Organizador", str(exc))
            return
        finally:
            self.botao_organizar.configure(
                state="normal", text="Selecionar pasta e organizar"
            )

        self._mostrar_resultado(stats)

    def _mostrar_resultado(self, stats):
        linhas = [f"{stats['movidos']} arquivo(s) organizado(s) com sucesso."]
        if stats["ignorados"]:
            linhas.append(
                f"{stats['ignorados']} arquivo(s) ignorado(s) pelo filtro de ano."
            )
        if stats["erros"]:
            linhas.append(f"{len(stats['erros'])} erro(s):")
            linhas.extend(f"  - {erro}" for erro in stats["erros"])

        self._escrever_resultado("\n".join(linhas))

        if stats["erros"]:
            messagebox.showwarning(
                "Organizador",
                "Organização concluída com erros. Veja os detalhes na janela.",
            )
        else:
            messagebox.showinfo("Organizador", "Arquivos organizados com sucesso!")


def main():
    window = tk.Tk()
    OrganizadorApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
