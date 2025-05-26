import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL do banco de dados do arquivo .env
DATABASE_URL = os.environ.get("DATABASE_URL")
print(f"DATABASE_URL carregada do .env: {DATABASE_URL}")

try:
    # Tenta criar uma conexão com o banco de dados
    engine = create_engine(DATABASE_URL)
    
    # Testa a conexão executando uma consulta simples
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Conexão com o banco de dados estabelecida com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
