@echo off
setlocal

set "SCRIPT_DIRECTORY=%~dp0"
set "PYTHON_EXECUTABLE=python"

if defined PYTHON (
    set "PYTHON_EXECUTABLE=%PYTHON%"
)

if exist "%SCRIPT_DIRECTORY%.venv\Scripts\python.exe" (
    set "PYTHON_EXECUTABLE=%SCRIPT_DIRECTORY%.venv\Scripts\python.exe"
)

if not exist "%SCRIPT_DIRECTORY%.venv\Scripts\python.exe" if exist "%SCRIPT_DIRECTORY%..\.venv\Scripts\python.exe" (
    set "PYTHON_EXECUTABLE=%SCRIPT_DIRECTORY%..\.venv\Scripts\python.exe"
)

pushd "%SCRIPT_DIRECTORY%" || exit /b 1

"%PYTHON_EXECUTABLE%" -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo Error: PyYAML is not installed for %PYTHON_EXECUTABLE%. 1>&2
    echo. 1>&2
    echo Create a project virtual environment and install the runtime dependencies: 1>&2
    echo   python -m venv .venv 1>&2
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt 1>&2
    popd
    exit /b 1
)

"%PYTHON_EXECUTABLE%" main.py %*
set "EXIT_STATUS=%ERRORLEVEL%"
popd

exit /b %EXIT_STATUS%
