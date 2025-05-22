from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from src.config.database import get_db
from src.models.user import User, UserRole
from src.schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientList
from src.services import client_service
from src.utils.security import get_current_user

router = APIRouter(prefix="/clients", tags=["Clientes"])


@router.get("", response_model=ClientList)
async def list_clients(
    name: Optional[str] = None,
    email: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return client_service.create_client(db=db, client=client)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return client_service.get_client(db=db, client_id=client_id)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return client_service.update_client(db=db, client_id=client_id, client=client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se o usuário é admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir clientes"
        )

    client_service.delete_client(db=db, client_id=client_id)
    return None
