@echo off
REM ========================================
REM Start Emergentica Voice Testing
REM ========================================

echo.
echo ================================================================================
echo   EMERGENTICA - LIVE VOICE TESTING
echo ================================================================================
echo.
echo This will open 3 windows:
echo   1. FastAPI Server (port 8000)
echo   2. Streamlit Dashboard (port 8501)
echo   3. Instructions for ngrok setup
echo.
pause

REM Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo Starting services...
echo.

REM Start FastAPI in new window
start "Emergentica - FastAPI Server" cmd /k "cd /d "%SCRIPT_DIR%" && .\venv\Scripts\activate && py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment
timeout /t 2 /nobreak > nul

REM Start Streamlit in new window
start "Emergentica - Dashboard" cmd /k "cd /d "%SCRIPT_DIR%" && .\venv\Scripts\activate && streamlit run dashboard.py"

REM Wait a moment
timeout /t 2 /nobreak > nul

REM Show ngrok instructions
start "Emergentica - ngrok Setup" cmd /k "echo. && echo ======================================== && echo   NGROK SETUP && echo ======================================== && echo. && echo Run this command: && echo. && echo   ngrok http 8000 && echo. && echo Then copy the HTTPS URL and configure: && echo. && echo 1. Retell AI Agent webhook: && echo    https://YOUR-NGROK-URL/webhook/retell/live && echo. && echo 2. Verify Twilio webhook (should already be set): && echo    https://api.retellai.com/v1/call/twilio && echo. && echo 3. Call your number: +447493790833 && echo. && echo See QUICK_START_VOICE.md for full instructions && echo. && echo ======================================== && echo."

echo.
echo ✅ Services started!
echo.
echo Check the opened windows:
echo   - FastAPI Server: http://localhost:8000
echo   - Dashboard: http://localhost:8501
echo   - ngrok instructions window
echo.
echo Press any key to close this window...
pause > nul
