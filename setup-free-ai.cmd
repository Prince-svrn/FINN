@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" scripts\setup_free_ai.py
if errorlevel 1 goto failed
echo.
echo Setup complete. Restart FINN with start.cmd, then try Include model synthesis.
pause
exit /b 0
:failed
echo.
echo Setup or connection check did not finish. Read the explanation above.
echo Do not purchase credits. The saved-data demo still works.
pause
exit /b 1
