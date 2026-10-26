@echo off
setlocal enabledelayedexpansion
title MATCHIX v3.0 — Resume Screening & Candidate Classification
cd /d "%~dp0"

:: Check for virtual environment and activate if present
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

:: Verify Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ======================================================================
    echo [ERROR] Python is not installed or not found in system PATH.
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo ======================================================================
    echo.
    pause
    exit /b 1
)

:: Check command line arguments for non-interactive execution
if /i "%~1"=="--app"   goto RUN_FULLSTACK
if /i "%~1"=="app"     goto RUN_FULLSTACK
if /i "%~1"=="--check" goto RUN_CHECK
if /i "%~1"=="check"   goto RUN_CHECK
if /i "%~1"=="--test"  goto RUN_SMOKE
if /i "%~1"=="test"    goto RUN_SMOKE
if /i "%~1"=="--bench" goto RUN_BENCH
if /i "%~1"=="bench"   goto RUN_BENCH

:MENU
cls
echo ======================================================================
echo           MATCHIX v3.0 -- RESUME SCREENING & CANDIDATE MATCHING
echo ======================================================================
echo.
echo   [1] Launch MATCHIX Full-Stack Web Application (localhost:5173)
echo   [2] Run System Health Check
echo   [3] Run Project Smoke Tests
echo   [4] Run Ground-Truth Benchmark Evaluation (75,000 Pairs)
echo   [5] Install / Update Dependencies (requirements.txt)
echo   [6] Exit
echo.
echo ======================================================================
set /p CHOICE="Enter your choice (1-6) [default: 1]: "

if "%CHOICE%"=="" set CHOICE=1
if "%CHOICE%"=="1" goto RUN_FULLSTACK
if "%CHOICE%"=="2" goto RUN_CHECK
if "%CHOICE%"=="3" goto RUN_SMOKE
if "%CHOICE%"=="4" goto RUN_BENCH
if "%CHOICE%"=="5" goto RUN_INSTALL
if "%CHOICE%"=="6" goto EXIT_SCRIPT

echo.
echo [!] Invalid selection "%CHOICE%". Please select a number between 1 and 6.
echo.
pause
goto MENU

:RUN_FULLSTACK
cls
echo ======================================================================
echo           LAUNCHING MATCHIX FULL-STACK MODERN WEB APPLICATION
echo ======================================================================
call run_fullstack.bat
if "%~1"=="" goto MENU
exit /b 0

:RUN_CHECK
cls
echo ======================================================================
echo                 RUNNING SYSTEM HEALTH CHECK
echo ======================================================================
python health_check.py
echo.
echo ======================================================================
pause
if "%~1"=="" goto MENU
exit /b %errorlevel%

:RUN_SMOKE
cls
echo ======================================================================
echo                   RUNNING PROJECT SMOKE TESTS
echo ======================================================================
python smoke_test.py
echo.
echo ======================================================================
pause
if "%~1"=="" goto MENU
exit /b %errorlevel%

:RUN_BENCH
cls
echo ======================================================================
echo           GROUND-TRUTH BENCHMARK EVALUATION (75,000 PAIRS)
echo ======================================================================
echo [*] Evaluating retrieval performance against ground truth...
python -m src.benchmark
echo.
echo ======================================================================
pause
if "%~1"=="" goto MENU
exit /b %errorlevel%

:RUN_INSTALL
cls
echo ======================================================================
echo                   INSTALLING DEPENDENCIES
echo ======================================================================
echo [*] Installing requirements from requirements.txt...
python -m pip install -r requirements.txt
echo.
echo ======================================================================
pause
if "%~1"=="" goto MENU
exit /b %errorlevel%

:EXIT_SCRIPT
echo.
echo Exiting MATCHIX v3.0. Have a great day!
exit /b 0
