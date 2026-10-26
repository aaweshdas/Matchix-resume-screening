@echo off
setlocal
title MATCHIX v3.0 — Resume Screening Full-Stack App
cd /d "%~dp0"

echo ======================================================================
echo           MATCHIX v3.0 -- Full-Stack Modern Web Application
echo ======================================================================
echo Starting Flask REST API Backend on http://localhost:5000...
start "MATCHIX-Backend" /min cmd /c "python server.py"

echo Starting Vite React Frontend on http://localhost:5173...
cd frontend
start "MATCHIX-Frontend" /min cmd /c "npm run dev"

echo.
echo ======================================================================
echo Both servers started!
echo Frontend UI: http://localhost:5173
echo Backend API: http://localhost:5000
echo ======================================================================
echo Press any key to open browser...
pause >nul
start http://localhost:5173
