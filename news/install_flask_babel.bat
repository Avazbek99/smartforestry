@echo off
echo 🔧 Installing Flask-Babel...
echo.

REM Try installing with pip
python -m pip install Flask-Babel

if %ERRORLEVEL% NEQ 0 (
    echo ✅ Flask-Babel installed successfully!
) else (
    echo ❌ Installation failed!
    echo Trying alternative method...
    
    REM Try installing with pip directly
    pip install Flask-Babel
)

echo.
echo 🎨 Compiling translations...
python -m pybabel compile -d translations

if %ERRORLEVEL% EQU 0 (
    echo ✅ Translations compiled successfully!
) else (
    echo ❌ Compilation failed!
)

echo.
echo 🚀 Starting Flask application...
python app.py

pause
