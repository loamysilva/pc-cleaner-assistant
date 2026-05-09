import os
import shutil
from send2trash import send2trash
from datetime import datetime


usuario = os.getlogin()

pastas_scan_rapido = [
    f"C:/Users/{usuario}/AppData/Local",
    f"C:/Users/{usuario}/AppData/Roaming",
    "C:/Windows/Temp",
]

pastas_proibidas = [
    "C:/WINDOWS/System32",
    "C:/WINDOWS/WinSxS",
    "C:/WINDOWS/SysWOW64",
    "C:/Program Files",
    "C:/Program Files (x86)",
    "C:/ProgramData"
]

print("=== PC Cleaner Assistant ===")
print()
print(f"Usuário detectado: {usuario}")
print()

total, usado, livre = shutil.disk_usage("C:/")

print(f"Espaço total: {total / (1024**3):.2f} GB")
print(f"Espaço usado: {usado / (1024**3):.2f} GB")
print(f"Espaço livre: {livre / (1024**3):.2f} GB")
print()

print("Escolha o tipo de scan:")
print("1 - Scan rápido recomendado")
print("2 - Scan completo do disco C:")
print("3 - Escolher pasta ou disco")
print()

opcao = input("Opção: ")

if opcao == "1":
    pastas = pastas_scan_rapido

elif opcao == "2":
    pastas = ["C:/"]

elif opcao == "3":
    caminho_personalizado = input("Digite o caminho, exemplo D:/ ou C:/Users/seu_nome/Downloads: ")
    pastas = [caminho_personalizado]

else:
    print("Opção inválida. Usando scan rápido.")
    pastas = pastas_scan_rapido

tipo_scan = opcao

print()

os.makedirs("logs", exist_ok=True)

data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
caminho_log = f"logs/cleaner-{data_atual}.txt"

log = []

def classificar_arquivo(caminho):
    caminho_minusculo = caminho.lower()

    if "temp" in caminho_minusculo:
        return "SEGURO"
    if "dxcache" in caminho_minusculo:
        return "SEGURO"
    if "dxccache" in caminho_minusculo:
        return "SEGURO"
    if "dxc_cache" in caminho_minusculo:
        return "SEGURO"
    if "updater" in caminho_minusculo:
        return "CUIDADO"
    if "programs" in caminho_minusculo:
        return "NÃO APAGAR"
    if "celestial launcher" in caminho_minusculo:
        return "CUIDADO"

    return "CUIDADO"

arquivos_grandes = []

for numero_pasta, pasta in enumerate(pastas, start=1):
    print(f"Escaneando pasta {numero_pasta}/{len(pastas)}:")
    print(pasta)
    print()

    arquivos_lidos = 0

    for raiz, diretorios, arquivos in os.walk(pasta):

        raiz_normalizada = raiz.replace("\\", "/")

        if any(raiz_normalizada.startswith(pastas_proibida) for pastas_proibida in pastas_proibidas):
            continue


        for arquivo in arquivos:
            arquivos_lidos += 1

            if arquivos_lidos % 1000 == 0:
                print(f"{arquivos_lidos} arquivos analisados...")


            caminho_arquivo = os.path.join(raiz, arquivo)

            try:
                tamanho_arquivo = os.path.getsize(caminho_arquivo)
                tamanho_mb = tamanho_arquivo / (1024**2)

                if tamanho_mb > 50:
                    arquivos_grandes.append({
                        "nome": arquivo,
                        "caminho": caminho_arquivo,
                        "tamanho_mb": tamanho_mb,
                        "risco": classificar_arquivo(caminho_arquivo),
                    })

            except:
                pass

print()
print("=== Top 20 maiores arquivos encontrados ===")
print()

arquivos_grandes.sort(
    key=lambda arquivo: arquivo["tamanho_mb"],
    reverse=True
)

total_seguro_mb = 0

for arquivo in arquivos_grandes:
    if arquivo["risco"] == "SEGURO":
        total_seguro_mb += arquivo["tamanho_mb"]

print(f"Espaço potencialmente liberável com arquivos seguros: {total_seguro_mb / 1024:.2f} GB")
log.append("=== PC Cleaner Assistant ===")
log.append(f"Data: {data_atual}")
log.append(f"Espaço total: {total / (1024**3):.2f} GB")
log.append(f"Espaço usado: {usado / (1024**3):.2f} GB")
log.append(f"Espaço livre: {livre / (1024**3):.2f} GB")
log.append(f"Espaço potencialmente liberável: {total_seguro_mb / 1024:.2f} GB")
log.append(f"Tipo de scan escolhido: {tipo_scan}")
log.append("Pastas escaneadas:")

for pasta in pastas:
    log.append(f"- {pasta}")

log.append(f"Quantidade de arquivos grandes encontrados: {len(arquivos_grandes)}")
log.append("")
log.append("=== Arquivos encontrados ===")
print()

for index, arquivo in enumerate(arquivos_grandes[:20], start=1):
    print(f"{index}. {arquivo['nome']}")
    print(f"   Tamanho: {arquivo['tamanho_mb']:.2f} MB")
    print(f"   Status: [{arquivo['risco']}]")
    print(f"   Caminho: {arquivo['caminho']}")
    print()
    log.append(f"{index}. {arquivo['nome']}")
    log.append(f"  Caminho: {arquivo['tamanho_mb']:.2f} MB")
    log.append(f"  Status: {arquivo['risco']}")
    log.append(f"  Caminho: {arquivo['caminho']}")
    log.append("")


if total_seguro_mb > 0:

    resposta = input("Deseja mover arquivos SEGUROS para a lixeira? (s/n): ")

    arquivos_apagados = 0
    if resposta.lower() == "s":

        for arquivo in arquivos_grandes:

            if arquivo["risco"] == "SEGURO":

                try:
                    send2trash(arquivo["caminho"])

                    print(f"Movido para lixeira:")
                    print(arquivo["caminho"])
                    print()

                    arquivos_apagados += 1

                except:
                        print(f"Erro ao mover:")
                        print(arquivo["caminho"])
                        print()

    else:
        print("Nenhum arquivo foi movido.")

    print(f"{arquivos_apagados} arquivos enviados para lixeira.")
    log.append("")
    log.append("=== Resultado da limpeza ===")
    log.append(f"Arquivos enviados para lixeira: {arquivos_apagados}")

else:
    print("Nenhum arquivo seguro encontrado para limpeza.")
    log.append("")
    log.append("=== Resultado da limpeza ===")
    log.append("Nenhum arquivo seguro encontrado para limpeza.")



resposta_logs = input("Deseja apagar logs antigos? (s/n): ")

if resposta_logs.lower() == "s":
    logs_apagados = 0

    for nome_arquivo in os.listdir("logs"):
        caminho_arquivo_log = os.path.join("logs", nome_arquivo)

        try:
            if os.path.isfile(caminho_arquivo_log) and caminho_arquivo_log != caminho_log:
                send2trash(caminho_arquivo_log)
                logs_apagados += 1

        except:
            pass

    print(f"{logs_apagados} logs antigos enviados para a lixeira.")
    log.append(f"Logs antigos enviados para a lixeira: {logs_apagados}")
else:
    print("Logs antigos mantidos.")
    log.append("Logs antigos mantidos.")

with open(caminho_log, "w", encoding="utf-8") as arquivo_log:
    arquivo_log.write("\n".join(log))

print(f"Log criado em: {caminho_log}")
