@echo off
setlocal

rem Get the directory of the batch file
set "batch_dir=%~dp0"

rem Navigate to the directory containing the main.py script
cd /d "%batch_dir%"

rem Execute the Python script
python main.py

endlocal