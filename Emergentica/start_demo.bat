@echo off
REM ========================================
REM Emergentica - Quick Demo Launcher
REM ========================================

echo.
echo ================================================================================
echo   EMERGENTICA - VOICE DEMO LAUNCHER
echo ================================================================================
echo.
echo Starting all services for voice demo...
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start FastAPI
start "Emergentica - API Server" cmd /k "cd /d "%SCRIPT_DIR%" && .\venv\Scripts\activate && py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

REM Start Dashboard
start "Emergentica - Dashboard" cmd /k "cd /d "%SCRIPT_DIR%" && .\venv\Scripts\activate && streamlit run dashboard.py"

timeout /t 3 /nobreak > nul

REM Open voice interface in browser
start "" "%SCRIPT_DIR%voice_interface.html"

timeout /t 2 /nobreak > nul

echo.
echo ================================================================================
echo   ✅ ALL SERVICES STARTED!
echo ================================================================================
echo.
echo   📊 Dashboard: http://localhost:8501
echo   🎤 Voice Interface: voice_interface.html (opened in browser)
echo   🔧 API Server: http://localhost:8000
echo.
echo   NOTE: You'll need ngrok running separately for webhooks:
echo        ngrok http 8000
echo.
echo   Then configure Retell webhook to:
echo        https://YOUR-NGROK-URL/webhook/retell/live
echo.
echo ================================================================================
echo.
pause
