import os
import time
from datetime import datetime
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, filedialog
from tkinter.ttk import Label, OptionMenu
from tkinter import messagebox
def organizar_arquivo(diretorio,ano):
    os.chdir(diretorio)
    count = 0
    lista_arquivos =[arquivo.lower() for arquivo in os.listdir() if os.path.isfile(arquivo)]
    lista_tipos = {tipo.split(".")[-1] for tipo in lista_arquivos}
    for tipo in lista_tipos:
        if os.path.exists(tipo):
            pass
        else:
            os.mkdir(tipo)
    for arquivo in lista_arquivos:
        pasta_destino = arquivo.split(".")[-1]
        timestamp = os.path.getmtime(arquivo)
        dataarquivo = datetime.fromtimestamp(timestamp).strftime('%Y')
        if(int(dataarquivo) < ano):
            os.remove(arquivo)
            continue
        de = os.path.join(os.getcwd(),arquivo)
        para = os.path.join(os.getcwd(), pasta_destino, arquivo)
        os.replace(de,para)
        count+= 1
        
    messagebox.showinfo("Organizador","Arquivos organizados com sucesso!")

def selecionar_arquivo(ano):
       folder_selected = filedialog.askdirectory()
       organizar_arquivo(folder_selected,int(ano))
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
    text="Insira o ano que deseja filtrar",
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


entry_1 = Entry(bd=1, bg="#FFFFFF", fg="#000716", highlightthickness=0)
entry_1.place(x=75.0, y=117.0, width=163.0, height=25.0)

button_1 = Button(
    #image=button_image_1,
    text="Selecionar",
    borderwidth=0,
    highlightthickness=0,
    command=lambda: selecionar_arquivo(entry_1.get()),
    relief="flat",
)

button_2 = Button(
    #image=button_image_1,
    text="Selecionar",
    borderwidth=0,
    highlightthickness=0,
    command=lambda: selecionar_arquivo(),
    relief="flat",
)
button_1.place(x=254.0, y=117.0, width=90.0, height=27.0)

window.resizable(False, False)
window.mainloop()