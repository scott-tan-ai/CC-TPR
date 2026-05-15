@echo off
setlocal enabledelayedexpansion

title CC-TPR Router
cd /d "%~dp0"

echo ========================================
echo   CC-TPR Router - Startup
echo ========================================
echo.

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    set PYVER=NOT FOUND
    goto :prompt_download
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    if %%a LSS 3 goto :prompt_download
    if %%a EQU 3 if %%b LSS 12 goto :prompt_download
)
echo       Python !PYVER! - OK
echo.
goto :check_venv

:prompt_download
echo.
echo ###############################################################################
echo.
echo   Python 3.12+ not found. Current: !PYVER!
echo.
echo   Download and install Python 3.12 LTS now?
echo.
echo   [Y] Yes, download Python 3.12
echo   [N] No, exit
echo.
echo ###############################################################################
choice /c YN /n
if errorlevel 2 exit /b

echo.
echo Downloading Python 3.12.4 LTS...
curl -L -o "%USERPROFILE%\Downloads\python-3.12.4-amd64.exe" https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe

echo.
echo Opening Downloads folder...
start explorer.exe "%USERPROFILE%\Downloads"

echo.
echo Launching Python installer...
start "" "%USERPROFILE%\Downloads\python-3.12.4-amd64.exe"

echo.
echo ###############################################################################
echo   Python 3.12 is being downloaded.
echo   Please install Python 3.12 or above and
echo   relaunch CC-TPR_Win_Start.bat to start CC-TPR.
echo   Press any key to exit...
echo ###############################################################################
pause >nul
exit /b

:check_venv
echo [2/6] Checking virtual environment...
if not exist ".venv" (
    echo       .venv not found - creating...
    python -m venv .venv
    echo       Installing dependencies...
    .venv\Scripts\python.exe -m pip install -q -e ".[dev]"
    echo       .venv created - OK
) else (
    echo       .venv found - OK
)
echo.

echo [3/6] Checking config...
if not exist "config.yaml" (
    echo       WARNING: config.yaml not found!
) else (
    echo       config.yaml found - OK
)
if not exist ".env" (
    echo       WARNING: .env not found - API keys may be missing
) else (
    echo       .env found - OK
)
echo.

echo [4/6] Setting up statusline...
set "CLAUDE_DIR=%USERPROFILE%\.claude"
if not exist "%CLAUDE_DIR%" mkdir "%CLAUDE_DIR%"

if not exist "%CLAUDE_DIR%\smart-router-status.py" (
    copy /Y "statusline\smart-router-status.py" "%CLAUDE_DIR%\smart-router-status.py" >nul
    echo       Copied smart-router-status.py to %CLAUDE_DIR%
) else (
    echo       smart-router-status.py already installed - OK
)

set "SETTINGS=%CLAUDE_DIR%\settings.json"
set "NEED_REGISTER=0"
if exist "%SETTINGS%" (
    findstr /C:"statusLine" "%SETTINGS%" >nul 2>&1
    if errorlevel 1 set "NEED_REGISTER=1"
) else (
    set "NEED_REGISTER=1"
)

if "!NEED_REGISTER!"=="1" (
    echo.
    echo       Statusline not registered in Claude Code.
    echo       Register now? [Y/n]
    choice /c YN /n /t 10 /d Y
    if not errorlevel 2 (
        if exist "%SETTINGS%" (
            copy /Y "%SETTINGS%" "%SETTINGS%.bak" >nul
            .venv\Scripts\python.exe -c "import json,sys;s=json.load(open(sys.argv[1]));s.setdefault('statusLine',{}).update({'command':'python \"%CLAUDE_DIR%\\smart-router-status.py\"'});json.dump(s,open(sys.argv[1],'w'),indent=2)" "%SETTINGS%"
        ) else (
            echo {"statusLine": {"command": "python \"%CLAUDE_DIR%\\smart-router-status.py\""}} > "%SETTINGS%"
        )
        echo       Registered! Restart Claude Code to activate statusline.
    ) else (
        echo       Skipped. You can register manually later.
    )
)
echo.

echo [5/6] Checking MiniMax MCP...
.venv\Scripts\python.exe -m src.utils.mcp_check
echo.

echo [6/6] Starting CC-TPR Router...
echo       Listening on http://127.0.0.1:3456
echo       Press Ctrl+C to stop
echo.
echo ========================================
echo.
.venv\Scripts\python.exe -m src.main
