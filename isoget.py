#!/usr/bin/env python3
"""
  ██╗███████╗ ██████╗  ██████╗ ███████╗████████╗
  ██║██╔════╝██╔═══██╗██╔════╝ ██╔════╝╚══██╔══╝
  ██║███████╗██║   ██║██║  ███╗█████╗     ██║
  ██║╚════██║██║   ██║██║   ██║██╔══╝     ██║
  ██║███████║╚██████╔╝╚██████╔╝███████╗   ██║
  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝
  ISO Downloader  ·  SyncX Tools  ·  BadOctop4s
"""

import os, sys, platform, subprocess, shutil, time, threading
import urllib.request, urllib.error
from pathlib import Path

IS_WINDOWS = platform.system() == "Windows"

# ─── ANSI Colors ──────────────────────────────────────────────────────────────
if IS_WINDOWS:
    os.system("color")   # Habilita ANSI no cmd/PowerShell

R  = '\033[0m'
BD = '\033[1m'
DM = '\033[2m'
CY = '\033[96m'
BL = '\033[94m'
GR = '\033[92m'
YL = '\033[93m'
RD = '\033[91m'
MG = '\033[95m'
WH = '\033[97m'
BB = '\033[44m'   # bg azul

# ─── Cross-platform getch (setas do teclado) ───────────────────────────────────
if IS_WINDOWS:
    import msvcrt

    def getch():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):        # Prefixo de tecla especial
            ch2 = msvcrt.getch()
            return {b'H': 'UP', b'P': 'DOWN', b'K': 'LEFT', b'M': 'RIGHT'}.get(ch2)
        if ch == b'\r':   return 'ENTER'
        if ch == b'\x03': raise KeyboardInterrupt
        if ch == b'\x1b': return 'ESC'
        return ch.decode('utf-8', errors='ignore')

else:
    import tty, termios, select

    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = os.read(fd, 1)
            if ch == b'\x1b':
                # Verifica se é uma sequência de escape (seta) ou ESC sozinho
                r, _, _ = select.select([fd], [], [], 0.05)
                if r:
                    ch2 = os.read(fd, 1)   # deve ser b'['
                    ch3 = os.read(fd, 1)
                    return {'A': 'UP', 'B': 'DOWN', 'C': 'RIGHT', 'D': 'LEFT'}.get(
                        ch3.decode(), 'ESC'
                    )
                return 'ESC'
            if ch in (b'\r', b'\n'): return 'ENTER'
            if ch == b'\x03': raise KeyboardInterrupt
            return ch.decode('utf-8', errors='ignore')
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ─── Helpers de terminal ───────────────────────────────────────────────────────
def clear():
    os.system('cls' if IS_WINDOWS else 'clear')

def banner():
    print(f"""{CY}{BD}
  ██╗███████╗ ██████╗  ██████╗ ███████╗████████╗
  ██║██╔════╝██╔═══██╗██╔════╝ ██╔════╝╚══██╔══╝
  ██║███████╗██║   ██║██║  ███╗█████╗     ██║
  ██║╚════██║██║   ██║██║   ██║██╔══╝     ██║
  ██║███████║╚██████╔╝╚██████╔╝███████╗   ██║
  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝{R}
{DM}        ISO Downloader  ·  SyncX Tools  ·  BadOctop4s{R}
""")

def sep(label=""):
    w = 54
    if label:
        pad = (w - len(label) - 2) // 2
        print(f"  {DM}{'─'*pad} {label} {'─'*pad}{R}")
    else:
        print(f"  {DM}{'─'*w}{R}")

def pause(msg=f"  Pressione Enter para continuar..."):
    print(f"\n{DM}{msg}{R} ", end="", flush=True)
    input()


# ─── Menu interativo com setas ─────────────────────────────────────────────────
def menu(title, options, breadcrumb="", allow_back=True):
    """Retorna o índice escolhido, ou -1 se ESC/Voltar."""
    idx = 0
    while True:
        clear()
        banner()
        if breadcrumb:
            print(f"  {DM}› {breadcrumb}{R}\n")
        print(f"  {BD}{WH}{title}{R}\n")
        for i, opt in enumerate(options):
            if i == idx:
                print(f"  {BB}{WH}{BD}  ›  {opt:<46}{R}")
            else:
                print(f"     {DM}{opt}{R}")
        footer = "↑↓ navegar   Enter selecionar"
        if allow_back:
            footer += "   Esc voltar"
        print(f"\n  {DM}{footer}{R}\n")
        k = getch()
        if   k == 'UP':    idx = (idx - 1) % len(options)
        elif k == 'DOWN':  idx = (idx + 1) % len(options)
        elif k == 'ENTER': return idx
        elif k == 'ESC' and allow_back: return -1


# ─── Banco de ISOs ─────────────────────────────────────────────────────────────
# Windows: url=None → abre navegador na página oficial
# Linux:   url direto → download automático

WINDOWS_ISOS = {
    "Windows 7 SP1 (64-bit)": {
        "url":  None,
        "page": "https://www.microsoft.com/en-us/software-download/windows7",
        "note": "Requer conta Microsoft. Abrindo navegador...",
    },
    "Windows 8.1 (64-bit)": {
        "url":  None,
        "page": "https://www.microsoft.com/en-us/software-download/windows8ISO",
        "note": "Requer conta Microsoft. Abrindo navegador...",
    },
    "Windows 10 22H2 (64-bit)": {
        "url":      "https://software.download.prss.microsoft.com/dbazure/Win10_22H2_Portuguese_x64.iso",
        "filename": "Win10_22H2_Portuguese_x64.iso",
        "note":     "Download direto ~5.8 GB",
    },
    "Windows 11 24H2 (64-bit)": {
        "url":  None,
        "page": "https://www.microsoft.com/software-download/windows11",
        "note": "Abrindo página oficial da Microsoft...",
    },
}

LINUX_ISOS = {
    "Ubuntu 24.04 LTS": {
        "GNOME (Padrão)":          "https://releases.ubuntu.com/24.04/ubuntu-24.04.2-desktop-amd64.iso",
        "KDE Plasma (Kubuntu)":    "https://cdimage.ubuntu.com/kubuntu/releases/24.04/release/kubuntu-24.04.2-desktop-amd64.iso",
        "XFCE (Xubuntu)":          "https://cdimage.ubuntu.com/xubuntu/releases/24.04/release/xubuntu-24.04.2-desktop-amd64.iso",
        "LXQt (Lubuntu)":          "https://cdimage.ubuntu.com/lubuntu/releases/24.04/release/lubuntu-24.04.2-desktop-amd64.iso",
        "MATE (Ubuntu MATE)":      "https://releases.ubuntu-mate.org/24.04/amd64/ubuntu-mate-24.04.2-desktop-amd64.iso",
        "Budgie (Ubuntu Budgie)":  "https://cdimage.ubuntu.com/ubuntu-budgie/releases/24.04/release/ubuntu-budgie-24.04.2-desktop-amd64.iso",
    },
    "Debian 12 Bookworm": {
        "GNOME":     "https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/debian-live-12.10.0-amd64-gnome.iso",
        "KDE Plasma":"https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/debian-live-12.10.0-amd64-kde.iso",
        "XFCE":      "https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/debian-live-12.10.0-amd64-xfce.iso",
        "LXDE":      "https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/debian-live-12.10.0-amd64-lxde.iso",
        "MATE":      "https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/debian-live-12.10.0-amd64-mate.iso",
        "Cinnamon":  "https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/debian-live-12.10.0-amd64-cinnamon.iso",
    },
    "Fedora 41 Workstation": {
        "GNOME":       "https://download.fedoraproject.org/pub/fedora/linux/releases/41/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-41-1.4.iso",
        "KDE Plasma":  "https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-KDE-Live-x86_64-41-1.4.iso",
        "XFCE":        "https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-Xfce-Live-x86_64-41-1.4.iso",
        "MATE+Compiz": "https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-MATE_Compiz-Live-x86_64-41-1.4.iso",
        "i3 (tiling)": "https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-i3-Live-x86_64-41-1.4.iso",
        "Cinnamon":    "https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-Cinnamon-Live-x86_64-41-1.4.iso",
    },
    "Linux Mint 22": {
        "Cinnamon": "https://mirrors.edge.kernel.org/linuxmint/stable/22/linuxmint-22-cinnamon-64bit.iso",
        "MATE":     "https://mirrors.edge.kernel.org/linuxmint/stable/22/linuxmint-22-mate-64bit.iso",
        "XFCE":     "https://mirrors.edge.kernel.org/linuxmint/stable/22/linuxmint-22-xfce-64bit.iso",
    },
    "Manjaro": {
        "KDE Plasma": "https://download.manjaro.org/kde/24.2.1/manjaro-kde-24.2.1-241216-linux612.iso",
        "GNOME":      "https://download.manjaro.org/gnome/24.2.1/manjaro-gnome-24.2.1-241216-linux612.iso",
        "XFCE":       "https://download.manjaro.org/xfce/24.2.1/manjaro-xfce-24.2.1-241216-linux612.iso",
    },
    "Kali Linux 2024.4": {
        "XFCE (Padrão)": "https://cdimage.kali.org/kali-2024.4/kali-linux-2024.4-live-amd64.iso",
        "GNOME":         "https://cdimage.kali.org/kali-2024.4/kali-linux-2024.4-installer-gnome-amd64.iso",
        "KDE Plasma":    "https://cdimage.kali.org/kali-2024.4/kali-linux-2024.4-installer-kde-amd64.iso",
    },
    "Pop!_OS 22.04": {
        "GNOME (Intel/AMD)": "https://iso.pop-os.org/22.04/amd64/intel/42/pop-os_22.04_amd64_intel_42.iso",
        "GNOME (NVIDIA)":    "https://iso.pop-os.org/22.04/amd64/nvidia/42/pop-os_22.04_amd64_nvidia_42.iso",
    },
    "Arch Linux": {
        "Base (sem DE, instala manual)": "https://mirror.rackspace.com/archlinux/iso/latest/archlinux-x86_64.iso",
    },
    "CachyOS (ARCH BASED)": {
        "CachyOS (ARCH BASED)": "https://cdn77.cachyos.org/ISO/desktop/260426/cachyos-desktop-linux-260426.iso",
    },
    "EndeavourOS": {
        "Galileo Neo (Multi-DE)": "https://mirror.alpix.eu/endeavouros/iso/EndeavourOS_Galileo-Neo-2024.09.22.iso",
    },
    "openSUSE Tumbleweed": {
        "GNOME":      "https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-GNOME-Live-x86_64-Current.iso",
        "KDE Plasma": "https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-KDE-Live-x86_64-Current.iso",
        "XFCE":       "https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-XFCE-Live-x86_64-Current.iso",
    },
    "Zorin OS 17": {
        "GNOME (Core)": "https://mirrors.edge.kernel.org/zorinos/17/Zorin-OS-17.2-Core-64-bit.iso",
        "GNOME (Lite/XFCE)": "https://mirrors.edge.kernel.org/zorinos/17/Zorin-OS-17.2-Lite-64-bit.iso",
    },
}


# ─── Utils de arquivo e download ───────────────────────────────────────────────
def get_downloads_dir():
    """Retorna ~/Downloads de forma correta em todos os sistemas."""
    if IS_WINDOWS:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )
            val, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
            return Path(val)
        except Exception:
            pass
    return Path.home() / "Downloads"

def safe_dirname(name: str) -> str:
    """Remove caracteres inválidos para nome de pasta."""
    for ch in r'\/:*?"<>|':
        name = name.replace(ch, "")
    return name.strip()

def open_folder(path: Path):
    """Abre o explorador de arquivos na pasta dada."""
    path = Path(path)
    if IS_WINDOWS:
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", str(path)])
    else:
        for cmd in ["xdg-open", "nautilus", "dolphin", "thunar", "nemo", "pcmanfm"]:
            if shutil.which(cmd):
                subprocess.Popen([cmd, str(path)])
                return
        print(f"  {YL}Abra manualmente: {path}{R}")

def open_url(url: str):
    import webbrowser
    webbrowser.open(url)

def fmt_size(b: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(b) < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


# ─── Tela de confirmação antes de baixar ──────────────────────────────────────
def confirm_download(label: str, url: str, dest_dir: Path) -> bool:
    filename = url.split("/")[-1]
    clear()
    banner()
    print(f"  {BD}{WH}Confirmar Download{R}\n")
    sep()
    print(f"  {DM}ISO       {R} {CY}{BD}{label}{R}")
    print(f"  {DM}Arquivo   {R} {WH}{filename}{R}")
    print(f"  {DM}Destino   {R} {BL}{dest_dir}{R}")
    print(f"  {DM}URL       {R} {DM}{url[:70]}{'…' if len(url)>70 else ''}{R}")
    sep()
    print(f"\n  {YL}Aviso:{R} ISOs costumam ter entre {BD}1 GB e 6 GB{R}.\n")
    opts = ["  ✔  Baixar agora", "  ✗  Cancelar"]
    ch = menu("", opts, allow_back=False)
    return ch == 0


# ─── Progress bar de download ──────────────────────────────────────────────────
def download_iso(label: str, url: str, dest_dir: Path, filename: str = None):
    if filename is None:
        filename = url.split("/")[-1]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename

    clear()
    banner()
    print(f"  {BD}{WH}Baixando{R}  {CY}{label}{R}\n")
    print(f"  {DM}Arquivo  {R} {WH}{filename}{R}")
    print(f"  {DM}Destino  {R} {BL}{dest_dir}{R}\n")

    downloaded = [0]
    total      = [0]
    done       = [False]
    error      = [None]
    start_time = [time.time()]

    def reporthook(count, block_size, total_size):
        downloaded[0] = count * block_size
        total[0] = total_size

    def progress_loop():
        bar_w  = 38
        spin   = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        s_idx  = 0
        while not done[0]:
            elapsed = time.time() - start_time[0] or 0.001
            dl      = downloaded[0]
            tot     = total[0]
            speed   = dl / elapsed

            if tot > 0:
                pct    = min(dl / tot, 1.0)
                filled = int(bar_w * pct)
                bar    = f"{CY}{'█'*filled}{DM}{'░'*(bar_w-filled)}{R}"
                eta    = int((tot - dl) / speed) if speed > 0 else 0
                line   = (
                    f"\r  [{bar}] {YL}{BD}{pct*100:5.1f}%{R}  "
                    f"{GR}{fmt_size(dl)}{R}/{DM}{fmt_size(tot)}{R}  "
                    f"{MG}{fmt_size(speed)}/s{R}  ETA {DM}{eta}s{R}   "
                )
            else:
                s_idx = (s_idx + 1) % len(spin)
                line  = (
                    f"\r  {CY}{spin[s_idx]}{R} {GR}{fmt_size(dl)}{R} baixados"
                    f"  {MG}{fmt_size(speed)}/s{R}   "
                )
            sys.stdout.write(line)
            sys.stdout.flush()
            time.sleep(0.12)

    t = threading.Thread(target=progress_loop, daemon=True)
    t.start()

    try:
        urllib.request.urlretrieve(url, dest, reporthook)
    except urllib.error.URLError as e:
        error[0] = e
    except KeyboardInterrupt:
        error[0] = "cancelado"
    finally:
        done[0] = True
        t.join(0.5)

    print()  # nova linha após a progress bar

    if error[0]:
        if error[0] == "cancelado":
            print(f"\n  {YL}Download cancelado pelo usuário.{R}")
        else:
            print(f"\n  {RD}{BD}✘  Erro:{R} {error[0]}")
            print(f"  {DM}Verifique sua conexão e tente novamente.{R}")
        if dest.exists():
            dest.unlink(missing_ok=True)
        pause()
        return

    elapsed  = time.time() - start_time[0]
    size_str = fmt_size(dest.stat().st_size)
    avg      = fmt_size(dest.stat().st_size / elapsed) + "/s"

    print(f"\n  {GR}{BD}✔  Download completo!{R}")
    print(f"  {DM}Tempo  {R}{WH}{elapsed:.1f}s{R}  {DM}Tamanho  {R}{WH}{size_str}{R}  {DM}Média  {R}{WH}{avg}{R}")
    print(f"\n  {WH}Abrindo pasta...{R}")
    time.sleep(1.2)
    open_folder(dest_dir)
    pause("  Pressione Enter para voltar ao menu...")


# ─── Fluxos de navegação ───────────────────────────────────────────────────────
def flow_windows():
    versions = list(WINDOWS_ISOS.keys())
    while True:
        choice = menu(
            "Selecione a versão do Windows",
            versions,
            breadcrumb="Início › Windows",
        )
        if choice == -1:
            return

        ver  = versions[choice]
        info = WINDOWS_ISOS[ver]

        if info.get("url"):
            dest_dir = get_downloads_dir() / "ISO" / "Windows"
            label    = ver
            url      = info["url"]
            filename = info.get("filename")
            if confirm_download(label, url, dest_dir):
                download_iso(label, url, dest_dir, filename)
        else:
            # Precisa de navegador
            clear()
            banner()
            print(f"  {BD}{WH}{ver}{R}\n")
            sep()
            print(f"  {YL}Esta versão requer download via página oficial da Microsoft.{R}")
            print(f"  {DM}{info.get('note','')}{R}\n")
            print(f"  {DM}Link:{R} {BL}{info['page']}{R}\n")
            sep()
            pause("  Pressione Enter para abrir o navegador (ou Ctrl+C para cancelar)...")
            open_url(info["page"])
            pause("  Pressione Enter para voltar ao menu...")


def flow_linux():
    distros = list(LINUX_ISOS.keys())
    while True:
        d_choice = menu(
            "Selecione a distribuição Linux",
            distros,
            breadcrumb="Início › Linux",
        )
        if d_choice == -1:
            return

        distro      = distros[d_choice]
        desktop_map = LINUX_ISOS[distro]
        de_list     = list(desktop_map.keys())

        while True:
            de_choice = menu(
                f"Interface gráfica  ›  {distro}",
                de_list,
                breadcrumb=f"Início › Linux › {distro}",
            )
            if de_choice == -1:
                break

            desktop  = de_list[de_choice]
            url      = desktop_map[desktop]
            label    = f"{distro}  [{desktop}]"
            dest_dir = (
                get_downloads_dir()
                / "ISO"
                / "Linux"
                / safe_dirname(distro)
            )

            if confirm_download(label, url, dest_dir):
                download_iso(label, url, dest_dir)


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    options = [
        "  🐧  Linux",
        "  🪟  Windows",
        "  ✖   Sair",
    ]
    while True:
        choice = menu(
            "Qual sistema você quer baixar?",
            options,
            allow_back=False,
        )
        if choice == 0:
            flow_linux()
        elif choice == 1:
            flow_windows()
        elif choice == 2:
            clear()
            banner()
            print(f"  {CY}Até a próxima!{R}\n")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {CY}Saindo...{R}\n")
        sys.exit(0)
