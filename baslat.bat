@echo off
title ElevatorPro - Baslatiliyor...

echo Python ortamı aktif ediliyor...
call venv\Scripts\activate.bat

echo Sunucu baslatiliyor...
start "" python manage.py runserver 8000

echo Sunucunun baslamasi bekleniyor...
timeout /t 5 /nobreak >nul

echo Tarayici aciliyor...
start http://127.0.0.1:8000

echo.
echo Sunucu calisiyor. Acilan python penceresini kapatmayin.
echo Programi kapatmak icin Ctrl+C yapip pencereyi kapatabilirsiniz.
pause