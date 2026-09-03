@echo off
setlocal enabledelayedexpansion
title Inicializador - Painel de Erros SAP

:: Garante que o terminal rode na mesma pasta onde o .bat esta salvo (ex: Area de Trabalho)
cd /d "%~dp0"

echo ==========================================================
echo        VERIFICANDO REQUISITOS DO SISTEMA
echo ==========================================================

:: 1. VERIFICA PASTA DO ONEDRIVE
set "ONEDRIVE_PATH=%USERPROFILE%\OneDrive - CENEGED - COMPANHIA ELETROMECANICA E GERENCIAMENTO DE DADOS\script erros"
if exist "%ONEDRIVE_PATH%" (
    echo [OK] OneDrive Logado - Pasta encontrada.
) else (
    echo [X] ERRO: Pasta do OneDrive nao encontrada. 
    echo     Verifique se o OneDrive da CENEGED esta logado neste computador.
    echo     Caminho esperado: "%ONEDRIVE_PATH%"
    pause
    exit
)

:: 2. VERIFICA DEPENDENCIAS OBRIGATORIAS NO CMD (GIT e PYTHON)
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Git nao encontrado! Instalando automaticamente via winget...
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    echo.
    echo [!] Instalacao do Git concluida! FECHE esta janela e abra o script novamente.
    pause
    exit
) else (
    echo [OK] Git
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python nao encontrado! Instale o Python e marque "Add Python to PATH".
    pause
    exit
) else (
    echo [OK] Python
)

:: 3. VERIFICA OUTROS PROGRAMAS ESSENCIAIS (APENAS AVISO SE FALTAR)

:: SAP Logon / SAP GUI
if exist "C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe" (
    echo [OK] SAP Logon
) else if exist "C:\Program Files\SAP\FrontEnd\SAPgui\saplogon.exe" (
    echo [OK] SAP Logon
) else (
    echo [!] AVISO: SAP GUI nao encontrado nos caminhos padroes.
)

:: VPN GlobalProtect
if exist "C:\Program Files\Palo Alto Networks\GlobalProtect\PanGPA.exe" (
    echo [OK] GlobalProtect VPN
) else (
    echo [!] AVISO: GlobalProtect VPN nao encontrado.
)

:: PostgreSQL
if exist "C:\Program Files\PostgreSQL" (
    echo [OK] PostgreSQL
) else (
    echo [!] AVISO: PostgreSQL nao encontrado na pasta padrao.
)

:: VS Code
code --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] VS Code
) else if exist "%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe" (
    echo [OK] VS Code
) else (
    echo [!] AVISO: VS Code nao encontrado.
)

:: DBeaver
if exist "C:\Program Files\DBeaver\dbeaver.exe" (
    echo [OK] DBeaver
) else if exist "%LOCALAPPDATA%\DBeaver\dbeaver.exe" (
    echo [OK] DBeaver
) else (
    echo [!] AVISO: DBeaver nao encontrado.
)

:: RustDesk
if exist "C:\Program Files\RustDesk\rustdesk.exe" (
    echo [OK] RustDesk
) else (
    echo [!] AVISO: RustDesk nao encontrado.
)

:: AnyDesk
if exist "C:\Program Files (x86)\AnyDesk\AnyDesk.exe" (
    echo [OK] AnyDesk
) else (
    echo [!] AVISO: AnyDesk nao encontrado.
)

echo ==========================================================
echo Verificacao concluida.
echo.

:: 4. GERENCIA O REPOSITORIO DO PROJETO
set PASTA_PROJETO=Painel_Erros_SAP
set REPOSITORIO=https://github.com/Paulo-cesar-Matos/script-leituras-ceneged.git

if not exist "%PASTA_PROJETO%\.git" (
  echo Projeto nao encontrado localmente. Baixando do zero...
  git clone %REPOSITORIO% "%PASTA_PROJETO%"
) else (
  echo Buscando atualizacoes do codigo no GitHub...
  cd "%PASTA_PROJETO%"
  git pull origin main
  cd ..
)

:: 5. ENTRA NA PASTA DO PROJETO PARA EXECUTAR OS ARQUIVOS
cd "%PASTA_PROJETO%"

:: 6. TRAVA DE SEGURANCA: VERIFICA AS SENHAS (.env)
if not exist ".env" (
  echo.
  echo ==========================================================
  echo ATENCAO: O arquivo .env (com as senhas) nao foi encontrado!
  echo Crie o arquivo .env dentro da pasta:
  echo "%~dp0%PASTA_PROJETO%"
  echo ==========================================================
  echo.
  pause
  exit
)

:: 7. INICIA O SISTEMA
echo Iniciando o robo e o painel...

:: Inicia o robo do SAP em uma nova janela minimizada
start "Robo SAP" /MIN python extrair_leituras.py

:: Inicia o servidor local na porta 9000 em uma janela para nao prender a porta no background
start "Servidor Local" /MIN python -m http.server 9000

:: Aguarda 3 segundos
timeout /t 3 /nobreak > nul

:: Abre o navegador em tela cheia
start msedge --kiosk http://localhost:9000

exit
