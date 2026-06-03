@echo off
setlocal
cd /d "C:\Users\HP\OneDrive - Build Bright University\Desktop\Pinterest Video Download" || (echo Failed to change directory & pause & exit /b 1)

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
  echo Virtual environment not found: %VENV_PY%
  echo Run setup to create .venv, then try again.
  pause
  exit /b 1
)

start "Pinterest Downloader" cmd /k ""%VENV_PY%" app.py"

rem Wait up to ~15s for the server to accept connections
powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 15;$i++){try{(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000 | Out-Null); $ok=$true; break}catch{}; Start-Sleep -Seconds 1}; if($ok){Start-Process http://127.0.0.1:5000} else {Write-Host 'Server did not start. Check the server window for errors.'}"
endlocal
