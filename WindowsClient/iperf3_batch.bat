@echo off
@echo Iperf3 Continuous Logging CLIENT SCRIPT
@echo 

SET DESTFOLDER=%USERPROFILE%\Iperf3ContinuousLogging
SET MEAS_INTERVAL_SEC=60
SET IPERF3_SERVER_ADDRESS=172.20.52.153


@echo off
goto check_Permissions

:check_Permissions
    echo Administrative permissions required. Detecting permissions...
    
    net session >nul 2>&1
    if %errorLevel% == 0 (
        echo Success: Administrative permissions confirmed.
    ) else (
        echo Failure: Current permissions inadequate. Please right-click and select "Run as Administrator". Hit a key to exit.
        pause >nul
        exit 2
    )
    


mkdir %DESTFOLDER%
@echo Results will be saved in %DESTFOLDER%



:LOOP
cls
set hr=%time:~0,2%
if "%hr:~0,1%" equ " " set hr=0%hr:~1,1%
REM SET LOGFILE=%date:~-4,4%_%date:~-7,2%_%date:~-10,2%__%hr%_%time:~3,2%_%time:~6,2%.log
SET LOGFILE=%date:~-4,4%_%date:~-7,2%_%date:~-10,2%__%hr%_%time:~3,2%

echo.
echo JSON output will be saved in %DESTFOLDER%\%LOGFILE%_upload.json
echo Now testing UPLOAD speed
cd %DESTFOLDER%
iperf3.exe --format m --client %IPERF3_SERVER_ADDRESS% --parallel 1 --json > %DESTFOLDER%\%LOGFILE%_upload.json
echo Done

echo.
echo JSON output will be saved in %DESTFOLDER%\%LOGFILE%_download.json
echo Now testing DOWNLOAD speed
iperf3.exe --format m --client %IPERF3_SERVER_ADDRESS% --parallel 1 --json --reverse >> %DESTFOLDER%\%LOGFILE%_download.json
echo Done

echo.
echo Now sleeping for %MEAS_INTERVAL_SEC%sec before next measurement
timeout /T %MEAS_INTERVAL_SEC% /NOBREAK
if not ErrorLevel 1 goto :LOOP
