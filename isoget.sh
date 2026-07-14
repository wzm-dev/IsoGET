#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  SyncX ISOGet  ·  Launcher Linux/macOS
#  BadOctop4s  ·  https://github.com/BadOctop4s
# ─────────────────────────────────────────────────────────────

# Cores ANSI
R=$'\033[0m'
BD=$'\033[1m'
DM=$'\033[2m'
CY=$'\033[96m'
GR=$'\033[92m'
YL=$'\033[93m'
RD=$'\033[91m'
WH=$'\033[97m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRIPT="$SCRIPT_DIR/isoget.py"

banner() {
    printf "\n"
    printf "${CY}${BD}  ██╗███████╗ ██████╗  ██████╗ ███████╗████████╗\n"
    printf "  ██║██╔════╝██╔═══██╗██╔════╝ ██╔════╝╚══██╔══╝\n"
    printf "  ██║███████╗██║   ██║██║  ███╗█████╗     ██║\n"
    printf "  ██║╚════██║██║   ██║██║   ██║██╔══╝     ██║\n"
    printf "  ██║███████║╚██████╔╝╚██████╔╝███████╗   ██║\n"
    printf "  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝${R}\n"
    printf "${DM}      ISO Downloader  ·  SyncX Tools  ·  BadOctop4s${R}\n"
    printf "\n"
    printf "  ${DM}════════════════════════════════════════════════${R}\n\n"
}

# ─── Verifica se o arquivo principal existe ────────────────────────────────────
if [ ! -f "$MAIN_SCRIPT" ]; then
    banner
    printf "  ${RD}[!] Arquivo isoget.py nao encontrado em:${R}\n"
    printf "      $SCRIPT_DIR\n\n"
    printf "  Certifique-se de que isoget.py e isoget.sh\n"
    printf "  estejam na mesma pasta.\n\n"
    exit 1
fi

banner

# ─── Detecta Python3 ──────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" --version 2>&1)
        # Aceita só Python 3.x
        if echo "$VER" | grep -q "Python 3"; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -n "$PYTHON" ]; then
    printf "  ${GR}[OK]${R} $($PYTHON --version) detectado.\n\n"
    printf "  ${DM}════════════════════════════════════════════════${R}\n\n"
    exec "$PYTHON" "$MAIN_SCRIPT"
fi

# ─── Python não encontrado — pergunta se instala ───────────────────────────────
printf "  ${YL}[!]${R} Python 3 nao encontrado.\n\n"
read -rp "   Deseja instalar o Python3 agora? (S/N): " CHOICE
printf "\n"

case "$CHOICE" in
    [Ss])
        printf "  Detectando gerenciador de pacotes...\n\n"

        if command -v apt-get &>/dev/null; then
            PM="apt"
            printf "  ${DM}Gerenciador:${R} apt (Debian/Ubuntu/Mint)\n"
            sudo apt-get update -qq
            sudo apt-get install -y python3 python3-pip

        elif command -v dnf &>/dev/null; then
            PM="dnf"
            printf "  ${DM}Gerenciador:${R} dnf (Fedora/RHEL)\n"
            sudo dnf install -y python3 python3-pip

        elif command -v pacman &>/dev/null; then
            PM="pacman"
            printf "  ${DM}Gerenciador:${R} pacman (Arch/Manjaro/EndeavourOS)\n"
            sudo pacman -S --noconfirm python python-pip

        elif command -v zypper &>/dev/null; then
            PM="zypper"
            printf "  ${DM}Gerenciador:${R} zypper (openSUSE)\n"
            sudo zypper install -y python3 python3-pip

        elif command -v emerge &>/dev/null; then
            PM="emerge"
            printf "  ${DM}Gerenciador:${R} emerge (Gentoo)\n"
            sudo emerge --ask=n dev-lang/python

        elif command -v brew &>/dev/null; then
            PM="brew"
            printf "  ${DM}Gerenciador:${R} brew (macOS/Linuxbrew)\n"
            brew install python3

        elif command -v apk &>/dev/null; then
            PM="apk"
            printf "  ${DM}Gerenciador:${R} apk (Alpine Linux)\n"
            sudo apk add python3 py3-pip

        else
            printf "  ${RD}[!]${R} Gerenciador de pacotes nao reconhecido.\n"
            printf "  Instale manualmente: ${WH}https://python.org/downloads${R}\n\n"
            exit 1
        fi

        # Verifica se a instalação funcionou
        if command -v python3 &>/dev/null; then
            printf "\n  ${GR}[OK]${R} Python 3 instalado com sucesso!\n\n"
            printf "  ${DM}════════════════════════════════════════════════${R}\n\n"
            exec python3 "$MAIN_SCRIPT"
        else
            printf "\n  ${RD}[!]${R} Instalacao falhou. Tente manualmente.\n\n"
            exit 1
        fi
        ;;
    *)
        printf "  Operacao cancelada.\n"
        printf "  Instale o Python 3 e rode o script novamente.\n\n"
        exit 1
        ;;
esac
