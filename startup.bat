@echo off
REM ──────────────────────────────────────────────────────────────────────
REM Start OfflineManager Application Only
REM ──────────────────────────────────────────────────────────────────────

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Ensure virtual environment exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found. Please run your setup script first.
    exit /b 1
)

REM Activate venv and configure PYTHONPATH
call .venv\Scripts\activate.bat
set PYTHONPATH=%~dp0

REM Launch the application based on available entry point
if exist "main.py" (
    echo Found main.py, starting application...
    python main.py
) else if exist "app_launcher.py" (
    echo Found app_launcher.py, starting application...
    python app_launcher.py
) else if exist "automotive_invoice_manager\ui\app.py" (
    echo Found automotive_invoice_manager\ui\app.py, running as module...
    python -c "import sys; sys.path.append('.'); from automotive_invoice_manager.ui.app import FullScreenLoginApp; app = FullScreenLoginApp(); app.run()"
) else if exist "app.py" (
    echo Found app.py, starting application...
    python app.py
) else if exist "automotive_invoice_manager\__main__.py" (
    echo Found __main__.py, starting as module...
    python -m automotive_invoice_manager
) else (
    echo No main entry point found.
    exit /b 1
)

endlocal
exit /b 0
