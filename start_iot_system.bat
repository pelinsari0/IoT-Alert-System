@echo off
REM IoT Alert System - One-Click Launcher
REM This script checks dependencies, starts the backend, sensor simulator, and GUI

echo ================================================
echo IoT Alert System - Starting...
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo [1/5] Checking Python installation... OK
echo.

REM Check if virtual environment exists, if not create it
if not exist "venv\" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo [2/5] Virtual environment found... OK
)
echo.

REM Activate virtual environment and check/install requirements
echo [3/5] Checking and installing dependencies...
call venv\Scripts\activate.bat

REM Check if requirements are installed by trying to import key packages
python -c "import fastapi, uvicorn, sqlalchemy, pydantic, requests, PySide6, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements!
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
) else (
    echo All dependencies already installed... OK
)
echo.

REM Start the FastAPI backend server in a new window
echo [4/5] Starting FastAPI backend server...
start "IoT Backend Server" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 127.0.0.1 --port 9000"

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Start the sensor simulator in a new window
echo [5/5] Starting sensor simulator...
start "IoT Sensor Simulator" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python sensors\sensors_simulator.py"

REM Wait a moment for sensors to start generating data
timeout /t 2 /nobreak >nul

REM Start the GUI application in the current window
echo.
echo ================================================
echo Starting GUI Dashboard...
echo ================================================
echo.
echo All components started successfully!
echo - Backend Server: http://127.0.0.1:9000
echo - Sensor Simulator: Running in background
echo - GUI Dashboard: Starting now...
echo.
echo Close this window to stop all components.
echo ================================================
echo.

python -m gui_dashboard.main

REM When GUI closes, inform user
echo.
echo GUI closed. Backend and sensors may still be running.
echo Please close their windows manually if needed.
pause
