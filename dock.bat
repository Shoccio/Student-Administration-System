@echo off
setlocal

set base=-f docker-compose.yml

if "%1"=="dev" (
    set layer=%base% -f docker-compose.dev.yml
) else if "%1"=="prod" (
    set layer=%base% -f docker-compose.prod.yml
) else (
    goto help
)

:: Shift past the environment argument (dev/prod)
shift

:: If no command was provided after dev/prod, show help
if "%1"=="" goto help

:: Collect all remaining arguments into a variable
set "args="
:loop
if "%1"=="" goto run
set "args=%args% %1"
shift
goto loop

:run
docker compose %layer% %args%
goto exit

:help
echo Usage: dock.bat [dev^|prod] [command...]
echo Examples:
echo   dock.bat dev up --build
echo   dock.bat prod exec backend bash
echo   dock.bat dev logs -f

:exit