@echo off
chcp 65001 >nul
echo [Restart] 结束旧学生端后端...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo [Restart] 启动新学生端后端...
cd /d d:\A_CODE_WORK\network-control-v2\packages\student-backend
python -m app.main > d:\A_CODE_WORK\network-control-v2\packages\student-backend\student-backend-admin.log 2>&1
