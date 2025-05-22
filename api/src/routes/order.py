from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.config.database import get_db
from src.models.user import User, UserRole
from src.models.order import OrderStatus
from src.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderList
from src.services import order_service
from src.utils.security import get_current_user

router = APIRouter(prefix="/orders", tags=["Pedidos"])


@router.get("", response_model=OrderList)
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


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.create_order(db=db, order=order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.get_order(db=db, order_id=order_id)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.update_order(db=db, order_id=order_id, order=order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se o usuário é admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir pedidos"
        )

    order_service.delete_order(db=db, order_id=order_id)
    return None
