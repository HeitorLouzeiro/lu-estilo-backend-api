@echo off
echo ===========================================
echo       Lu Estilo API - Docker Setup
echo ===========================================
echo.

echo Parando containers existentes...
docker-compose down

echo.
echo Construindo e iniciando os containers...
docker-compose up --build

echo.
echo Aplicacao iniciada! Acesse:
echo API: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo.
pause
