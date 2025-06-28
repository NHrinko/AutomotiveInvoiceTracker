@echo off
REM OfflineManager Development Helper Script
REM This batch file automates common development tasks for the automotive invoice manager

setlocal enabledelayedexpansion

REM Set project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM Display menu
:menu
echo.
echo ==========================================
echo  OfflineManager Development Tools
echo ==========================================
echo  1. Setup Project (Create venv + install deps)
echo  2. Install Dependencies Only
echo  3. Run Tests
echo  4. Run Linting (flake8)
echo  5. Start Application
echo  6. Clean Environment
echo  7. Exit
echo ==========================================
set /p choice="Select an option (1-7): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto install_deps
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto run_linting
if "%choice%"=="5" goto start_app
if "%choice%"=="6" goto clean
if "%choice%"=="7" goto exit
echo Invalid choice. Please try again.
goto menu

:setup
echo.
echo Setting up OfflineManager development environment...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    goto menu
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        goto menu
    )
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    goto menu
)

python -m pip install --upgrade pip
pip install -r requirements.txt
if exist "requirements-dev.txt" (
    pip install -r requirements-dev.txt
)

echo.
echo Setup complete! Virtual environment created and dependencies installed.
pause
goto menu

:install_deps
echo.
echo Installing dependencies...
if not exist ".venv" (
    echo ERROR: Virtual environment not found. Please run setup first.
    pause
    goto menu
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if exist "requirements-dev.txt" (
    pip install -r requirements-dev.txt
)

echo Dependencies installed successfully.
pause
goto menu

:run_tests
echo.
echo Running tests...
if not exist ".venv" (
    echo ERROR: Virtual environment not found. Please run setup first.
    pause
    goto menu
)

call .venv\Scripts\activate.bat

REM Set PYTHONPATH to include project root (Windows equivalent of export PYTHONPATH=$(pwd))
set PYTHONPATH=%PROJECT_ROOT%

REM Run pytest
pytest -q
if errorlevel 1 (
    echo Tests failed with errors
) else (
    echo All tests passed!
)
pause
goto menu

:run_linting
echo.
echo Running code linting with flake8...
if not exist ".venv" (
    echo ERROR: Virtual environment not found. Please run setup first.
    pause
    goto menu
)

call .venv\Scripts\activate.bat
flake8
if errorlevel 1 (
    echo Linting found issues
) else (
    echo Code passes linting checks!
)
pause
goto menu

:start_app
echo.
echo Starting OfflineManager application...
if not exist ".venv" (
    echo ERROR: Virtual environment not found. Please run setup first.
    pause
    goto menu
)

call .venv\Scripts\activate.bat
set PYTHONPATH=%PROJECT_ROOT%

REM Look for main entry points in order of preference
if exist "main.py" (
    echo Found main.py, starting application...
    python main.py
) else if exist "app_launcher.py" (
    echo Found app_launcher.py, starting application...
    python app_launcher.py
) else if exist "automotive_invoice_manager\ui\app.py" (
    echo Found automotive_invoice_manager\ui\app.py, running as module...
    REM Run as module to fix relative import issues
    python -c "import sys; sys.path.append('.'); from automotive_invoice_manager.ui.app import FullScreenLoginApp; app = FullScreenLoginApp(); app.run()"
) else if exist "app.py" (
    echo Found app.py, starting application...
    python app.py
) else if exist "automotive_invoice_manager\__main__.py" (
    echo Found __main__.py, starting as module...
    python -m automotive_invoice_manager
) else (
    echo No main entry point found. 
    echo.
    echo Based on your project structure, try creating one of these files:
    echo 1. main.py (comprehensive launcher^)
    echo 2. app_launcher.py (simple launcher^)
    echo.
    echo Or run manually:
    echo python -c "import sys; sys.path.append('.'); from automotive_invoice_manager.ui.app import FullScreenLoginApp; app = FullScreenLoginApp(); app.run()"
)
pause
goto menu

:clean
echo.
echo Cleaning development environment...
set /p confirm="Are you sure you want to delete the virtual environment? (y/N): "
if /i "%confirm%"=="y" (
    if exist ".venv" (
        echo Removing virtual environment...
        rmdir /s /q ".venv"
        echo Virtual environment removed.
    ) else (
        echo No virtual environment found.
    )
    
    REM Clean Python cache files
    echo Cleaning Python cache files...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f"
    for /r . %%f in (*.pyo) do @if exist "%%f" del /q "%%f"
    
    echo Cleanup complete.
) else (
    echo Cleanup cancelled.
)
pause
goto menu

:exit
echo.
echo Goodbye!
exit /b 0

REM Error handling
:error
echo An error occurred. Please check the output above.
pause
goto menu