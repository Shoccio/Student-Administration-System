@ECHO off
set arg1=%1

if "%1"=="dev" GOTO :dev

if "%1" == "prod" GOTO :prod

echo Usage: .\dock dev - launch docker in development
echo Usage: .\dock prod - launch docker in production

GOTO :exit

:dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
GOTO :exit

:prod
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
GOTO :exit

:exit