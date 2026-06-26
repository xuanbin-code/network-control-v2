@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0\.."

echo [1/3] 安装/更新教师端后端依赖...
cd packages\teacher-backend
pip install -r requirements.txt
if errorlevel 1 goto error

echo [2/3] 打包教师端后端...
pyinstaller main.spec --noconfirm
if errorlevel 1 goto error

cd ..\teacher-app

echo [3/3] 安装教师端前端依赖并打包...
npm install
if errorlevel 1 goto error
npm run build:win
if errorlevel 1 goto error

echo 教师端打包完成，产物位于 packages\teacher-app\release
pause
goto eof

:error
echo 打包失败，请检查错误信息。
pause
exit /b 1

:eof
