@echo off
REM STICKMAN FIGHTERS - Kurulum ekranini terminal acmadan baslatir
cd /d "%~dp0"
set "PYW="
if exist "%LocalAppData%\Programs\Python\Python311\pythonw.exe" set "PYW=%LocalAppData%\Programs\Python\Python311\pythonw.exe"
for /f "delims=" %%p in ('where pythonw 2^>nul') do if not defined PYW set "PYW=%%p"
if defined PYW (
    start "" "%PYW%" "%~dp0setup.py"
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        start "" py -3 setup.py
    ) else (
        python setup.py
    )
)