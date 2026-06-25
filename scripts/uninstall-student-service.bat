@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0.."
set "BACKEND=%ROOT%\packages\student-backend"

cd /d "%BACKEND%"

if not exist "dist\student-backend.exe" (
    echo 未找到学生端程序
    exit /b 1
)

dist\student-backend.exe stop
dist\student-backend.exe remove
echo 服务已卸载
