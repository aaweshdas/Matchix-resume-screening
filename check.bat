@echo off
setlocal enabledelayedexpansion
title Candidate-Job Matching - Health Check

echo ======================================================================
echo           RESUME SCREENING ^& CANDIDATE-JOB MATCHING SYSTEM
echo                         SYSTEM HEALTH CHECK
echo ======================================================================
echo.

:: Detect Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH.
    echo Please install Python 3.9+ and make sure "Add Python to PATH" is checked.
    echo.
    pause
    exit /b 1
)

:: Run health_check.py
python health_check.py
set CHECK_EXIT=%errorlevel%

echo.
if %CHECK_EXIT% equ 0 (
    echo [SUCCESS] Everything is working properly!
) else (
    echo [WARNING] One or more components need attention.
)
echo.
pause
exit /b %CHECK_EXIT%
