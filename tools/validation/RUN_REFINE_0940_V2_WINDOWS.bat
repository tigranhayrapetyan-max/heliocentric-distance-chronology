@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" refine_940_horizons_v2.py
) else (
  python refine_940_horizons_v2.py
)
echo.
pause
