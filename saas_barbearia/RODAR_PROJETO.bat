@echo off
cd /d %~dp0
python -m pip install --user -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8080
pause
