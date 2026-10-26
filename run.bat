@echo off
TITLE InterviewIQ — AI Interview Answer Analyzer Launch Script
SETLOCAL EnableDelayedExpansion

echo ===================================================
echo   InterviewIQ — AI Interview Answer Analyzer
echo ===================================================
echo.

:: 1. Check Python Availability
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10 or higher and try again.
    pause
    exit /b 1
)

echo [1/4] Checking Python environment...
python --version

:: 2. Create Virtual Environment if not exists
IF NOT EXIST ".venv" (
    echo [2/4] Creating virtual environment (.venv)...
    python -m venv .venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) ELSE (
    echo [2/4] Virtual environment (.venv) already exists.
)

:: 3. Activate Virtual Environment
echo [3/4] Activating virtual environment...
CALL .venv\Scripts\activate.bat

:: 4. Install Dependencies if needed
echo [4/4] Checking and installing required packages...
pip install -r requirements.txt --quiet

echo.
echo ===================================================
echo Starting InterviewIQ Streamlit Application...
echo ===================================================
echo.

streamlit run app.py

pause
