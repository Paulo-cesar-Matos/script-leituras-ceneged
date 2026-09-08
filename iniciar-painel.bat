@echo off
:: Garante que o terminal rode na mesma pasta onde o .bat está salvo
cd /d "%~dp0"

:: Nome da pasta e link do seu repositório Git
set PASTA_PROJETO=Painel_Erros_SAP
set REPOSITORIO=https://github.com/Paulo-cesar-Matos/script-leituras-ceneged.git

:: 1. VERIFICA SE O PROJETO JÁ FOI BAIXADO
if not exist "%PASTA_PROJETO%\.git" (
    echo Projeto nao encontrado. Baixando do zero...
    git clone %REPOSITORIO% "%PASTA_PROJETO%"
) else (
    echo Atualizando o codigo com as ultimas alteracoes...
    cd "%PASTA_PROJETO%"
    git pull origin main
    cd ..
)

:: 2. ENTRA NA PASTA DO PROJETO PARA EXECUTAR OS ARQUIVOS
cd "%PASTA_PROJETO%"

:: 3. TRAVA DE SEGURANÇA: VERIFICA AS SENHAS
if not exist ".env" (
    echo.
    echo ==========================================================
    echo [AVISO] O arquivo .env nao foi encontrado!
    echo Coloque o arquivo .env
    echo dentro da pasta "%PASTA_PROJETO%" antes de continuar.
    echo ==========================================================
    echo.
    pause
    exit
)

:: 4. INICIA O SISTEMA
echo Iniciando o painel.

:: Inicia o robo do SAP minimizado na barra de tarefas
start /MIN python extrair_leituras.py

:: Inicia o servidor do painel na porta 9000 de forma invisivel
start /B python -m http.server 9000

:: Aguarda 3 segundos para dar tempo de os processos iniciarem
timeout /t 3 /nobreak > nul

:: Abre o navegador Edge em tela cheia (Kiosk) direto no painel
start msedge --kiosk http://localhost:9000