from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.order import OrderStatus
from src.models.user import User, UserRole
from src.schemas.order import (OrderCreate, OrderList, OrderResponse,
                               OrderUpdate)
from src.services import order_service
from src.utils.security import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["🛒 Pedidos"],
    responses={
        404: {"description": "Pedido não encontrado"},
        400: {"description": "Dados inválidos"},
        403: {"description": "Acesso negado"},
    }
)


@router.get("", response_model=OrderList, summary="Listar pedidos", description="Retorna uma lista paginada de pedidos, com filtros por cliente, status, data e seção.", response_description="Lista de pedidos.")
async def list_orders(
    client_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    section: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista pedidos cadastrados.
    - **client_id**: Filtra por ID do cliente
    - **status**: Filtra por status do pedido
    - **start_date**: Data inicial
    - **end_date**: Data final
    - **section**: Filtra por seção
    - **page**: Página da paginação
    - **size**: Tamanho da página
    """
    skip = (page - 1) * size
    orders, total = order_service.get_orders(
        db=db,
        skip=skip,
        limit=size,
        client_id=client_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        section=section
    )

    return {
        "items": orders,
        "total": total,
        "page": page,
        "size": size
    }


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Criar pedido", description="Cria um novo pedido no sistema.", response_description="Dados do pedido criado.")
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo pedido.
    - **order**: Dados do pedido a ser criado
    """
    db_order = order_service.create_order(db=db, order=order)

    # Carregar explicitamente os itens antes de retornar
    db.refresh(db_order)

    # Converter para um formato que inclua os itens
    return {
        **db_order.__dict__,
        "items": [item.__dict__ for item in db_order.items]
    }


@router.get("/{order_id}", response_model=OrderResponse, summary="Obter pedido", description="Retorna os dados de um pedido pelo ID.", response_description="Dados do pedido.")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca um pedido pelo ID.
    - **order_id**: ID do pedido
    """
    return order_service.get_order(db=db, order_id=order_id)


@router.put("/{order_id}", response_model=OrderResponse, summary="Atualizar pedido", description="Atualiza os dados de um pedido existente.", response_description="Dados do pedido atualizado.")
async def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um pedido existente.
    - **order_id**: ID do pedido
    - **order**: Novos dados do pedido
    """
    return order_service.update_order(db=db, order_id=order_id, order=order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir pedido", description="Remove um pedido do sistema pelo ID. Apenas administradores podem acessar.")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exclui um pedido pelo ID.
    - **order_id**: ID do pedido
    """
    # Verificar se o usuário é admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir pedidos"
        )

    order_service.delete_order(db=db, order_id=order_id)
    return None
