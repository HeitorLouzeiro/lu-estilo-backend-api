from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.client import Client
from src.models.order import Order, OrderItem, OrderStatus, order_products
from src.models.product import Product
from src.schemas.order import OrderCreate, OrderUpdate


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    section: Optional[str] = None
) -> tuple[List[Order], int]:
    query = db.query(Order)

    # Aplicar filtros se fornecidos
    if client_id:
        query = query.filter(Order.client_id == client_id)
    if status:
        query = query.filter(Order.status == status)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    if section:
        # Filtrar pedidos que contêm produtos da seção especificada
        query = query.join(order_products).join(
            Product).filter(Product.section == section)

    total = query.count()
    orders = query.offset(skip).limit(limit).all()

    return orders, total


def get_order(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com ID {order_id} não encontrado"
        )
    return order


def create_order(db: Session, order: OrderCreate) -> Order:
    # Verificar se o cliente existe
    client = db.query(Client).filter(Client.id == order.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com ID {order.client_id} não encontrado"
        )

    # Verificar se há itens no pedido
    if not order.items or len(order.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O pedido deve conter pelo menos um item"
        )

    # Calcular o valor total e verificar estoque
    total_amount = 0
    order_items = []

    for item in order.items:
        product = db.query(Product).filter(
            Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item.product_id} não encontrado"
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto {product.description}"
            )

        # Atualizar estoque
        product.stock -= item.quantity

        # Adicionar ao valor total
        item_total = product.price * item.quantity
        total_amount += item_total

        # Adicionar à lista de itens do pedido
        order_items.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "unit_price": product.price
        })

    # Criar o pedido
    db_order = Order(
        client_id=order.client_id,
        status=order.status,
        total_amount=total_amount
    )
    db.add(db_order)
    db.flush()  # Para obter o ID do pedido antes de commit
    # Adicionar os itens do pedido
    for item in order_items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            unit_price=item["unit_price"]
        )
        db.add(order_item)

    db.commit()
    db.refresh(db_order)  # Refresh para atualizar o objeto com os dados atuais

    return db_order


def update_order(db: Session, order_id: int, order: OrderUpdate) -> Order:
    db_order = get_order(db, order_id)

    # Atualizar apenas os campos fornecidos
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> None:
    db_order = get_order(db, order_id)

    # Restaurar o estoque dos produtos
    order_items = db.query(order_products).filter(
        order_products.c.order_id == order_id).all()
    for item in order_items:
        product = db.query(Product).filter(
            Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity

    # Excluir o pedido
    db.delete(db_order)
    db.commit()
