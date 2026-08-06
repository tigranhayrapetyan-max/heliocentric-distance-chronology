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

if not exist outputs mkdir outputs

echo.
echo FULL CATALOGUE GENERATION IS NETWORK-INTENSIVE AND MAY TAKE MANY HOURS.
echo Existing valid cache files will be reused if the run is restarted.
echo Do not delete the cache folder after an interruption.
echo.

.venv\Scripts\python.exe code\run_pipeline.py --start=-3999-01-01 --stop=2026-08-03 --chunk-size 64 --trials 1000000 > outputs\full_pipeline_run.log 2>&1
set EXITCODE=%ERRORLEVEL%
type outputs\full_pipeline_run.log

echo.
if "%EXITCODE%"=="0" (
  echo FULL PIPELINE COMPLETED.
  echo Please ZIP these files and folders for final review:
  echo   outputs\generated_roots
  echo   outputs\root_catalogue_comparison.json
  echo   outputs\root_catalogue_comparison_details.csv
  echo   outputs\control_case_validation_full_run.json
  echo   outputs\full_pipeline_run.log
) else (
  echo FULL PIPELINE STOPPED OR FAILED. Exit code: %EXITCODE%
  echo The log is outputs\full_pipeline_run.log
  echo You may run this BAT again; completed Horizons chunks remain cached.
)
echo.
pause
exit /b %EXITCODE%

:setup_error
echo Python environment setup failed.
pause
exit /b 1
