@echo off
cd /d "%~dp0..\"
cloudflared tunnel --url http://127.0.0.1:5000 > "%~dp0..\tunnel.log" 2>&1
