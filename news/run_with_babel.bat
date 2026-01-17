@echo off
echo 🌍 Flask-Babel EcoNews Setup
echo =============================

REM Check virtual environment paths
set VENV_PATH=..\..\.venv
set VENV_PIP=%VENV_PATH%\Scripts\pip.exe
set VENV_PYTHON=%VENV_PATH%\Scripts\python.exe

echo 🔍 Checking virtual environment...
if exist "%VENV_PIP%" (
    echo ✅ Virtual environment found
    echo 📦 Installing Flask-Babel...
    "%VENV_PIP%" install Flask-Babel==3.1.0
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Flask-Babel installed successfully!
        echo 🚀 Starting application with virtual environment...
        "%VENV_PYTHON%" app.py
    ) else (
        echo ❌ Installation failed in virtual environment
        echo 🔄 Trying with system pip...
        python -m pip install Flask-Babel==3.1.0
        echo 🚀 Starting application with system Python...
        python app.py
    )
) else (
    echo ❌ Virtual environment not found at %VENV_PATH%
    echo 🔄 Installing with system pip...
    python -m pip install Flask-Babel==3.1.0
    echo 🚀 Starting application with system Python...
    python app.py
)

pause
