@echo off
echo Iniciando paineis e automacoes...

:: ==========================================
:: PARTE 1: INICIA OS SERVIDORES E A TELA
:: ==========================================

:: Inicia o servidor proprio para o index.html na porta 9001 minimizado
start "Servidor Index" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\script-leituras-ceneged && python -m http.server 9001"

:: Inicia o Frontend e Backend minimizados na barra de tarefas
start "Frontend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\sap-site-builder && npm run dev"
start "Backend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\operacao-diaria2-backend && python manage.py runserver"

:: Aguarda 5 segundos para dar tempo de os processos iniciarem
timeout /t 5 /nobreak > nul

:: Abre o navegador em tela cheia com as duas abas na mesma janela
start msedge --start-fullscreen "http://localhost:9001" "http://localhost:8080"


:: ==========================================
:: PARTE 2: FILA PERFEITA DOS ROBOS (LOOP)
:: ==========================================
:: Este terminal vai ficar aberto em segundo plano rodando a fila

:inicio
echo.
echo ========================================
echo [%time%] Iniciando: Extrair Leituras
cd C:\Users\paulomatos\Documents\GitHub\script-leituras-ceneged
C:\Python314\python.exe extrair_leituras.py

echo.
echo ========================================
echo [%time%] Limpando a memoria e processos residuais do SAP...
:: O parametro /F forca o fechamento e o /T mata qualquer processo filho invisivel
taskkill /F /IM saplogon.exe /T > nul 2>&1
taskkill /F /IM sapgui.exe /T > nul 2>&1
:: O sapdp (Data Provider) costuma ser o culpado por travar a memoria COM
taskkill /F /IM sapdp.exe /T > nul 2>&1

echo.
echo ========================================
echo Aguardando 15 segundos para o Windows limpar o SAP da memoria...
timeout /t 15 /nobreak > nul

echo.
echo ========================================
echo [%time%] Iniciando: Leitura Repescagem
cd C:\Users\paulomatos\Documents\GitHub\extrair-para-acomp-diario
C:\Python314\python.exe extracao_leitura_repe.py

echo.
echo ========================================
echo [%time%] Rodada concluida! Aguardando 30 minutos...
:: Espera 1800 segundos (30 min) antes de recomecar
timeout /t 1800 /nobreak
goto inicio