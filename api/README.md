# 🌸 Lu Estilo API

API REST para gerenciamento de vendas de moda feminina, desenvolvida com FastAPI, PostgreSQL e autenticação JWT.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso da API](#uso-da-api)
- [Documentação da API](#documentação-da-api)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Migrações de Banco](#migrações-de-banco)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Deploy](#deploy)
- [Contribuição](#contribuição)

## 🎯 Sobre o Projeto

A **Lu Estilo API** é uma solução backend robusta para gerenciamento de vendas de uma loja de moda feminina. O sistema oferece funcionalidades completas de CRUD para clientes, produtos e pedidos, com sistema de autenticação seguro e controle de permissões por roles.

### Principais Características

- ✅ **API RESTful** com documentação automática
- 🔐 **Autenticação JWT** com roles (admin/user)
- 📊 **CRUD completo** para todas as entidades
- 🔍 **Filtros e paginação** avançados
- 🐳 **Containerização** com Docker
- 🧪 **Testes automatizados** com cobertura completa
- 📈 **Migrações de banco** com Alembic
- 🛡️ **Validação de dados** com Pydantic
- 🌐 **CORS configurado** para frontend

## 🚀 Tecnologias Utilizadas

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno e rápido
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM para Python
- **[Alembic](https://alembic.sqlalchemy.org/)** - Migrações de banco de dados
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Validação de dados
- **[PassLib](https://passlib.readthedocs.io/)** - Hash de senhas
- **[Python-Jose](https://python-jose.readthedocs.io/)** - JWT tokens

### Banco de Dados
- **[PostgreSQL](https://www.postgresql.org/)** - Banco principal (produção)
- **[SQLite](https://www.sqlite.org/)** - Banco para testes

### DevOps e Testes
- **[Docker](https://www.docker.com/)** & **Docker Compose** - Containerização
- **[Pytest](https://docs.pytest.org/)** - Framework de testes
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI

## ⚡ Funcionalidades

### 🔐 Autenticação
- Registro de usuários com validação
- Login com JWT tokens
- Renovação de tokens
- Controle de acesso por roles (admin/user)

### 👥 Gerenciamento de Clientes
- Cadastro com validação de CPF e email
- Busca com filtros por nome e email
- Atualização de dados
- Paginação de resultados

### 📦 Gerenciamento de Produtos
- CRUD completo (apenas admins podem criar/editar)
- Controle de estoque
- Filtros por categoria, preço e disponibilidade
- Suporte a múltiplas imagens
- Data de validade para produtos perecíveis

### 🛒 Gerenciamento de Pedidos
- Criação de pedidos com múltiplos itens
- Cálculo automático de totais
- Acompanhamento de status (pending, confirmed, shipped, delivered, cancelled)
- Histórico completo de pedidos
- Filtros por cliente, data e status

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas bem definida:

```
src/
├── main.py              # Ponto de entrada da aplicação
├── config/              # Configurações (database, etc.)
├── models/              # Modelos SQLAlchemy (ORM)
├── schemas/             # Schemas Pydantic (validação)
├── routes/              # Endpoints da API
├── services/            # Lógica de negócio
└── utils/               # Utilitários (segurança, etc.)
```

### Padrões Utilizados
- **Repository Pattern** - Separação da lógica de acesso a dados
- **Service Layer** - Lógica de negócio centralizada
- **DTO Pattern** - Schemas Pydantic para transferência de dados
- **Dependency Injection** - Injeção de dependências do FastAPI

## 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Python 3.9+** (caso queira rodar localmente)
- **PostgreSQL** (caso não use Docker)

## 🔧 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd lu-estilo-backend-api/api
```

### 2. Configure as variáveis de ambiente
```bash
# Copie os arquivos de exemplo
cp .env.example .env
cp .env.docker.example .env.docker
```

### 3. Execute com Docker (Recomendado)
```bash
# Suba os serviços
docker-compose up -d

# Verifique os logs
docker-compose logs -f api
```

### 4. Ou execute localmente
```bash
# Instale as dependências
pip install -r requirements.txt

# Configure o banco local
export DATABASE_URL="postgresql://user:password@localhost/lu_estilo"

# Execute as migrações
alembic upgrade head

# Inicie o servidor
uvicorn src.main:app --reload
```

### 5. Verifique a instalação
- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 📚 Uso da API

### Autenticação

1. **Registre um usuário:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@luestilo.com",
    "password": "senha123",
    "role": "admin"
  }'
```

2. **Faça login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=senha123"
```

3. **Use o token nas requisições:**
```bash
curl -X GET "http://localhost:8000/products" \
  -H "Authorization: Bearer <seu-token-jwt>"
```

### Exemplos de Uso

#### Criar um cliente
```bash
curl -X POST "http://localhost:8000/clients" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Silva Santos",
    "email": "maria@email.com",
    "cpf": "12345678901",
    "phone": "(11) 99999-8888",
    "address": "Rua das Flores, 123, São Paulo - SP"
  }'
```

#### Criar um produto (admin apenas)
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Vestido Floral Verão",
    "price": 89.90,
    "section": "Roupas Femininas",
    "stock": 15,
    "barcode": "7891234567890"
  }'
```

#### Criar um pedido
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ]
  }'
```

## 📖 Documentação da API

A API possui documentação interativa automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/auth/register` | Registrar usuário | ❌ |
| POST | `/auth/login` | Login | ❌ |
| POST | `/auth/refresh-token` | Renovar token | ✅ |
| GET | `/clients` | Listar clientes | ✅ |
| POST | `/clients` | Criar cliente | ✅ |
| GET | `/clients/{id}` | Obter cliente | ✅ |
| PUT | `/clients/{id}` | Atualizar cliente | ✅ |
| DELETE | `/clients/{id}` | Excluir cliente | ✅ |
| GET | `/products` | Listar produtos | ✅ |
| POST | `/products` | Criar produto | ✅ (Admin) |
| GET | `/products/{id}` | Obter produto | ✅ |
| PUT | `/products/{id}` | Atualizar produto | ✅ (Admin) |
| DELETE | `/products/{id}` | Excluir produto | ✅ (Admin) |
| GET | `/orders` | Listar pedidos | ✅ |
| POST | `/orders` | Criar pedido | ✅ |
| GET | `/orders/{id}` | Obter pedido | ✅ |
| PUT | `/orders/{id}` | Atualizar pedido | ✅ |
| DELETE | `/orders/{id}` | Excluir pedido | ✅ (Admin) |

## 🧪 Testes

O projeto possui uma suíte completa de testes automatizados.

### Executar todos os testes
```bash
# Com Docker
docker-compose exec api pytest

# Localmente
pytest
```

### Executar testes específicos
```bash
# Testes de autenticação
pytest tests/test_auth.py

# Testes com cobertura
pytest --cov=src tests/

# Testes verbosos
pytest -v
```

### Cobertura de Testes
- ✅ Autenticação e autorização
- ✅ CRUD de clientes
- ✅ CRUD de produtos
- ✅ CRUD de pedidos
- ✅ Validações de dados
- ✅ Regras de negócio
- ✅ Segurança (JWT, CORS, etc.)

## 📁 Estrutura do Projeto

```
lu-estilo-backend-api/
├── README.md
├── requirements.txt          # Dependências Python
├── Dockerfile               # Container da aplicação
├── docker-compose.yml       # Orquestração dos serviços
├── docker-compose.dev.yml   # Configuração de desenvolvimento
├── alembic.ini             # Configuração do Alembic
├── pytest.ini             # Configuração dos testes
├── .env                    # Variáveis de ambiente (local)
├── .env.docker            # Variáveis de ambiente (Docker)
├── .env.test              # Variáveis de ambiente (testes)
├── migrations/            # Migrações do banco de dados
│   ├── env.py
│   └── versions/
├── src/                   # Código fonte da aplicação
│   ├── main.py           # Ponto de entrada
│   ├── config/           # Configurações
│   │   └── database.py
│   ├── models/           # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── product.py
│   │   └── order.py
│   ├── schemas/          # Schemas Pydantic
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── product.py
│   │   └── order.py
│   ├── routes/           # Endpoints da API
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── product.py
│   │   └── order.py
│   ├── services/         # Lógica de negócio
│   │   ├── client_service.py
│   │   ├── product_service.py
│   │   └── order_service.py
│   └── utils/            # Utilitários
│       └── security.py
└── tests/                # Testes automatizados
    ├── conftest.py       # Configurações de teste
    ├── test_auth.py
    ├── test_clients.py
    ├── test_products.py
    ├── test_orders.py
    ├── test_security.py
    └── test_services.py
```

## 🗄️ Migrações de Banco

O projeto usa **Alembic** para versionamento do banco de dados.

### Comandos Úteis
```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrações
alembic upgrade head

# Voltar uma migração
alembic downgrade -1

# Ver histórico
alembic history

# Ver migração atual
alembic current
```

### Modelos Principais
- **User**: Usuários do sistema com roles
- **Client**: Clientes da loja
- **Product**: Produtos do catálogo
- **Order**: Pedidos de venda
- **OrderItem**: Itens dos pedidos

## 🔧 Variáveis de Ambiente

### Arquivo `.env` (desenvolvimento local)
```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/lu_estilo
SECRET_KEY=sua-chave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

### Arquivo `.env.docker` (Docker)
```env
DATABASE_URL=postgresql://postgres:admin@db:5432/lu_estilo
SECRET_KEY=sua-chave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

### Arquivo `.env.test` (testes)
```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=test-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

## 🚀 Deploy

### Deploy com Docker

1. **Ajuste as variáveis de produção:**
```bash
# Configure .env.docker com dados de produção
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=chave-super-segura-aleatoria
```

2. **Execute em produção:**
```bash
docker-compose -f docker-compose.yml up -d
```

### Deploy em Cloud

O projeto está pronto para deploy em:
- **Heroku** (com addon PostgreSQL)
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **DigitalOcean App Platform**

### Checklist de Produção
- [ ] Configurar CORS para domínios específicos
- [ ] Usar HTTPS
- [ ] Configurar logs estruturados
- [ ] Implementar health checks
- [ ] Configurar backup do banco
- [ ] Monitoramento e alertas

## 🤝 Contribuição

### Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões do Projeto

- **Código**: Seguir PEP 8
- **Commits**: Usar conventional commits
- **Testes**: Manter cobertura > 80%
- **Documentação**: Atualizar README e docstrings

## 📝 Licença

Este projeto é propriedade da **Lu Estilo** e destina-se a fins de avaliação técnica.

## 📞 Contato

- **Desenvolvedor**: [Seu Nome]
- **Email**: [seu.email@exemplo.com]
- **LinkedIn**: [seu-linkedin]

---

### 🏆 Diferenciais Técnicos

- ✨ **Arquitetura limpa** com separação de responsabilidades
- 🔒 **Segurança robusta** com JWT e hash de senhas
- 📊 **Documentação automática** com exemplos práticos
- 🧪 **100% testado** com casos de uso reais
- 🐳 **Containerizado** para facilitar deploy
- 📈 **Escalável** e pronto para produção
- 🔍 **Observabilidade** com logs e health checks

---
