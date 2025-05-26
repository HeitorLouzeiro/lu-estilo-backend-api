from src.utils.security import create_access_token, get_password_hash
from src.models import order, product, user
from src.models import client  # Importamos os modelos para criar tabelas
from src.main import app
import os
from datetime import timedelta

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.database import Base, get_db

# Inicializar o Faker
fake = Faker('pt_BR')  # Configurando para português do Brasil

# Configuração do banco de dados de teste em memória
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Criar engine para testes"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Cria todas as tabelas no banco de dados de teste
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db_session(engine):
    """Fixture para criar uma nova sessão do banco de dados para cada teste"""
    # Recria as tabelas para cada teste
    Base.metadata.create_all(bind=engine)

    # Cria uma nova sessão
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        # Limpa as tabelas após o teste
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture para fornecer um cliente de teste da API"""
    # Sobrescreve a função de dependência para usar o banco de dados de teste
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Limpa as sobrescrições após o teste
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db_session):
    """Fixture para criar um usuário administrador para testes"""
    admin_user = user.User(
        username="testadmin",
        # Email único para evitar conflitos
        email=fake.email(),
        hashed_password=get_password_hash("adminpassword"),
        role=user.UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    return admin_user


@pytest.fixture
def test_normal_user(db_session):
    """Fixture para criar um usuário normal para testes"""
    normal_user = user.User(
        username="testnormal",
        email=fake.email(),  # Email único gerado pelo Faker
        hashed_password=get_password_hash("userpassword"),
        role=user.UserRole.USER,
        is_active=True
    )
    db_session.add(normal_user)
    db_session.commit()
    db_session.refresh(normal_user)
    return normal_user


@pytest.fixture
def admin_token(test_admin_user):
    """Fixture para criar um token de acesso para o usuário administrador"""
    access_token = create_access_token(
        data={"sub": test_admin_user.username},
        expires_delta=timedelta(minutes=30)
    )
    return access_token


@pytest.fixture
def normal_token(test_normal_user):
    """Fixture para criar um token de acesso para um usuário normal"""
    access_token = create_access_token(
        data={"sub": test_normal_user.username},
        expires_delta=timedelta(minutes=30)
    )
    return access_token


@pytest.fixture
def admin_headers(admin_token):
    """Fixture para criar cabeçalhos de autorização para um usuário administrador"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def normal_headers(normal_token):
    """Fixture para criar cabeçalhos de autorização para um usuário normal"""
    return {"Authorization": f"Bearer {normal_token}"}


@pytest.fixture
def test_client(db_session):
    """Fixture para criar um cliente de teste"""
    from src.models.client import Client
    new_client = Client(
        name=fake.name(),
        email=fake.email(),  # Email único gerado pelo Faker
        cpf=fake.cpf().replace('.', '').replace('-', ''),  # CPF único sem pontuação
        phone=fake.phone_number(),
        address=fake.address()
    )
    db_session.add(new_client)
    db_session.commit()
    db_session.refresh(new_client)
    return new_client


@pytest.fixture
def test_product(db_session):
    """Fixture para criar um produto de teste"""
    product_test = product.Product(
        description=fake.sentence(nb_words=3),
        price=float(fake.random_number(digits=2) + fake.random_number(digits=2) / 100),
        barcode=fake.ean13(),  # Código de barras EAN13 válido
        section=fake.word(ext_word_list=["Roupas", "Calçados", "Acessórios", "Cosméticos"]),
        stock=fake.random_int(min=5, max=100),
    )
    db_session.add(product_test)
    db_session.commit()
    db_session.refresh(product_test)
    return product_test


@pytest.fixture
def test_order(db_session, test_client, test_product):
    """Fixture para criar um pedido de teste"""
    # Garantir estoque adequado
    test_product.stock = 10
    db_session.commit()

    # Criar o pedido
    new_order = order.Order(
        client_id=test_client.id,
        status=order.OrderStatus.PENDING,
        total_amount=test_product.price * 2
    )
    db_session.add(new_order)
    db_session.flush()  # Para obter o ID do pedido

    # Criar um item de pedido
    order_item = order.OrderItem(
        order_id=new_order.id,
        product_id=test_product.id,
        quantity=2,
        unit_price=test_product.price
    )
    db_session.add(order_item)

    db_session.commit()
    db_session.refresh(new_order)
    return new_order
