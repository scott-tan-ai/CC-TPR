@echo off
title CC-TPR Router - Stopping

echo Stopping CC-TPR Router...
echo.

:: Find process using port 3456 and kill it
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3456 ^| findstr LISTENING') do (
    echo Killing process %%a on port 3456...
    taskkill /F /PID %%a >nul 2>&1
)

echo Done.
timeout /t 2 >nul
