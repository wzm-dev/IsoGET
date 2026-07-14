@echo off
title SyncX ISOGet
chcp 65001 >nul 2>&1

:: Habilita cores ANSI no cmd moderno
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

echo.
echo   ██╗███████╗ ██████╗  ██████╗ ███████╗████████╗
echo   ██║██╔════╝██╔═══██╗██╔════╝ ██╔════╝╚══██╔══╝
echo   ██║███████╗██║   ██║██║  ███╗█████╗     ██║
echo   ██║╚════██║██║   ██║██║   ██║██╔══╝     ██║
echo   ██║███████║╚██████╔╝╚██████╔╝███████╗   ██║
echo   ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝
echo       ISO Downloader  ·  SyncX Tools  ·  BadOctop4s
echo.
echo   ════════════════════════════════════════════════
echo.

:: ── Verifica Python ───────────────────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% == 0 goto :check_ok

:: Python não encontrado — pergunta se instala
echo   [!] Python nao encontrado no PATH.
echo.
set /p "INSTALL=   Deseja instalar o Python agora? (S/N): "
echo.

if /i "%INSTALL%"=="S" goto :install_python
if /i "%INSTALL%"=="s" goto :install_python

echo   Sem Python, nao e possivel continuar.
echo   Instale manualmente em: https://python.org/downloads
echo.
pause
exit /b 1

:install_python
echo   Tentando instalar via winget (requer Windows 10+)...
echo.
winget install --id Python.Python.3 --accept-package-agreements --accept-source-agreements
if %errorlevel% == 0 (
    echo.
    echo   [OK] Python instalado com sucesso!
    echo   Reiniciando o script para aplicar as mudancas...
    echo.
    timeout /t 3 /nobreak >nul
    :: Relança o script em um novo processo para pegar o Python novo no PATH
    start "" "%~f0"
    exit /b 0
) else (
    echo.
    echo   [!] Falha no winget. Abrindo python.org no navegador...
    start https://www.python.org/downloads/
    echo.
    echo   Instale o Python marcando a opcao "Add to PATH",
    echo   feche este terminal, abra um novo e rode o script novamente.
    echo.
    pause
    exit /b 1
)

:check_ok
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo   [OK] Python %PYVER% detectado.
echo.
echo   ════════════════════════════════════════════════
echo.

:: ── Roda o script principal ────────────────────────────────────────────────────
python "%~dp0isoget.py"

if %errorlevel% neq 0 (
    echo.
    echo   [!] O script terminou com erro (codigo %errorlevel%).
    pause
)
