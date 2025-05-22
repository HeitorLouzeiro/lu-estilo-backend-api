from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import auth

app = FastAPI(
    title="Lu Estilo API",
    description="API para gerenciamento de vendas da Lu Estilo",
    version="0.1.0"
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


@app.get("/")
async def root():
    return {"message": "Bem-vindo à API da Lu Estilo"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
