@echo off
title CC-TPR Router
cd /d "%~dp0"

echo Starting CC-TPR Router...
echo.

if not exist ".venv" (
    echo ERROR: Virtual environment not found.
    echo Run the setup first: python -m venv .venv
    pause
    exit /b 1
)

.venv\Scripts\python.exe -m pip install -q --upgrade pip
.venv\Scripts\python.exe -m pip install -q -e ".[dev]"

if not exist ".env" (
    echo WARNING: .env file not found.
    echo Copy .env.example to .env and add your API keys.
    echo Continuing anyway...
    echo.
)

.venv\Scripts\python.exe -m src.main
