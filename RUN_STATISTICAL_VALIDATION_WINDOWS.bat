@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  .venv\Scripts\python.exe -m pip install --upgrade pip
  .venv\Scripts\python.exe -m pip install -r requirements.txt
)
.venv\Scripts\python.exe code\legacy\circular_shift_validation_REVISED.py data\root_catalogue\Planetary_Coincidences_STATISTICAL_VALIDATION_EN_REVISED.xlsx --trials 1000000 --seed 20260804 --sensitivity-csv outputs\circular_shift_sensitivity_legacy_windows.csv
.venv\Scripts\python.exe code\circular_shift_validation_from_csv.py data\root_catalogue --trials 1000000 --seed 20260804 --sensitivity-csv outputs\circular_shift_sensitivity_csv_windows.csv
.venv\Scripts\python.exe -m pytest -q
pause
