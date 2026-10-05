@echo off
chcp 65001 >nul
cd /d "%~dp0.."
set PY=pythonw.exe
if exist "%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe"
%PY% "SETUP\mobil_setup.py"
exit /b