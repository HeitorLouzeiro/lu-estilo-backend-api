from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User, UserRole
from src.schemas.product import (ProductCreate, ProductList, ProductResponse,
                                 ProductUpdate)
from src.services import product_service
from src.utils.security import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["📦 Produtos"],
    responses={
        404: {"description": "Produto não encontrado"},
        403: {"description": "Acesso negado - apenas administradores"},
    }
)


@router.get("", response_model=ProductList, summary="Listar produtos", description="Retorna uma lista paginada de produtos, com filtros por categoria, preço e estoque.", response_description="Lista de produtos.")
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: Optional[bool] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista produtos cadastrados.
    - **category**: Filtra por categoria
    - **min_price**: Preço mínimo
    - **max_price**: Preço máximo
    - **in_stock**: Apenas produtos em estoque
    - **page**: Página da paginação
    - **size**: Tamanho da página
    """
    skip = (page - 1) * size
    products, total = product_service.get_products(
        db=db,
        skip=skip,
        limit=size,
        category=category,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock
    )

    return {
        "items": products,
        "total": total,
        "page": page,
        "size": size
    }


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Criar produto", description="Cria um novo produto. Apenas administradores podem acessar.", response_description="Dados do produto criado.")
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo produto.
    - **product**: Dados do produto a ser criado
    """
    # Verificar se o usuário é admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar produtos"
        )

    return product_service.create_product(db=db, product=product)


@router.get("/{product_id}", response_model=ProductResponse, summary="Obter produto", description="Retorna os dados de um produto pelo ID.", response_description="Dados do produto.")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca um produto pelo ID.
    - **product_id**: ID do produto
    """
    return product_service.get_product(db=db, product_id=product_id)


@router.put("/{product_id}", response_model=ProductResponse, summary="Atualizar produto", description="Atualiza os dados de um produto existente. Apenas administradores podem acessar.", response_description="Dados do produto atualizado.")
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um produto existente.
    - **product_id**: ID do produto
    - **product**: Novos dados do produto
    """
    # Verificar se o usuário é admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem atualizar produtos"
        )

    return product_service.update_product(db=db, product_id=product_id, product=product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir produto", description="Remove um produto do sistema pelo ID. Apenas administradores podem acessar.")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exclui um produto pelo ID.
    - **product_id**: ID do produto
    """
    # Verificar se o usuário é admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir produtos"
        )

    product_service.delete_product(db=db, product_id=product_id)
    return None
