@echo off
cd /d "%~dp0"

:: Activate the virtual environment
call .venv/Scripts/activate.bat

python src/app.py

pause