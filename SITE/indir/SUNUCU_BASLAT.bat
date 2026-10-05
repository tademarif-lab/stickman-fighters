@echo off
chcp 65001 >nul
cd /d "%~dp0"
title STICKMAN FIGHTERS - ONLINE SUNUCU
echo ============================================================
echo   STICKMAN FIGHTERS ONLINE SUNUCU
echo   En fazla 4 oyuncu. Arkadaslarin bu bilgisayarin IP'sine baglanir.
echo   IP adresi asagida yaziyor. Kapatmak icin Ctrl+C
echo ============================================================
python server.py %1
pause