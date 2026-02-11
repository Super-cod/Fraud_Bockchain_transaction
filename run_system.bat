@echo off
title Blockchain System Launcher
color 0A
echo.
echo  ====================================================
echo   LOCAL PERMISSIONED BLOCKCHAIN SYSTEM
echo   SHA-256 Proof-of-Work with AI Fraud Detection
echo  ====================================================
echo.

:: Create models directory if not exists
if not exist models mkdir models

:: Clean up any existing instances first
echo  [0/4] Cleaning up existing instances...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8765 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo  [1/4] Starting Blockchain Server...
start "Blockchain Server" cmd /k "title Blockchain Server && color 0B && python server.py"
echo        Waiting for server to initialize...
timeout /t 7 /nobreak >nul

echo  [2/4] Starting Transaction Receiver...
start "Transaction Receiver" cmd /k "title Transaction Receiver && color 0D && python receiver.py"
timeout /t 2 /nobreak >nul

echo  [3/4] Starting Live Dashboard...
start "Live Dashboard" cmd /k "title Live Dashboard && color 0E && python dashboard.py"
timeout /t 2 /nobreak >nul

echo  [4/4] Starting Transaction Sender...
start "Transaction Sender" cmd /k "title Transaction Sender && color 0A && python sender.py"

echo.
echo  ====================================================
echo   ALL COMPONENTS STARTED SUCCESSFULLY!
echo  ====================================================
echo.
echo   Server    : ws://localhost:8765  (Cyan Window)
echo   Receiver  : Listening...        (Purple Window)
echo   Dashboard : Live Stats...       (Yellow Window)
echo   Sender    : Interactive CLI     (Green Window)
echo.
echo  To stop all components, run: stop_system.bat
echo.
echo  Press any key to STOP all components...
pause >nul
echo.
echo  Shutting down all components...
call stop_system.bat
