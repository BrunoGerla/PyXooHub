@echo off
cd /d "%~dp0"

:: start app
uv run src/app.py

pause