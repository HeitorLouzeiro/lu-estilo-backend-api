from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from src.models.client import Client
from src.schemas.client import ClientCreate, ClientUpdate


def get_clients(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None
) -> tuple[List[Client], int]:
    query = db.query(Client)

    # Aplicar filtros se fornecidos
    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Client.email.ilike(f"%{email}%"))

    total = query.count()
    clients = query.offset(skip).limit(limit).all()

    return clients, total


def get_client(db: Session, client_id: int) -> Client:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {client_id} não encontrado"
        )
    return client


def create_client(db: Session, client: ClientCreate) -> Client:
    # Verificar se já existe cliente com mesmo email ou CPF
    existing_client = db.query(Client).filter(
        (Client.email == client.email) | (Client.cpf == client.cpf)
    ).first()

    if existing_client:
        if existing_client.email == client.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

    # Criar novo cliente
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: int, client: ClientUpdate) -> Client:
    db_client = get_client(db, client_id)

    # Verificar se o email já está em uso por outro cliente
    if client.email and client.email != db_client.email:
        existing = db.query(Client).filter(
            Client.email == client.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado para outro cliente"
            )

    # Atualizar apenas os campos fornecidos
    update_data = client.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)

    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> None:
    db_client = get_client(db, client_id)
    db.delete(db_client)
    db.commit()
