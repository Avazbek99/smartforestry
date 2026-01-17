@echo off
echo 🔧 Installing Flask-Babel in virtual environment...
echo.

REM Install Flask-Babel in virtual environment
..\..\.venv\Scripts\pip.exe install Flask-Babel==3.1.0

if %ERRORLEVEL% EQU 0 (
    echo ✅ Flask-Babel installed successfully!
) else (
    echo ❌ Installation failed!
)

echo.
echo 🚀 Starting Flask application with virtual environment...
..\..\.venv\Scripts\python.exe app.py

pause
