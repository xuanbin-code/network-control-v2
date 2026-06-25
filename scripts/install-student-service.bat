@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0.."
set "BACKEND=%ROOT%\packages\student-backend"

cd /d "%BACKEND%"

if not exist "dist\student-backend.exe" (
    echo 请先运行 build-student.bat 打包学生端
    exit /b 1
)

echo 正在安装 Windows 服务 NetControlAgent...
dist\student-backend.exe install
if errorlevel 1 (
    echo 服务安装失败，请以管理员身份运行
    exit /b 1
)

dist\student-backend.exe start
echo 服务安装并启动完成
