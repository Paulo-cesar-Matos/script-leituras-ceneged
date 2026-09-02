@echo off
:: Navega até a pasta do projeto (Coloque o caminho correto da sua pasta aqui)
cd "C:\Users\paulomatos\Downloads\Script erros\Script erros"

:: ?? Traz as últimas atualizações do código do GitHub antes de ligar
echo Verificando atualizacoes do codigo no Git...
git pull origin main

:: Iniciar extrair_leituras.py em segundo plano
start /MIN python extrair_leituras.py

:: Inicia o servidor silenciosamente na porta 8000
start /B python -m http.server 8000

:: Aguarda 2 segundos para o servidor ligar
timeout /t 2 /nobreak > nul

:: Abre o navegador Edge (ou Chrome) em tela cheia direto no painel
start msedge --kiosk http://localhost:8000