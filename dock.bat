@echo off

set base=-f docker-compose.yml

if "%1"=="dev" goto dev
if "%1"=="prod" goto prod
goto help

:dev
set layer=%base% -f docker-compose.dev.yml
goto second_arg

:prod
set layer=%base% -f docker-compose.prod.yml
goto second_arg

:second_arg
if "%2"=="up" goto up
if "%2"=="down" goto down
goto help

:up
docker compose %layer% up --build
goto exit

:down
docker compose %layer% down
goto exit

:help
echo Usage: dock.bat [dev^|prod] [up^|down]

:exit