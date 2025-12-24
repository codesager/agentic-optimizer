@echo off
REM Setup script for creating virtual environment and installing dependencies

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Trying python3...
    python3 -m venv venv
    if errorlevel 1 (
        echo Trying py launcher...
        py -m venv venv
        if errorlevel 1 (
            echo ERROR: Could not create virtual environment.
            echo Please ensure Python is installed and in your PATH.
            pause
            exit /b 1
        )
    )
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
pause

