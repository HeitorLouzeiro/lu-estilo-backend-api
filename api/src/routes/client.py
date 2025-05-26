from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User, UserRole
from src.schemas.client import (ClientCreate, ClientList, ClientResponse,
                                ClientUpdate)
from src.services import client_service
from src.utils.security import get_current_user

router = APIRouter(
    prefix="/clients",
    tags=["👥 Clientes"],
    responses={
        404: {"description": "Cliente não encontrado"},
        400: {"description": "Dados inválidos"},
    }
)


@router.get("", response_model=ClientList, summary="Listar clientes", description="Retorna uma lista paginada de clientes cadastrados, com filtros por nome e email.", response_description="Lista de clientes.")
async def list_clients(
    name: Optional[str] = None,
    email: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista clientes cadastrados.
    - **name**: Filtra clientes pelo nome
    - **email**: Filtra clientes pelo email
    - **page**: Página da paginação
    - **size**: Tamanho da página
    """
    skip = (page - 1) * size
    clients, total = client_service.get_clients(
        db=db,
        skip=skip,
        limit=size,
        name=name,
        email=email
    )

    return {
        "items": clients,
        "total": total,
        "page": page,
        "size": size
    }


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, summary="Criar cliente", description="Cria um novo cliente no sistema.", response_description="Dados do cliente criado.")
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo cliente.
    - **client**: Dados do cliente a ser criado
    """
    return client_service.create_client(db=db, client=client)


@router.get("/{client_id}", response_model=ClientResponse, summary="Obter cliente", description="Retorna os dados de um cliente pelo ID.", response_description="Dados do cliente.")
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca um cliente pelo ID.
    - **client_id**: ID do cliente
    """
    return client_service.get_client(db=db, client_id=client_id)


@router.put("/{client_id}", response_model=ClientResponse, summary="Atualizar cliente", description="Atualiza os dados de um cliente existente.", response_description="Dados do cliente atualizado.")
async def update_client(
    client_id: int,
    client: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um cliente existente.
    - **client_id**: ID do cliente
    - **client**: Novos dados do cliente
    """
    return client_service.update_client(db=db, client_id=client_id, client=client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir cliente", description="Remove um cliente do sistema pelo ID.")
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exclui um cliente pelo ID.
    - **client_id**: ID do cliente
    """
    # Verificar se o usuário é admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir clientes"
        )

    client_service.delete_client(db=db, client_id=client_id)
    return None
