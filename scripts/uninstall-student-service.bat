@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0.."
set "BACKEND=%ROOT%\packages\student-backend"

cd /d "%BACKEND%"

if not exist "dist\student-backend.exe" (
    echo Student app not found
    exit /b 1
)

dist\student-backend.exe stop
dist\student-backend.exe remove
echo Service uninstalled
