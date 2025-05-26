# Use Python 3.12 como base
FROM python:3.12-slim

# Defina o diretório de trabalho
WORKDIR /app

# Instale dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copie o arquivo de requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instale as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação
COPY . .

# Defina variáveis de ambiente padrão
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Exponha a porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
