@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0\.."

echo [1/3] Installing/updating student backend dependencies...
cd packages\student-backend
pip install -r requirements.txt
if errorlevel 1 goto error

echo [2/3] Packaging student backend...
pyinstaller main.spec --noconfirm
if errorlevel 1 goto error

cd ..\student-app

echo [3/3] Installing student frontend dependencies and packaging...
npm install
if errorlevel 1 goto error
npm run build:win
if errorlevel 1 goto error

echo Student build complete, output at packages\student-app\release
pause
goto eof

:error
echo Build failed, check errors above.
pause
exit /b 1

:eof
