import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from src.models.product import Product
from src.schemas.product import ProductCreate, ProductUpdate


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None
) -> tuple[List[Product], int]:
    query = db.query(Product)

    # Aplicar filtros se fornecidos
    if category:
        query = query.filter(Product.section == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock is not None and in_stock:
        query = query.filter(Product.stock > 0)

    total = query.count()
    products = query.offset(skip).limit(limit).all()

    # Converter image_urls de JSON string para lista
    for product in products:
        if product.image_urls:
            product.image_urls = json.loads(product.image_urls)
        else:
            product.image_urls = []

    return products, total


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {product_id} não encontrado"
        )

    # Converter image_urls de JSON string para lista
    if product.image_urls:
        product.image_urls = json.loads(product.image_urls)
    else:
        product.image_urls = []

    return product


def create_product(db: Session, product: ProductCreate) -> Product:
    # Verificar se já existe produto com mesmo código de barras
    if product.barcode:
        existing = db.query(Product).filter(
            Product.barcode == product.barcode).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de barras já cadastrado"
            )

    # Converter lista de URLs de imagens para JSON string
    product_data = product.dict()
    if product_data.get('image_urls'):
        product_data['image_urls'] = json.dumps(product_data['image_urls'])

    # Criar novo produto
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Converter image_urls de JSON string para lista para a resposta
    if db_product.image_urls:
        db_product.image_urls = json.loads(db_product.image_urls)
    else:
        db_product.image_urls = []

    return db_product


def update_product(db: Session, product_id: int, product: ProductUpdate) -> Product:
    db_product = get_product(db, product_id)

    # Verificar se o código de barras já está em uso por outro produto
    if product.barcode and product.barcode != db_product.barcode:
        existing = db.query(Product).filter(
            Product.barcode == product.barcode).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de barras já cadastrado para outro produto"
            )

    # Atualizar apenas os campos fornecidos
    update_data = product.dict(exclude_unset=True)

    # Converter lista de URLs de imagens para JSON string
    if 'image_urls' in update_data and update_data['image_urls'] is not None:
        update_data['image_urls'] = json.dumps(update_data['image_urls'])

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    # Converter image_urls de JSON string para lista para a resposta
    if db_product.image_urls:
        db_product.image_urls = json.loads(db_product.image_urls)
    else:
        db_product.image_urls = []

    return db_product


def delete_product(db: Session, product_id: int) -> None:
    db_product = get_product(db, product_id)
    db.delete(db_product)
    db.commit()
