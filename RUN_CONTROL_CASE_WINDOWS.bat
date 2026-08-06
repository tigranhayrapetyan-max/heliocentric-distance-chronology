@echo off
setlocal
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 goto :setup_error
  .venv\Scripts\python.exe -m pip install --upgrade pip
  if errorlevel 1 goto :setup_error
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto :setup_error
)

rem A control run is small, so always discard incomplete/stale cached responses.
if exist cache\horizons_control rmdir /s /q cache\horizons_control
if exist outputs\control rmdir /s /q outputs\control
mkdir outputs\control

.venv\Scripts\python.exe code\horizons_root_generation.py --start=-0140-01-01 --stop=-0137-12-31 --cache-dir cache\horizons_control --work-dir outputs\control --output-dir outputs\control\roots --chunk-size 64 --validate-control --log-level INFO > outputs\control\control_run.log 2>&1
set EXITCODE=%ERRORLEVEL%
type outputs\control\control_run.log

echo.
if "%EXITCODE%"=="0" (
  echo CONTROL CASE PASSED.
  echo Please ZIP the outputs\control folder and send it for final review.
) else (
  echo CONTROL CASE FAILED OR IS INCOMPLETE. Exit code: %EXITCODE%
  echo The diagnostic log is outputs\control\control_run.log
)
echo.
pause
exit /b %EXITCODE%

:setup_error
echo Python environment setup failed.
pause
exit /b 1
