@echo off

where cloudflared

if errorlevel 1 (
    echo.
    echo Cloudflared 未安装。
    echo 请下载：
    echo https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
    pause
    exit
)

cloudflared tunnel --url http://localhost:5000

pause
