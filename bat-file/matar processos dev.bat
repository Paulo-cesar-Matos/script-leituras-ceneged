echo Matando processos desenvolvimento

taskkill /F /IM saplogon.exe /T > nul 2>&1
taskkill /F /IM sapgui.exe /T > nul 2>&1
taskkill /F /IM sapdp.exe /T > nul 2>&1
taskkill /F /IM firefox.exe /T > nul 2>&1
taskkill /F /IM python.exe /T > nul 2>&1
taskkill /F /IM cmd.exe /T > nul 2>&1