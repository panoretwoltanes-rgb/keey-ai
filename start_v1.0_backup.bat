@echo off
cd /d "%~dp0"
start "Flask" cmd /k python app.py
timeout /t 5
start "Tunnel" cmd /k cloudflared tunnel --url http://127.0.0.1:5000
