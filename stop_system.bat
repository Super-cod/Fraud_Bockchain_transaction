@echo off
title Stopping Blockchain System
color 0C
echo.
echo  ====================================================
echo   STOPPING ALL BLOCKCHAIN COMPONENTS
echo  ====================================================
echo.

echo  [1/2] Closing all blockchain windows...
taskkill /FI "WINDOWTITLE eq Blockchain Server*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Transaction Receiver*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Live Dashboard*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Transaction Sender*" /F >nul 2>&1

echo  [2/2] Killing any remaining Python processes on port 8765...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8765') do (
    taskkill /PID %%a /F >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo  ====================================================
echo   ALL COMPONENTS STOPPED
echo  ====================================================
echo.
pause
