 @echo off
cd /d "%~dp0"
uv sync --dev
uv run python main.py %*