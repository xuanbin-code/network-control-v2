@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0.."
set "BACKEND=%ROOT%\packages\student-backend"

cd /d "%BACKEND%"

if not exist "dist\student-backend.exe" (
    echo Run build-student.bat first to package the student app
    exit /b 1
)

echo Installing Windows service NetControlAgent...
dist\student-backend.exe install
if errorlevel 1 (
    echo Service install failed, run as administrator
    exit /b 1
)

dist\student-backend.exe start
echo Service installed and started
