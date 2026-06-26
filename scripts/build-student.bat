@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0\.."

echo [1/3] 安装/更新学生端后端依赖...
cd packages\student-backend
pip install -r requirements.txt
if errorlevel 1 goto error

echo [2/3] 打包学生端后端...
pyinstaller main.spec --noconfirm
if errorlevel 1 goto error

cd ..\student-app

echo [3/3] 安装学生端前端依赖并打包...
npm install
if errorlevel 1 goto error
npm run build:win
if errorlevel 1 goto error

echo 学生端打包完成，产物位于 packages\student-app\release
pause
goto eof

:error
echo 打包失败，请检查错误信息。
pause
exit /b 1

:eof
