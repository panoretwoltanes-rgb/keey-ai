@echo off
cd /d "%~dp0"

echo KEEY AI Quote System
echo.

REM Check cloudflared
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo [ERROR] cloudflared not found.
    echo Download cloudflared-windows-amd64.exe, rename to cloudflared.exe
    echo put in C:\Windows\System32
    echo https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/3] Starting Flask...
start "KEEY Flask Server" cmd /k "cd /d %~dp0 && python app.py"
echo [OK]
echo.

echo [2/3] Waiting port 5000...
set /a tries=0
:wait_port
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto port_ready
timeout /t 1 /nobreak >nul
set /a tries+=1
if %tries% GEQ 30 (
    echo [ERROR] Port 5000 did not start within 30 seconds.
    echo Check the Flask window.
    pause
    exit /b 1
)
goto wait_port
:port_ready
echo [OK]
echo.

echo [3/3] Starting Cloudflare Tunnel...
start "KEEY Cloudflare Tunnel" cmd /k "cd /d %~dp0 && cloudflared tunnel --url http://127.0.0.1:5000"
echo [OK]
echo.

echo ==========================================
echo Copy the public URL from the Tunnel window:
echo https://xxxxx.trycloudflare.com
echo ==========================================
pause
