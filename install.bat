@echo off
:: Ensure pip is installed
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo pip could not be found, please install pip first.
    exit /b
)

:: Install the required packages
pip install -r requirements.txt
