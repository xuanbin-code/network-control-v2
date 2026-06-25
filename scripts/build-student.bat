@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "ROOT=%~dp0.."
cd /d "%ROOT%"

:: 使用国内镜像下载 Electron
set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/

echo ========================================
echo  打包学生端
echo ========================================

:: 1. 打包 Python 后端
set "BACKEND=%ROOT%\packages\student-backend"
cd /d "%BACKEND%"

if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

python -m pip install -r requirements.txt --quiet
python -m PyInstaller --noconfirm --onefile --name student-backend --console app/main.py
if errorlevel 1 (
    echo Python 后端打包失败
    exit /b 1
)

:: 2. 打包 Electron 前端
set "APP=%ROOT%\packages\student-app"
cd /d "%APP%"

call npm install
if errorlevel 1 (
    echo npm install 失败
    exit /b 1
)

call npm run build:win
if errorlevel 1 (
    echo Electron 打包失败
    exit /b 1
)

echo ========================================
echo  学生端打包完成
echo  产物目录: %APP%\release
