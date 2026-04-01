import customtkinter as ctk
import requests
import os
import re
import winreg
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import threading

ctk.set_appearance_mode("dark")


# =========================
# FUNÇÕES BACKEND
# =========================

def log(msg):
    textbox.insert("end", msg + "\n")
    textbox.see("end")
    app.update_idletasks()

def get_steam_path():
    paths = [
        r"SOFTWARE\WOW6432Node\Valve\Steam",
        r"SOFTWARE\Valve\Steam"
    ]

    for path in paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            value, _ = winreg.QueryValueEx(key, "InstallPath")
            return value
        except:
            continue
    return None


def get_depots(lua_path):
    depots = set()
    with open(lua_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = re.search(r'addappid\((\d+),', line)
            if match:
                depots.add(match.group(1))
    return list(depots)


def get_app_info(appid):
    try:
        return requests.get(f"https://api.steamcmd.net/v1/info/{appid}").json()
    except:
        return None


def get_manifest(appinfo, appid, depot):
    try:
        return appinfo["data"][appid]["depots"][depot]["manifests"]["public"]["gid"]
    except:
        return None


def download_manifest(depot, manifest, path):
    url = f"https://raw.githubusercontent.com/qwe213312/k25FCdfEOoEJ42S6/main/{depot}_{manifest}.manifest"
    file_path = os.path.join(path, f"{depot}_{manifest}.manifest")

    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(r.content)
            return True
    except:
        return False

    return False


# =========================
# EXECUÇÃO COM PROGRESSO
# =========================

def executar():
    threading.Thread(target=run).start()

def run():
    textbox.delete("1.0", "end")
    progress.set(0)

    appid = entry_appid.get()

    if not appid.isdigit():
        messagebox.showerror("Erro", "AppID inválido")
        return

    steam = get_steam_path()
    if not steam:
        log("❌ Steam não encontrado")
        return

    log(f"✔ Steam encontrado")

    lua_path = os.path.join(steam, f"config/stplug-in/{appid}.lua")

    if not os.path.exists(lua_path):
        log("❌ Lua não encontrado")
        return

    log("✔ Lua encontrado")

    depots = get_depots(lua_path)
    total = len(depots)

    log(f"✔ {total} depots encontrados")

    appinfo = get_app_info(appid)
    if not appinfo:
        log("❌ Erro API")
        return

    output = os.path.join(steam, "depotcache")
    os.makedirs(output, exist_ok=True)

    sucesso = 0

    for i, d in enumerate(depots):
        manifest = get_manifest(appinfo, appid, d)

        if not manifest:
            log(f"⚠ {d} sem manifest")
            continue

        log(f"⬇ Baixando {d}...")

        if download_manifest(d, manifest, output):
            sucesso += 1
            log(f"✔ {d}")
        else:
            log(f"❌ {d}")

        # Atualiza barra
        progress.set((i + 1) / total)

    log(f"\n✅ Finalizado {sucesso}/{total}")


# =========================
# UI
# =========================

app = ctk.CTk()
app.geometry("900x600")
app.title("Steam Manifest Downloader PRO")

# ===== BACKGROUND =====
img = Image.open("fundo.jpg")
img = img.resize((900, 600))
img = img.filter(ImageFilter.GaussianBlur(8))  # desfoca
bg = ImageTk.PhotoImage(img)

bg_label = ctk.CTkLabel(app, image=bg, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ===== CARD CENTRAL =====
card = ctk.CTkFrame(app, corner_radius=20, fg_color="#1a1a1a")
card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

title = ctk.CTkLabel(card, text="Steam Manifest Downloader", font=("Arial", 20, "bold"))
title.pack(pady=15)

entry_appid = ctk.CTkEntry(card, placeholder_text="Digite o AppID")
entry_appid.pack(pady=10, padx=20, fill="x")

btn = ctk.CTkButton(card, text="🚀 Baixar Manifests", command=executar)
btn.pack(pady=10)

# ===== PROGRESS BAR =====
progress = ctk.CTkProgressBar(card)
progress.pack(pady=10, padx=20, fill="x")
progress.set(0)

# ===== LOG =====
textbox = ctk.CTkTextbox(card)
textbox.pack(padx=20, pady=10, fill="both", expand=True)



app.mainloop()