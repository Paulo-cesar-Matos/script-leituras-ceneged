@echo off
echo Iniciando paineis e automacoes...

:: preconfig paineis modulos
:: C:\Python314\python.exe -m pip install openpyxl pywin32 pyperclip pandas psycopg2-binary sqlalchemy schedule python-dotenv
:: instalação extensão edge/chrome
:: 3-2-1 Revolver - Tab Rotator & Twitch Auto-Reloader

:: Inicia o script de extracao repe minimizado
start "Leitura Repe" /MIN cmd /k "timeout /t 30 /nobreak > nul && cd C:\Users\paulomatos\Documents\GitHub\extrair-para-acomp-diario && C:\Python314\python.exe extracao_leitura_repe.py"
:: Inicia o bot de extrair leituras minimizado
start "Extrair Leituras" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\script-leituras-ceneged && C:\Python314\python.exe extrair_leituras.py"

:: Inicia o servidor proprio para o index.html na porta 9001 minimizado
start "Servidor Index" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\script-leituras-ceneged && python -m http.server 9001"

:: Inicia o servidor do outro painel na porta 9000 de forma invisivel
start /B python -m http.server 9000

:: Inicia o Frontend e Backend minimizados na barra de tarefas
start "Frontend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\sap-site-builder && npm run dev"
start "Backend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\operacao-diaria2-backend && python manage.py runserver"

:: Aguarda 5 segundos para dar tempo de os processos iniciarem
timeout /t 5 /nobreak > nul

:: Abre o navegador em tela cheia com as três abas na mesma janela
start msedge --start-fullscreen "http://localhost:9001" "http://localhost:8080"