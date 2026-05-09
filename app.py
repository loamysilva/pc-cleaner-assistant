import tkinter as tk
from cleaner_core import escanear_pastas, obter_espaco_disco, obter_pastas_scan_rapido
import threading
arquivos_encontrados = []
from send2trash import send2trash
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import os
import subprocess


EXTENSOES_PROTEGIDAS = [".dll", ".sys", ".exe", ".msi"]

PASTAS_PROTEGIDAS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData"
]


janela = tk.Tk()
janela.title("PC Cleaner Assistant")
janela.geometry("1000x800")
janela.configure(bg="#09090b")

titulo = tk.Label(
    janela,
    text="PC Cleaner Assistant",
    font=("Arial", 24, "bold"),
    fg="white",
    bg="#09090b"
)

titulo.pack(pady=20)

subtitulo = tk.Label(
    janela,
    text="Limpeza segura, análise de arquivos pesados e logs automáticos.",
    font=("Arial", 12),
    fg="#a1a1aa",
    bg="#09090b"
)

subtitulo.pack()

def escolher_pasta():
    pasta = filedialog.askdirectory()

    if not pasta:
        return

    botao.config(state="disabled")
    botao_limpar.config(state="disabled")
    barra_progresso["value"] = 0

    thread = threading.Thread(
        target=lambda: executar_scan_personalizado(pasta),
        daemon=True
    )
    thread.start()

def arquivo_pode_ser_limpo(caminho, risco):
    caminho_normalizado = os.path.normpath(caminho).lower()

    if risco != "SEGURO":
        return False

    extensao = os.path.splitext(caminho_normalizado)[1]

    if extensao in EXTENSOES_PROTEGIDAS:
        return False

    for pasta in PASTAS_PROTEGIDAS:
        if caminho_normalizado.startswith(pasta.lower()):
            return False

    return True

def abrir_pasta_arquivo(event):
    item_selecionado = tabela.focus()

    if not item_selecionado:
        return

    valores = tabela.item(item_selecionado, "values")

    if not valores:
        return

    caminho = valores[3]
    caminho = os.path.normpath(caminho)

    print(caminho)

    if os.path.exists(caminho):
        subprocess.Popen(f'explorer /select,"{caminho}"')

    else:
        pasta = os.path.dirname(caminho)

        if os.path.exists(pasta):
            subprocess.Popen(["explorer", pasta])

            status_label.config(
                text=f"Arquivo não encontrado. Abrindo pasta: {pasta}"
            )

        else:
            status_label.config(
                text=f"Caminho não encontrado: {caminho}"
            )

def executar_scan():

    global arquivos_encontrados


    for item in tabela.get_children():
        tabela.delete(item)

    status_label.config(text="Iniciando scan...")

    espaco = obter_espaco_disco()


    pastas = obter_pastas_scan_rapido()

    status_label.config(text="Escaneando pastas...")

    arquivos = escanear_pastas(pastas)

    arquivos.sort(
    key=lambda x: x["tamanho_mb"],
    reverse=True
)

    total_para_mostrar = min(len(arquivos), 20)
    barra_progresso["maximum"] = total_para_mostrar
    barra_progresso["value"] = 0

    arquivos_encontrados = arquivos

    total_seguro_mb = 0

    for arquivo in arquivos:
        if arquivo["risco"] == "SEGURO":
            total_seguro_mb += arquivo["tamanho_mb"]



    for index, arquivo in enumerate(arquivos[:20], start=1):

        if arquivo["risco"] == "SEGURO":
            tag = "seguro"

        elif arquivo["risco"] == "CUIDADO":
            tag = "cuidado"

        else:
            tag = "nao_apagar"

        tabela.insert(
            "",
            tk.END,
            values=(
                arquivo["nome"],
                f"{arquivo['tamanho_mb']:.2f}",
                arquivo["risco"],
                arquivo["caminho"]
            ),
            tags=(tag,)
        )

        barra_progresso["value"] = index
        status_label.config(text=f"Carregando tabela: {index}/{total_para_mostrar}")



    total_seguros = sum(
        1 for arquivo in arquivos
        if arquivo["risco"] == "SEGURO"
    )

    status_label.config(
        text=f"Scan finalizado: {len(arquivos)} arquivos | "
            f"Seguros: {total_seguros} | "
            f"Recuperável: {total_seguro_mb / 1024:.2f} GB"
    )

    barra_progresso["value"] = total_para_mostrar
    botao.config(state="normal")
    botao_limpar.config(state="normal")
    botao_limpar.config(state="normal")
    botao_limpar_selecionados.config(state="normal")
    botao_exportar.config(state="normal")

def escanear():
    botao.config(state="disabled")
    botao_limpar.config(state="disabled")
    botao_limpar_selecionados.config(state="disabled")

    barra_progresso["value"] = 0

    thread = threading.Thread(target=executar_scan, daemon=True)
    thread.start()

def exportar_relatorio():
    if not arquivos_encontrados:
        status_label.config(text="Nenhum scan disponível para exportar.")
        return

    os.makedirs("logs", exist_ok=True)

    nome_arquivo = "logs/relatorio_scan.txt"

    with open(nome_arquivo, "w", encoding="utf-8") as arquivo_log:
        arquivo_log.write("PC Cleaner Assistant - Relatório de Scan\n")
        arquivo_log.write("=" * 50 + "\n\n")

        for arquivo in arquivos_encontrados:
            arquivo_log.write(f"Nome: {arquivo['nome']}\n")
            arquivo_log.write(f"Tamanho: {arquivo['tamanho_mb']:.2f} MB\n")
            arquivo_log.write(f"Risco: {arquivo['risco']}\n")
            arquivo_log.write(f"Caminho: {arquivo['caminho']}\n")
            arquivo_log.write("-" * 50 + "\n")

    status_label.config(text=f"Relatório exportado: {nome_arquivo}")

def executar_scan_personalizado():
    pasta = filedialog.askdirectory()

    if not pasta:
        return

    status_label.config(text=f"Escaneando: {pasta}")

    global arquivos_encontrados

    for item in tabela.get_children():
        tabela.delete(item)

    arquivos = escanear_pastas([pasta])

    arquivos.sort(
        key=lambda x: x["tamanho_mb"],
        reverse=True
    )

    arquivos_encontrados = arquivos

    total_seguro_mb = 0

    for arquivo in arquivos:
        if arquivo["risco"] == "SEGURO":
            total_seguro_mb += arquivo["tamanho_mb"]

    barra_progresso["maximum"] = len(arquivos)
    barra_progresso["value"] = 0

    for index, arquivo in enumerate(arquivos, start=1):

        tag = arquivo["risco"]

        tabela.insert(
            "",
            tk.END,
            values=(
                arquivo["nome"],
                f"{arquivo['tamanho_mb']:.2f}",
                arquivo["risco"],
                arquivo["caminho"]
            ),
            tags=(tag,)
        )

        barra_progresso["value"] = index

    total_seguros = sum(
        1 for arquivo in arquivos
        if arquivo["risco"] == "SEGURO"
    )

    status_label.config(
        text=f"Scan personalizado: {len(arquivos)} arquivos | "
             f"Seguros: {total_seguros} | "
             f"Recuperável: {total_seguro_mb / 1024:.2f} GB"
    )

    botao_limpar.config(state="normal")
    botao_limpar_selecionados.config(state="normal")
    botao_exportar.config(state="normal")



def limpar_seguros():
    if not arquivos_encontrados:
        status_label.config(text="Nenhum scan foi feito ainda.")
        return

    arquivos_seguros = [
        arquivo for arquivo in arquivos_encontrados
        if arquivo_pode_ser_limpo(arquivo["caminho"], arquivo["risco"])
    ]

    if not arquivos_seguros:
        status_label.config(text="Nenhum arquivo seguro encontrado.")
        return

    confirmar = messagebox.askyesno(
        "Confirmar limpeza",
        f"Foram encontrados {len(arquivos_seguros)} arquivos seguros.\n\n"
        "Deseja mover esses arquivos para a lixeira?"
    )

    if not confirmar:
        status_label.config(text="Limpeza cancelada.")
        return

    botao.config(state="disabled")
    botao_limpar.config(state="disabled")

    status_label.config(text="Iniciando limpeza segura...")

    def tarefa_limpeza():
        apagados = 0
        erros = 0

        for arquivo in arquivos_seguros:
            try:
                send2trash(arquivo["caminho"])
                apagados += 1
                status_label.config(text=f"Limpando: {arquivo['nome']}")
            except Exception as erro:
                erros += 1
                status_label.config(text=f"Erro ao mover: {arquivo['nome']}")



        botao.config(state="normal")
        botao_limpar.config(state="normal")

    threading.Thread(target=tarefa_limpeza, daemon=True).start()

    status_label.config(
    text=f"Limpeza finalizada: {apagados} arquivos enviados para lixeira."
)

def aplicar_filtro():
    filtro = filtro_risco.get()

    for item in tabela.get_children():
        tabela.delete(item)

    total_para_mostrar = 0

    for arquivo in arquivos_encontrados[:20]:
        if filtro != "TODOS" and arquivo["risco"] != filtro:
            continue

        if arquivo["risco"] == "SEGURO":
            tag = "seguro"
        elif arquivo["risco"] == "CUIDADO":
            tag = "cuidado"
        else:
            tag = "nao_apagar"

        tabela.insert(
            "",
            tk.END,
            values=(
                arquivo["nome"],
                f"{arquivo['tamanho_mb']:.2f}",
                arquivo["risco"],
                arquivo["caminho"]
            ),
            tags=(tag,)
        )

        total_para_mostrar += 1

    status_label.config(
        text=f"Filtro aplicado: {filtro} | {total_para_mostrar} arquivo(s) exibido(s)."
    )

def limpar_selecionados():
    itens = tabela.selection()

    if not itens:
        status_label.config(text="Nenhum arquivo selecionado.")
        return

    confirmar = messagebox.askyesno(
        "Confirmar limpeza",
        f"Deseja mover {len(itens)} arquivo(s) selecionado(s) para a lixeira?"
    )

    if not confirmar:
        status_label.config(text="Limpeza cancelada.")
        return

    apagados = 0
    erros = 0

    for item in itens:
        valores = tabela.item(item, "values")
        caminho = valores[3]
        risco = valores[2]

        if not arquivo_pode_ser_limpo(caminho, risco):
            erros += 1
            continue

        caminho = os.path.normpath(caminho)

        if caminho.startswith("\\\\?\\"):
            caminho = caminho[4:]

        try:
            send2trash(caminho)
            apagados += 1
            tabela.delete(item)

        except Exception as erro:
            erros += 1
            print(erro)

    status_label.config(
        text=f"Limpeza selecionada finalizada: {apagados} enviados, {erros} erros."
    )

frame_botoes = tk.Frame(janela, bg="#09090b")

frame_botoes.pack(pady=20)

filtro_risco = tk.StringVar(value="TODOS")


frame_filtro = tk.Frame(janela, bg="#09090b")
frame_filtro.pack(pady=5)

label_filtro = tk.Label(
    frame_filtro,
    text="Filtrar por risco:",
    font=("Arial", 11),
    fg="white",
    bg="#09090b"
)

label_filtro.pack(side=tk.LEFT, padx=5)

combo_filtro = ttk.Combobox(
    frame_filtro,
    textvariable=filtro_risco,
    values=["TODOS", "SEGURO", "CUIDADO", "NÃO APAGAR"],
    state="readonly",
    width=15
)

combo_filtro.pack(side=tk.LEFT, padx=5)

botao_filtro = tk.Button(
    frame_filtro,
    text="Aplicar filtro",
    command=aplicar_filtro,
    font=("Arial", 10, "bold"),
    bg="#52525b",
    fg="white",
    padx=10,
    pady=5
)

botao_exportar = tk.Button(
    frame_botoes,
    text="Exportar relatório",
    command=exportar_relatorio,
    font=("Arial", 12, "bold"),
    bg="#52525b",
    fg="white",
    padx=20,
    pady=10,
    state="disabled"
)

botao_exportar.pack(side=tk.LEFT, padx=10)

botao_filtro.pack(side=tk.LEFT, padx=5)


frame_botoes = tk.Frame(janela, bg="#09090b")
frame_botoes.pack(pady=10)


botao_limpar_selecionados = tk.Button(
    frame_botoes,
    text="Limpar selecionados",
    command=limpar_selecionados,
    font=("Arial", 12, "bold"),
    bg="#f97316",
    fg="white",
    padx=20,
    pady=10,
    state="disabled"
)

botao_limpar_selecionados.pack(side=tk.LEFT, padx=10)


botao = tk.Button(
    frame_botoes,
    text="Scan rápido",
    command=escanear,
    font=("Arial", 12, "bold"),
    bg="#6366f1",
    fg="white",
    padx=20,
    pady=10
)

botao.pack(side=tk.LEFT, padx=10)

botao_limpar = tk.Button(
    frame_botoes,
    text="Limpar arquivos seguros",
    command=limpar_seguros,
    font=("Arial", 12, "bold"),
    bg="#22c55e",
    fg="white",
    padx=20,
    pady=10,
    state="disabled"
)

botao_pasta = tk.Button(
    frame_botoes,
    text="Escolher pasta",
    command=executar_scan_personalizado,
    font=("Arial", 12, "bold"),
    bg="#0ea5e9",
    fg="white",
    padx=20,
    pady=10
)

botao_pasta.pack(side=tk.LEFT, padx=10)

botao_limpar.pack(side=tk.LEFT, padx=10)

barra_progresso = ttk.Progressbar(
    janela,
    orient="horizontal",
    length=500,
    mode="determinate"
)

barra_progresso.pack(pady=8)

status_label = tk.Label(
    janela,
    text="Pronto para escanear.",
    font=("Arial", 11),
    fg="#d4d4d8",
    bg="#09090b"
)

status_label.pack(pady=5)

frame_resultado = tk.Frame(janela, bg="#09090b")
frame_resultado.pack(pady=20, fill="both", expand=True)

tabela = ttk.Treeview(
    frame_resultado,
    columns=("nome", "tamanho", "risco", "caminho"),
    show="headings",
    height=18,
    selectmode="extended"
)

tabela.heading("nome", text="Arquivo")
tabela.heading("tamanho", text="Tamanho MB")
tabela.heading("risco", text="Status")
tabela.heading("caminho", text="Caminho")

tabela.column("nome", width=650)
tabela.column("tamanho", width=120, anchor="center")
tabela.column("risco", width=120, anchor="center")

tabela.column("caminho", width=0, stretch=False)
tabela["displaycolumns"] = ("nome", "tamanho", "risco")

tabela.tag_configure("seguro", foreground="#22c55e")
tabela.tag_configure("cuidado", foreground="#eab308")
tabela.tag_configure("nao_apagar", foreground="#ef4444")


tabela.bind("<Double-1>", abrir_pasta_arquivo)


scroll_tabela = ttk.Scrollbar(
    frame_resultado,
    orient="vertical",
    command=tabela.yview
)

tabela.configure(yscrollcommand=scroll_tabela.set)

scroll_tabela.pack(side=tk.RIGHT, fill="y")

tabela.pack(
    side=tk.LEFT,
    fill="both",
    expand=True,
    padx=20,
    pady=20
)


janela.mainloop()