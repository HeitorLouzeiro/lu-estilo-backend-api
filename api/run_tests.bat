@echo off
REM Script para executar testes da API Lu Estilo

echo === Executando testes da API Lu Estilo ===
echo.

REM Configurar variáveis de ambiente para teste
set TEST_DATABASE_URL=sqlite:///./test_db.sqlite
set SECRET_KEY=testingsecretkey
set ACCESS_TOKEN_EXPIRE_MINUTES=30

REM Executar os testes com pytest
echo Executando todos os testes...
pytest -xvs tests/

echo.
echo === Testes específicos ===
echo Para executar um teste específico, use:
echo run_tests.bat [nome_do_arquivo_de_teste] [nome_do_teste]
echo.
echo Exemplos:
echo run_tests.bat test_auth.py
echo run_tests.bat test_clients.py test_create_client

REM Verifica se foram passados argumentos para testes específicos
if not "%1"=="" (
    if not "%2"=="" (
        echo Executando teste específico: %1::%2
        pytest -xvs tests/%1::%2
    ) else (
        echo Executando arquivo de teste: %1
        pytest -xvs tests/%1
    )
)

echo.
echo === Testes concluídos ===
