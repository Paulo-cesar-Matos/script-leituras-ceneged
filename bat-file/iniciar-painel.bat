@echo off
echo Iniciando paineis e automacoes...

:: ==========================================
:: INICIA OS SERVIDORES E A TELA (Roda 1 vez)
:: ==========================================
start "Servidor Index" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\script-leituras-ceneged && python -m http.server 9001"
start "Frontend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\sap-site-builder && npm run dev"
start "Backend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\operacao-diaria2-backend && python manage.py runserver"

timeout /t 5 /nobreak > nul
start msedge --start-fullscreen "http://localhost:9001" "http://localhost:8080"


:: ==========================================
:: CICLO DOS ROBOS (Loop a cada 30 minutos)
:: ==========================================
:inicio

:: ------------------------------------------
:: BLOCO 1: EXTRAIR LEITURAS
:: ------------------------------------------
echo.
echo ========================================
echo [%time%] Limpando processos antigos do SAP...
taskkill /F /IM saplogon.exe /T > nul 2>&1
taskkill /F /IM sapgui.exe /T > nul 2>&1
taskkill /F /IM sapdp.exe /T > nul 2>&1
timeout /t 3 /nobreak > nul

echo [%time%] Abrindo SAP Logon para Extrair Leituras...
start "" "C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"

echo Aguardando 15 segundos para o SAP carregar...
timeout /t 15 /nobreak > nul

echo [%time%] Iniciando: Extrair Leituras
cd C:\Users\paulomatos\Documents\GitHub\script-leituras-ceneged
C:\Python314\python.exe extrair_leituras.py


:: ------------------------------------------
:: BLOCO 2: LEITURA REPESCAGEM
:: ------------------------------------------
echo.
echo ========================================
echo [%time%] Limpando processos para a Repescagem...
taskkill /F /IM saplogon.exe /T > nul 2>&1
taskkill /F /IM sapgui.exe /T > nul 2>&1
taskkill /F /IM sapdp.exe /T > nul 2>&1
timeout /t 3 /nobreak > nul

echo [%time%] Abrindo SAP Logon para Repescagem...
start "" "C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"

echo Aguardando 15 segundos para o SAP carregar...
timeout /t 15 /nobreak > nul

echo [%time%] Iniciando: Leitura Repescagem
cd C:\Users\paulomatos\Documents\GitHub\extrair-para-acomp-diario
C:\Python314\python.exe extracao_leitura_repe.py


:: ------------------------------------------
:: FIM DO CICLO
:: ------------------------------------------
echo.
echo ========================================
echo [%time%] Rodada completa finalizada! Aguardando 30 minutos...
timeout /t 1800 /nobreak
goto inicio