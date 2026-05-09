import os
import shutil

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


def escanear_pastas(pastas, limite_mb=50):
    arquivos_grandes = []

    for pasta in pastas:
        for raiz, diretorios, arquivos in os.walk(pasta):
            for arquivo in arquivos:
                caminho_arquivo = os.path.join(raiz, arquivo)

                try:
                    tamanho_arquivo = os.path.getsize(caminho_arquivo)
                    tamanho_mb = tamanho_arquivo / (1024**2)

                    if tamanho_mb > limite_mb:
                        arquivos_grandes.append({
                            "nome": arquivo,
                            "caminho": caminho_arquivo,
                            "tamanho_mb": tamanho_mb,
                            "risco": classificar_arquivo(caminho_arquivo),
                        })

                except:
                    pass

    arquivos_grandes.sort(
        key=lambda arquivo: arquivo["tamanho_mb"],
        reverse=True
    )

    return arquivos_grandes


def obter_espaco_disco():
    total, usado, livre = shutil.disk_usage("C:/")

    return {
        "total_gb": total / (1024**3),
        "usado_gb": usado / (1024**3),
        "livre_gb": livre / (1024**3),
    }


def obter_pastas_scan_rapido():
    usuario = os.getlogin()

    return [
        f"C:/Users/{usuario}/AppData/Local",
        f"C:/Users/{usuario}/AppData/Roaming",
        "C:/Windows/Temp",
    ]