@echo off
:: Garante que o terminal rode na mesma pasta onde o .bat esta salvo (ex:Area de Trabalho)
cd /d "%~dp0"

:: Nome da pasta que ele vai criar e link do seu repositorio Git
set PASTA_PROJETO=Painel_Erros_SAP
set REPOSITORIO=https://github.com/Paulo-cesar-Matos/script-leituras-ceneged.git

:: 0. VERIFICA E INSTALA O GIT SE NECESSARIO
git --version >nul 2>&1
if %errorlevel% neq 0 (
  echo [!] Git nao encontrado! Instalando automaticamente via winget...
  winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
  echo.
  echo ==========================================================
  echo Instalacao do Git concluida!
  echo Por favor, FECHE esta janela e ABRA O SCRIPT NOVAMENTE
  echo para o sistema reconhecer os comandos do Git.
  echo ==========================================================
  pause
  exit
)

:: 1. VERIFICA SE O PROJETO JA FOI BAIXADO
if not exist "%PASTA_PROJETO%\.git" (
  echo Projeto nao encontrado. Baixando do zero...
  git clone %REPOSITORIO% "%PASTA_PROJETO%"
  ) else (
  echo ?? Atualizando o codigo com as ultimas alteracoes...
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
  echo ATENCAO: O arquivo .env nao foi encontrado!
  echo O Git nao baixa senhas por seguranca. Crie o arquivo .env
  echo dentro da pasta "%PASTA_PROJETO%" antes de continuar.
  echo ==========================================================
  echo.
  pause
  exit
)

:: 4. INICIA O SISTEMA
echo Iniciando o robo e o painel...

:: Inicia o robo do SAP minimizado
start /MIN python extrair_leituras.py

:: Inicia o servidor do painel na porta 9000
start /B python -m http.server 9000

:: Aguarda 3 segundos
timeout /t 3 /nobreak > nul

:: Abre o navegador em tela cheia
start msedge --kiosk http://localhost:9000
