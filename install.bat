@echo off
echo Please, DO NOT INTERRUPT this program. The installation will take a while.
call py -m venv venv
call venv\Scripts\activate
call pip install flask
call pip install python-dotenv
call pip install numpy
call pip install sounddevice
echo All modules have been installed. Press any button to close this window.
pause 