@echo off
REM IMPORTANT: Replace "C:\path\to\your\project" with the actual path to your project folder.
cd /d "C:\path\to\your\project"

echo Running Python syntax check on jarvis.py...
python -m py_compile jarvis.py
if %errorlevel% neq 0 (
    echo Python syntax check failed. Exiting.
    exit /b %errorlevel%
)

echo Running Pip dependency check...
pip list
if %errorlevel% neq 0 (
    echo Pip dependency check failed. Exiting.
    exit /b %errorlevel%
)

echo All checks passed. Running git status...
git status