@echo off
cd /d "%~dp0"

:: Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate

:: Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Run the app
echo Running image_converter.py...
python image_converter.py

pause
