@echo off
REM Quick start script for TophatC Clan Bot (Windows)

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo uv is not installed. Please install it first:
    echo   pip install uv
    echo Or visit: https://github.com/astral-sh/uv
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found!
    echo Please copy setup_example.env to .env and configure it:
    echo   copy setup_example.env .env
    echo   notepad .env
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
uv pip install -e .

REM Run the bot
echo Starting TophatC Clan Bot...
uv run bot.py

