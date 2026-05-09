@echo off
cd /d %~dp0

echo Activate virtual space!
call C:\virtuals\my_venv\scripts\activate

echo Start python!
python main.py

pause