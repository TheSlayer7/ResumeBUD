@echo off
echo ==============================================
echo   Smart Resume Screener - Setup and Run
echo ==============================================
echo.

IF NOT EXIST ".venv" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo [1/3] Virtual environment already exists.
)

echo [2/3] Installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

IF NOT EXIST ".env" (
    echo [3/3] Creating default .env file...
    copy .env.example .env
) ELSE (
    echo [3/3] .env file already exists.
)

echo.
echo ==============================================
echo Setup complete! Starting the server...
echo Access the dashboard at http://127.0.0.1:8000
echo Press Ctrl+C to stop.
echo ==============================================
echo.
python run.py
pause
