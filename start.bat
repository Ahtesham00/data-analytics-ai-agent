@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: start.bat  –  Sets up and runs the Superstore AI Chatbot (Windows CMD)
:: ─────────────────────────────────────────────────────────────────────────────
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
:: Remove trailing backslash
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

set "VENV=%ROOT%\.venv"
set "BACKEND_PORT=5000"
set "FRONTEND_PORT=5173"

echo.
echo ══════════════════════════════════════════════════
echo   Superstore AI Chatbot  —  Setup ^& Start
echo ══════════════════════════════════════════════════
echo.

:: ── 4. Build and start Docker container (logs stream here) ───────────────────
echo.
echo ══════════════════════════════════════════════════
echo   Backend  ^→  http://localhost:%BACKEND_PORT%
echo   Frontend ^→  http://localhost:3000
echo   Health   ^→  http://localhost:%BACKEND_PORT%/api/health
echo.
echo   Ctrl+C stops the container.
echo ══════════════════════════════════════════════════
echo.

docker compose up --build
pause
endlocal
