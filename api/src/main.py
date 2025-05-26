from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import auth, client, order, product

app = FastAPI(
    title="Lu Estilo API",
    description="""
    ## API para Gerenciamento de Vendas da Lu Estilo

    Esta API fornece endpoints para gerenciar:

    * **Autenticação** - Login, registro e renovação de tokens
    * **Clientes** - CRUD completo de clientes
    * **Produtos** - Gerenciamento de estoque e catálogo
    * **Pedidos** - Criação e acompanhamento de vendas

    ### Autenticação
    
    A API utiliza **JWT (JSON Web Tokens)** para autenticação. Para acessar endpoints protegidos:
    
    1. Faça login em `/auth/login` com suas credenciais
    2. Use o token retornado no header `Authorization: Bearer <token>`
    
    ### Permissões
    
    - **Usuários comuns**: Podem visualizar produtos, criar e gerenciar pedidos
    - **Administradores**: Têm acesso completo, incluindo criação/edição de produtos
    
    ### Filtros e Paginação
    
    Muitos endpoints suportam filtros e paginação para facilitar a navegação dos dados.
    """,
    version="1.0.0"
)

# Configuração de CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique as origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(client.router)
app.include_router(product.router)
app.include_router(order.router)


@app.get("/", tags=["🏠 Informações"], summary="Informações da API", description="Retorna informações básicas sobre a API e links úteis.")
async def root():
    """
    Endpoint de boas-vindas com informações básicas da API.
    """
    return {
        "message": "Bem-vindo à API da Lu Estilo",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "description": "API para gerenciamento de vendas de moda feminina"
    }


@app.get("/health", tags=["🏠 Informações"], summary="Status da API", description="Verifica se a API está funcionando corretamente.")
async def health_check():
    """
    Endpoint para verificar a saúde da API.
    Útil para monitoramento e load balancers.
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-20T10:30:00Z",
        "service": "Lu Estilo API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
