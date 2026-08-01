@echo off
chcp 65001 >nul
cd /d "%~dp0"

where cloudflared >nul 2>&1
if errorlevel 1 (
    echo.
    echo [错误] cloudflared 未安装。
    echo 请下载 cloudflared-windows-amd64.exe 并改名为 cloudflared.exe
    echo 放到 C:\Windows\System32
    echo.
    echo 下载地址:
    echo https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
    echo.
    pause
    exit
)

echo ==========================================
echo   KEEY AI 报价系统 - 一键启动
echo ==========================================
echo.

echo [1/2] 启动 Flask 服务器...
start "KEEY Flask Server" cmd /k "cd /d %~dp0 && python app.py"

echo 等待 Flask 启动...
timeout /t 3 /nobreak >nul

echo [2/2] 启动 Cloudflare Tunnel...
start "KEEY Cloudflare Tunnel" cmd /k "cd /d %~dp0 && cloudflared tunnel --url http://localhost:5000"

echo.
echo 请在 Cloudflare Tunnel 窗口查看公网地址：
echo https://xxxxx.trycloudflare.com
echo.
echo 手机 5G / WiFi 均可访问。
echo 关闭窗口即停止服务。
echo.
pause
