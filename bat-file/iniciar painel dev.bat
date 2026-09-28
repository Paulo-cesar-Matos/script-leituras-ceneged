start "Servidor Index" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\script-leituras-ceneged && python -m http.server 9001"
start "Frontend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\sap-site-builder && npm run dev"
start "Backend" /MIN cmd /k "cd C:\Users\paulomatos\Documents\GitHub\operacao-diaria2-backend && python manage.py runserver"

timeout /t 5 /nobreak > nul
start firefox "http://localhost:9001" "http://localhost:8080"