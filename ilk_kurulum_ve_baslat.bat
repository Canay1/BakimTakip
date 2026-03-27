@echo off
title ElevatorPro - Ilk Kurulum ve Baslatma

echo Python bulunuyor mu diye kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python yuklu degil! Lutfen https://www.python.org/downloads/ adresinden Python 3.12 kurun.
    echo Kurulumda "Add Python to PATH" secenegini isaretleyin.
    pause
    exit
)

echo Sanal ortam olusturuluyor...
if not exist venv (
    python -m venv venv
)

echo Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat

echo Gerekli paketler yukleniyor...
pip install --upgrade pip
pip install -r requirements.txt

echo Veritabani migrasyonlari uygulaniyor...
python manage.py makemigrations
python manage.py migrate

echo Superuser olusturuluyor (istege bagli, Ctrl+C ile atlayabilirsiniz)...
python manage.py createsuperuser

echo Kurulum tamamlandi!
echo Simdi sunucu baslatiliyor...

start "" python manage.py runserver 8000

timeout /t 5 /nobreak >nul

echo Tarayici aciliyor...
start http://127.0.0.1:8000

echo.
echo Sunucu calisiyor. Bu pencereyi kapatmayin.
echo Kapatmak icin Ctrl+C yapip pencereyi kapatabilirsiniz.
pause