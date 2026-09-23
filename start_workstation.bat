@echo off
title Industrial PdM Platform - Workstation Launcher (Turbine Motor Unit A1)
color 0A

echo ==============================================================================
echo       INDUSTRIAL PREDICTIVE MAINTENANCE PLATFORM - WORKSTATION LAUNCHER
echo                 Asset: Turbine Motor Unit A1 (MCH-802X)
echo ==============================================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    echo Please install Python 3.10+ and run again.
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in system PATH.
    echo Please install Node.js 18+ and run again.
    pause
    exit /b 1
)

echo [1/3] Starting FastAPI Backend & AI Inference Engine (Port 8001)...
start "PDM Backend - Turbine Motor A1" cmd /c "python -u -m uvicorn main:app --host 0.0.0.0 --port 8001"

echo Waiting 5 seconds for AI models and backend to initialize...
timeout /t 5 /nobreak >nul

echo [2/3] Starting React Dashboard Frontend (Port 5173)...
start "PDM Dashboard - Turbine Motor A1" cmd /c "cd frontend && npx vite --port 5173 --host"

echo Waiting 4 seconds for frontend dev server...
timeout /t 4 /nobreak >nul

echo [3/3] Opening Dashboard in default web browser...
start http://localhost:5173/

echo.
echo ==============================================================================
echo  SYSTEM IS ONLINE!
echo ==============================================================================
echo  - Dashboard UI          : http://localhost:5173/
echo  - Backend API & Docs    : http://localhost:8001/docs
echo  - Live Tag ID Endpoint  : http://localhost:8001/api/tags/live
echo  - MQTT Gateway Status   : http://localhost:8001/api/mqtt/status
echo.
echo  MQTT Ingestion Details:
echo  - Topic                 : plant/bay4/turbine_motor/MCH-802X/telemetry
echo  - Target Machine ID     : MCH-802X
echo  - Nominal Cadence (Dt)  : 1000 ms (1 Hz)
echo  - Supported Tag IDs     : 8 standard industrial tags
echo.
echo  To run the test publisher from this workstation:
echo    python scripts/test_gpu_sender.py --interval 1.0
echo.
echo  Keep the opened command windows running while using the system.
echo ==============================================================================
pause
