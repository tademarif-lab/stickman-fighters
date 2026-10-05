@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title STICKMAN FIGHTERS - APK DERVEE

echo ============================================================
echo   ANDROID APK DERVESI
echo   WSL Ubuntu uzerinde calisir.
echo ============================================================

wsl -e bash -lc "cd '$(wslpath -m "%CD%" 2>nul || echo /mnt/c)' 2>/dev/null; true"

REM WSL'e kurulum
wsl -e bash -lc "sudo apt-get update -qq && sudo apt-get install -y -qq --no-install-recommends git zip unzip openjdk-17-jdk python3-pip ccache libffi-dev libssl-dev build-essential autoconf libtool pkg-config zlib1g-dev libbz2-dev libncurses-dev libncursesw5-dev xz-utils libjpeg-dev cmake; echo WSL_HAZIR"

if errorlevel 1 (
  echo.
  echo WSL kurulu degil. Once: wsl --install -d Ubuntu
  echo Sonra bu dosyayi tekrar calistir.
  pause
  exit /b 1
)

WSL_PATH=$(wsl wslpath -a "%CD%")
wsl -e bash -lc "cd '$(WSL_PATH)' && bash ANDROID/build_apk.sh"

echo.
echo Bitti! APK klasoru: APK_CIKTI
pause