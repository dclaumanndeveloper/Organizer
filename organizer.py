import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import organizer_ai
import organizer_history
from organizer_config import carregar_config, salvar_config
from organizer_core import carregar_mapa_categorias, carregar_regras, organizar_arquivos
from organizer_i18n import IDIOMA_PADRAO, IDIOMAS_DISPONIVEIS, t

BG_COLOR = "#FAFBFF"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1E1E1E"
MUTED_COLOR = "#6B6B6B"
PRIMARY_COLOR = "#4C5FD5"
PRIMARY_HOVER = "#3B4BC0"

CAMINHO_CATEGORIAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "categorias.json"
)
CAMINHO_REGRAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regras.json")

INTERVALO_MONITORAMENTO_MS = 30_000


class OrganizadorApp:
    LARGURA = 560
    ALTURA = 560

    def __init__(self, window):
        self.window = window
        config = carregar_config()
        self.idioma = config.get("idioma") or IDIOMA_PADRAO
        self.ultimo_diretorio = config.get("ultimo_diretorio") or None
        self._ano_inicial = config.get("ano_minimo", "")
        self.var_simular = tk.BooleanVar(value=config.get("simular", False))
        self.var_categorias = tk.BooleanVar(value=config.get("categorias", False))
        self.var_ia = tk.BooleanVar(value=config.get("ia", False))
        self.var_recursivo = tk.BooleanVar(value=config.get("recursivo", False))
        self.var_duplicados = tk.BooleanVar(value=config.get("duplicados", False))
        self.var_regras = tk.BooleanVar(value=config.get("regras", False))
        self.var_monitorar = tk.BooleanVar(value=config.get("monitorar", False))

        self.monitorando = False
        self._id_agendamento_monitoramento = None
        self._estado_botao_organizar = "padrao"
        self._diretorio_selecionado = bool(
            self.ultimo_diretorio and os.path.isdir(self.ultimo_diretorio)
        )
        self._resultado_mostrando_inicial = True

        self._configurar_janela()
        self._configurar_estilos()
        self._construir_layout()

    def _t(self, chave, **kwargs):
        return t(self.idioma, chave, **kwargs)

    def _configurar_janela(self):
        self.window.title(self._t("titulo_janela"))
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

        cabecalho_frame = ttk.Frame(container, style="App.TFrame")
        cabecalho_frame.pack(fill="x")

        titulo_frame = ttk.Frame(cabecalho_frame, style="App.TFrame")
        titulo_frame.pack(side="left", fill="x", expand=True)
        self.rotulo_titulo = ttk.Label(
            titulo_frame, text=self._t("titulo_janela"), style="Title.TLabel"
        )
        self.rotulo_titulo.pack(anchor="w")
        self.rotulo_subtitulo = ttk.Label(
            titulo_frame,
            text=self._t("subtitulo"),
            style="Subtitle.TLabel",
        )
        self.rotulo_subtitulo.pack(anchor="w", pady=(4, 0))

        idioma_frame = ttk.Frame(cabecalho_frame, style="App.TFrame")
        idioma_frame.pack(side="right", anchor="ne")
        self.rotulo_idioma = ttk.Label(
            idioma_frame, text=self._t("rotulo_idioma"), style="Muted.TLabel"
        )
        self.rotulo_idioma.pack(anchor="e")
        self.combo_idioma = ttk.Combobox(
            idioma_frame,
            values=list(IDIOMAS_DISPONIVEIS.values()),
            state="readonly",
            width=10,
        )
        self.combo_idioma.set(
            IDIOMAS_DISPONIVEIS.get(self.idioma, IDIOMAS_DISPONIVEIS[IDIOMA_PADRAO])
        )
        self.combo_idioma.bind("<<ComboboxSelected>>", self._ao_trocar_idioma_combobox)
        self.combo_idioma.pack(anchor="e", pady=(2, 0))

        ttk.Frame(container, style="App.TFrame").pack(pady=(8, 0))

        self.rotulo_pasta = ttk.Label(
            container, text=self._t("rotulo_pasta"), style="FieldLabel.TLabel"
        )
        self.rotulo_pasta.pack(anchor="w")
        dir_frame = ttk.Frame(container, style="Card.TFrame")
        dir_frame.pack(fill="x", pady=(6, 16))
        texto_diretorio_inicial = (
            self.ultimo_diretorio
            if self._diretorio_selecionado
            else self._t("pasta_nao_selecionada")
        )
        self.label_diretorio = ttk.Label(
            dir_frame,
            text=texto_diretorio_inicial,
            style="Directory.TLabel",
        )
        self.label_diretorio.pack(fill="x")

        self.rotulo_ano = ttk.Label(
            container,
            text=self._t("rotulo_ano"),
            style="FieldLabel.TLabel",
        )
        self.rotulo_ano.pack(anchor="w")
        self.entry_ano = ttk.Entry(container, font=("Segoe UI", 10))
        self.entry_ano.pack(fill="x", pady=(6, 4))
        if self._ano_inicial:
            self.entry_ano.insert(0, self._ano_inicial)
        self.rotulo_ajuda_ano = ttk.Label(
            container,
            text=self._t("ajuda_ano"),
            style="Muted.TLabel",
            wraplength=500,
        )
        self.rotulo_ajuda_ano.pack(anchor="w", pady=(0, 12))

        opcoes_frame = ttk.Frame(container, style="App.TFrame")
        opcoes_frame.pack(fill="x", pady=(0, 16))
        self.check_simular = ttk.Checkbutton(
            opcoes_frame,
            text=self._t("check_simular"),
            variable=self.var_simular,
            style="Check.TCheckbutton",
        )
        self.check_simular.pack(anchor="w")
        self.check_categorias = ttk.Checkbutton(
            opcoes_frame,
            text=self._t("check_categorias"),
            variable=self.var_categorias,
            style="Check.TCheckbutton",
        )
        self.check_categorias.pack(anchor="w")
        self.check_ia = ttk.Checkbutton(
            opcoes_frame,
            text=self._t("check_ia"),
            variable=self.var_ia,
            style="Check.TCheckbutton",
        )
        self.check_ia.pack(anchor="w")
        self.check_recursivo = ttk.Checkbutton(
            opcoes_frame,
            text=self._t("check_recursivo"),
            variable=self.var_recursivo,
            style="Check.TCheckbutton",
        )
        self.check_recursivo.pack(anchor="w")
        self.check_duplicados = ttk.Checkbutton(
            opcoes_frame,
            text=self._t("check_duplicados"),
            variable=self.var_duplicados,
            style="Check.TCheckbutton",
        )
        self.check_duplicados.pack(anchor="w")
        self.check_regras = ttk.Checkbutton(
            opcoes_frame,
            text=self._t("check_regras"),
            variable=self.var_regras,
            style="Check.TCheckbutton",
        )
        self.check_regras.pack(anchor="w")
        self.check_monitorar = ttk.Checkbutton(
            opcoes_frame,
            text=self._texto_check_monitorar(),
            variable=self.var_monitorar,
            style="Check.TCheckbutton",
            command=self._ao_alternar_checkbox_monitorar,
        )
        self.check_monitorar.pack(anchor="w")

        botoes_frame = ttk.Frame(container, style="App.TFrame")
        botoes_frame.pack(fill="x", pady=(0, 12))
        self.botao_organizar = ttk.Button(
            botoes_frame,
            text=self._texto_botao_atual(),
            style="Primary.TButton",
            command=self._selecionar_e_organizar,
        )
        self.botao_organizar.pack(side="left")
        self.botao_desfazer = ttk.Button(
            botoes_frame,
            text=self._t("botao_desfazer"),
            command=self._desfazer_ultima_organizacao,
        )
        self.botao_desfazer.pack(side="left", padx=(8, 0))
        self._atualizar_estado_botao_desfazer()

        self.progress = ttk.Progressbar(
            container, orient="horizontal", mode="determinate"
        )
        self.progress.pack(fill="x", pady=(0, 20))

        self.rotulo_resultado = ttk.Label(
            container, text=self._t("rotulo_resultado"), style="FieldLabel.TLabel"
        )
        self.rotulo_resultado.pack(anchor="w")
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
        scrollbar = ttk.Scrollbar(resultado_frame, command=self.texto_resultado.yview)
        self.texto_resultado.configure(yscrollcommand=scrollbar.set)
        self.texto_resultado.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._limpar_resultado(self._t("resultado_inicial"))

    def _texto_check_monitorar(self):
        return self._t("check_monitorar", intervalo=INTERVALO_MONITORAMENTO_MS // 1000)

    def _texto_botao_atual(self):
        chave = {
            "padrao": "botao_organizar",
            "organizando": "botao_organizando",
            "parar_monitoramento": "botao_parar_monitoramento",
        }[self._estado_botao_organizar]
        return self._t(chave)

    def _definir_estado_botao_organizar(self, estado):
        self._estado_botao_organizar = estado
        self.botao_organizar.configure(text=self._texto_botao_atual())

    def _ao_trocar_idioma_combobox(self, event=None):
        nome_selecionado = self.combo_idioma.get()
        codigo = next(
            (
                cod
                for cod, nome in IDIOMAS_DISPONIVEIS.items()
                if nome == nome_selecionado
            ),
            IDIOMA_PADRAO,
        )
        self._trocar_idioma(codigo)

    def _trocar_idioma(self, codigo):
        self.idioma = codigo
        config_atual = carregar_config()
        config_atual["idioma"] = codigo
        salvar_config(config_atual)
        self._atualizar_textos_estaticos()

    def _atualizar_textos_estaticos(self):
        self.window.title(self._t("titulo_janela"))
        self.rotulo_titulo.configure(text=self._t("titulo_janela"))
        self.rotulo_subtitulo.configure(text=self._t("subtitulo"))
        self.rotulo_idioma.configure(text=self._t("rotulo_idioma"))
        self.rotulo_pasta.configure(text=self._t("rotulo_pasta"))
        if not self._diretorio_selecionado:
            self.label_diretorio.configure(text=self._t("pasta_nao_selecionada"))
        self.rotulo_ano.configure(text=self._t("rotulo_ano"))
        self.rotulo_ajuda_ano.configure(text=self._t("ajuda_ano"))
        self.check_simular.configure(text=self._t("check_simular"))
        self.check_categorias.configure(text=self._t("check_categorias"))
        self.check_ia.configure(text=self._t("check_ia"))
        self.check_recursivo.configure(text=self._t("check_recursivo"))
        self.check_duplicados.configure(text=self._t("check_duplicados"))
        self.check_regras.configure(text=self._t("check_regras"))
        self.check_monitorar.configure(text=self._texto_check_monitorar())
        self.botao_organizar.configure(text=self._texto_botao_atual())
        self.botao_desfazer.configure(text=self._t("botao_desfazer"))
        self.rotulo_resultado.configure(text=self._t("rotulo_resultado"))
        if self._resultado_mostrando_inicial:
            self._limpar_resultado(self._t("resultado_inicial"))

    def _limpar_resultado(self, texto=""):
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.delete("1.0", "end")
        if texto:
            self.texto_resultado.insert("1.0", texto)
        self.texto_resultado.configure(state="disabled")

    def _adicionar_linha_resultado(self, linha):
        self._resultado_mostrando_inicial = False
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.insert("end", linha + "\n")
        self.texto_resultado.see("end")
        self.texto_resultado.configure(state="disabled")

    def _preparar_categorias_e_classificador(self, silencioso):
        mapa_categorias = None
        if self.var_categorias.get() or self.var_ia.get():
            mapa_categorias = carregar_mapa_categorias(CAMINHO_CATEGORIAS)

        classificador = None
        if self.var_ia.get():
            if not organizer_ai.ollama_disponivel():
                aviso = self._t("aviso_ollama_indisponivel")
                if silencioso:
                    self._adicionar_linha_resultado(aviso)
                else:
                    messagebox.showwarning(self._t("titulo_organizador"), aviso)
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
        self.botao_desfazer.configure(state="normal" if tem_historico else "disabled")

    def _desfazer_ultima_organizacao(self):
        try:
            stats = organizer_history.desfazer_ultima_operacao()
        except ValueError as exc:
            messagebox.showinfo(self._t("titulo_organizador"), str(exc))
            return

        self._limpar_resultado()
        self._adicionar_linha_resultado(
            self._t("revertido_resumo", n=stats["revertidos"])
        )
        if stats["erros"]:
            self._adicionar_linha_resultado(
                self._t("resumo_erros_titulo", n=len(stats["erros"]))
            )
            for erro in stats["erros"]:
                self._adicionar_linha_resultado(f"  - {erro}")
            messagebox.showwarning(
                self._t("titulo_organizador"), self._t("aviso_desfazer_erros")
            )
        else:
            messagebox.showinfo(
                self._t("titulo_organizador"), self._t("info_desfazer_sucesso")
            )

        self._atualizar_estado_botao_desfazer()

    def _ao_alternar_checkbox_monitorar(self):
        if not self.var_monitorar.get() and self.monitorando:
            self._parar_monitoramento()

    def _selecionar_e_organizar(self):
        if self.monitorando:
            self._parar_monitoramento()
            return

        diretorio = filedialog.askdirectory(
            initialdir=self.ultimo_diretorio or os.path.expanduser("~")
        )
        if not diretorio:
            return

        self.ultimo_diretorio = diretorio
        self._diretorio_selecionado = True
        self.label_diretorio.configure(text=diretorio)

        if self.var_monitorar.get():
            self._iniciar_monitoramento(diretorio)
        else:
            self._organizar_diretorio(diretorio, silencioso=False)

    def _iniciar_monitoramento(self, diretorio):
        self.monitorando = True
        self._definir_estado_botao_organizar("parar_monitoramento")
        self._limpar_resultado()
        self._adicionar_linha_resultado(
            self._t(
                "monitoramento_iniciado",
                diretorio=diretorio,
                intervalo=INTERVALO_MONITORAMENTO_MS // 1000,
            )
        )
        self._executar_ciclo_monitoramento(diretorio)

    def _executar_ciclo_monitoramento(self, diretorio):
        if not self.monitorando:
            return
        self._organizar_diretorio(diretorio, silencioso=True)
        self._id_agendamento_monitoramento = self.window.after(
            INTERVALO_MONITORAMENTO_MS,
            lambda: self._executar_ciclo_monitoramento(diretorio),
        )

    def _parar_monitoramento(self):
        self.monitorando = False
        if self._id_agendamento_monitoramento is not None:
            self.window.after_cancel(self._id_agendamento_monitoramento)
            self._id_agendamento_monitoramento = None
        self._definir_estado_botao_organizar("padrao")
        self._adicionar_linha_resultado(self._t("monitoramento_interrompido"))

    def _organizar_diretorio(self, diretorio, silencioso):
        ano_texto = self.entry_ano.get().strip()
        ano_minimo = None
        if ano_texto:
            try:
                ano_minimo = int(ano_texto)
            except ValueError:
                mensagem = self._t("erro_ano_invalido")
                if silencioso:
                    self._adicionar_linha_resultado(
                        self._t("ciclo_pulado", mensagem=mensagem)
                    )
                else:
                    messagebox.showerror(self._t("titulo_organizador"), mensagem)
                return

        mapa_categorias, classificador = self._preparar_categorias_e_classificador(
            silencioso
        )
        simular = self.var_simular.get()
        recursivo = self.var_recursivo.get()
        detectar_duplicados = self.var_duplicados.get()
        regras = carregar_regras(CAMINHO_REGRAS) if self.var_regras.get() else None

        salvar_config(
            {
                "idioma": self.idioma,
                "ultimo_diretorio": diretorio,
                "ano_minimo": ano_texto,
                "simular": simular,
                "categorias": self.var_categorias.get(),
                "ia": self.var_ia.get(),
                "recursivo": recursivo,
                "duplicados": detectar_duplicados,
                "regras": self.var_regras.get(),
                "monitorar": self.var_monitorar.get(),
            }
        )

        if not silencioso:
            self._definir_estado_botao_organizar("organizando")
            self.botao_organizar.configure(state="disabled")
            self._limpar_resultado()
        self.progress.configure(value=0, maximum=1)
        self.window.update_idletasks()

        verbo = self._t("verbo_seria_movido") if simular else self._t("verbo_movido")

        def registrar_progresso(indice, total, nome_arquivo, status, pasta_destino):
            self.progress.configure(maximum=total, value=indice)
            descricao = {
                "movido": self._t("status_movido", verbo=verbo, pasta=pasta_destino),
                "duplicado": self._t(
                    "status_duplicado", verbo=verbo, pasta=pasta_destino
                ),
                "ignorado": self._t("status_ignorado"),
                "erro": self._t("status_erro"),
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
            if silencioso:
                self._adicionar_linha_resultado(self._t("erro_generico", erro=exc))
                self._parar_monitoramento()
            else:
                messagebox.showerror(self._t("titulo_organizador"), str(exc))
            return
        finally:
            if not silencioso:
                self._definir_estado_botao_organizar("padrao")
                self.botao_organizar.configure(state="normal")

        organizer_history.registrar_operacao(stats["movimentos"])
        self._atualizar_estado_botao_desfazer()
        self._mostrar_resultado(stats, simular, silencioso)

    def _mostrar_resultado(self, stats, simular, silencioso=False):
        if (
            stats["movidos"] == stats["duplicados"] == stats["ignorados"] == 0
            and not stats["erros"]
        ):
            self._adicionar_linha_resultado(self._t("nenhum_arquivo_encontrado"))
            if not silencioso:
                messagebox.showinfo(
                    self._t("titulo_organizador"), self._t("nenhum_arquivo_encontrado")
                )
            return

        verbo = (
            self._t("verbo_seriam_organizados")
            if simular
            else self._t("verbo_organizados_sucesso")
        )
        linhas = ["", self._t("resumo_organizados", n=stats["movidos"], verbo=verbo)]
        if stats["duplicados"]:
            linhas.append(self._t("resumo_duplicados", n=stats["duplicados"]))
        if stats["ignorados"]:
            linhas.append(self._t("resumo_ignorados", n=stats["ignorados"]))
        if stats["erros"]:
            linhas.append(self._t("resumo_erros_titulo", n=len(stats["erros"])))
            linhas.extend(f"  - {erro}" for erro in stats["erros"])

        for linha in linhas:
            self._adicionar_linha_resultado(linha)

        if silencioso:
            return

        if stats["erros"]:
            messagebox.showwarning(
                self._t("titulo_organizador"), self._t("aviso_erros")
            )
        elif simular:
            messagebox.showinfo(
                self._t("titulo_organizador"), self._t("info_simulacao")
            )
        else:
            messagebox.showinfo(self._t("titulo_organizador"), self._t("info_sucesso"))


def main():
    window = tk.Tk()
    OrganizadorApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
