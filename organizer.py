from tkinter import Tk, Canvas, Entry, Button, filedialog, messagebox

from organizer_core import organizar_arquivos


def selecionar_diretorio_e_organizar(ano_texto):
    diretorio = filedialog.askdirectory()
    if not diretorio:
        return

    ano_minimo = None
    ano_texto = ano_texto.strip()
    if ano_texto:
        try:
            ano_minimo = int(ano_texto)
        except ValueError:
            messagebox.showerror(
                "Organizador",
                "Ano inválido. Informe um número (ex: 2020) ou deixe em branco.",
            )
            return

    try:
        stats = organizar_arquivos(diretorio, ano_minimo)
    except NotADirectoryError as exc:
        messagebox.showerror("Organizador", str(exc))
        return

    mensagem = f"{stats['movidos']} arquivo(s) organizado(s) com sucesso!"
    if stats["ignorados"]:
        mensagem += f"\n{stats['ignorados']} arquivo(s) ignorado(s) pelo filtro de ano."

    if stats["erros"]:
        mensagem += f"\n{len(stats['erros'])} erro(s):\n" + "\n".join(stats["erros"])
        messagebox.showwarning("Organizador", mensagem)
    else:
        messagebox.showinfo("Organizador", mensagem)


def construir_janela():
    window = Tk()
    window.title("Organizador de arquivos")
    window.geometry("547x422")
    window.configure(bg="#FAFBFF")

    canvas = Canvas(
        window,
        bg="#FAFBFF",
        height=422,
        width=547,
        bd=0,
        highlightthickness=0,
        relief="ridge",
    )
    canvas.place(x=0, y=0)
    canvas.create_rectangle(42.0, 117.0, 242.0, 144.0, fill="#FFFFFF", outline="")
    canvas.create_text(
        42.0,
        91.0,
        anchor="nw",
        text="Insira o ano que deseja filtrar (opcional)",
        fill="#3F3F3F",
        font=("Poppins Medium", 12 * -1),
    )
    canvas.create_text(
        42.0,
        30.0,
        anchor="nw",
        text="Organizador de arquivos",
        fill="#1E1E1E",
        font=("Poppins Bold", 24 * -1),
    )

    entry_ano = Entry(bd=1, bg="#FFFFFF", fg="#000716", highlightthickness=0)
    entry_ano.place(x=75.0, y=117.0, width=163.0, height=25.0)

    button_selecionar = Button(
        text="Selecionar",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: selecionar_diretorio_e_organizar(entry_ano.get()),
        relief="flat",
    )
    button_selecionar.place(x=254.0, y=117.0, width=90.0, height=27.0)

    window.resizable(False, False)
    return window


def main():
    window = construir_janela()
    window.mainloop()


if __name__ == "__main__":
    main()
