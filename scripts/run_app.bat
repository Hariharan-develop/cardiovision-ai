@echo off
setlocal enabledelayedexpansion

echo ===============================================================================
echo   CardioVision AI - Startup Script (Windows)
echo   IIT Mandi Multimodal AI Hackathon 2026 - Track A
echo ===============================================================================

:: 1. Validate Python availability
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found on your system PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    exit /b 1
)

:: 2. Check for port conflicts on port 8502
echo [INFO] Checking for active listeners on port 8502...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8502" ^| findstr "LISTENING"') do (
    echo [WARNING] Port 8502 is already in use by process PID: %%a.
    echo Attempting to terminate stale process...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 2 /nobreak >nul
)

:: 3. Change to project root directory
cd /d "%~dp0\.."

:: 4. Verify model files exist
if not exist "models\cad_model.pkl" (
    if not exist "cad_model.pkl" (
        echo [ERROR] Model files missing! Expected models/cad_model.pkl
        exit /b 1
    )
)

echo [INFO] Starting CardioVision AI Server on http://127.0.0.1:8502/dashboard...
echo [INFO] Press Ctrl+C in this terminal to shut down the server.
echo ===============================================================================

python api_server.py
