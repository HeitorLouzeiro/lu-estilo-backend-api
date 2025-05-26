@echo off
echo ===========================================
echo     Parando Lu Estilo API - Docker
echo ===========================================
echo.

echo Parando e removendo containers...
docker-compose down

echo.
echo Para remover tambem os volumes (dados do banco):
echo docker-compose down -v
echo.
pause
