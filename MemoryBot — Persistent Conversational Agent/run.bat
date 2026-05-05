@echo off
title MemoryBot Launcher
echo.
echo  ========================================
echo   MemoryBot -- Persistent Memory Chatbot
echo  ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Install from python.org
    pause
    exit /b 1
)

echo.
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo [3/4] Installing dependencies (first run takes a few minutes)...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Install failed. See above for details.
    pause
    exit /b 1
)

echo.
echo [4/4] Launching MemoryBot...
echo  App will open at http://localhost:8501
echo  Press Ctrl+C in this window to stop.
echo.
python -m streamlit run app.py
pause
