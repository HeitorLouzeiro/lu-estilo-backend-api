from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User
from src.schemas.auth import Token, UserCreate, UserResponse
from src.utils.security import (ACCESS_TOKEN_EXPIRE_MINUTES,
                                create_access_token, get_current_user,
                                get_password_hash, verify_password)

router = APIRouter(
    prefix="/auth",
    tags=["🔐 Autenticação"],
    responses={
        401: {"description": "Credenciais inválidas"},
        403: {"description": "Acesso negado"},
    }
)


@router.post("/login", response_model=Token, summary="Login do usuário", description="Autentica um usuário e retorna um token JWT para acesso às rotas protegidas.", response_description="Token de acesso JWT.")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica um usuário com username e senha.
    - **username**: Nome de usuário
    - **password**: Senha do usuário
    Retorna um token JWT se as credenciais estiverem corretas.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Registrar novo usuário", description="Cria um novo usuário no sistema. Usuários devem ter username, email e senha únicos.", response_description="Dados do usuário criado.")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário.
    - **username**: Nome de usuário único
    - **email**: E-mail único
    - **password**: Senha do usuário
    - **role**: Papel do usuário (admin ou user)
    """
    # Verificar se o usuário já existe
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário ou email já cadastrado"
        )

    # Criar novo usuário
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/refresh-token", response_model=Token, summary="Renovar token de acesso", description="Gera um novo token JWT para o usuário autenticado.", response_description="Novo token de acesso JWT.")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Renova o token de acesso do usuário autenticado.
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
