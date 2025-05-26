import pytest
from faker import Faker
from fastapi import status

# Inicializa o Faker para gerar dados de teste
fake = Faker('pt_BR')


def test_login_success(client, test_admin_user):
    """Testa login com credenciais válidas."""
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "adminpassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client, test_admin_user):
    """Testa login com senha incorreta."""
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Usuário ou senha incorretos" in response.json()["detail"]


def test_login_user_not_found(client):
    """Testa login com usuário que não existe."""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Usuário ou senha incorretos" in response.json()["detail"]


def test_register_success(client):
    """Testa registro de um novo usuário com sucesso."""
    # Usar Faker para gerar dados únicos
    username = f"user_{fake.user_name().replace('.', '').replace(' ', '_')}"
    user_data = {
        "username": username,
        "email": fake.email(),
        "password": "newpassword",
        "role": "user",  # Enum em minúsculo conforme exigido pela API
        "full_name": fake.name()  # Adicionando campo que pode ser necessário
    }
    response = client.post("/auth/register", json=user_data)
    print(f"Resposta: {response.status_code}")
    print(f"Corpo da resposta: {response.json()}")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]
    assert "id" in response.json()


def test_register_duplicate_username(client, test_admin_user):
    """Testa registro com nome de usuário já existente."""
    user_data = {
        "username": "testadmin",  # Username que já existe
        "email": "different@test.com",
        "password": "newpassword"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já cadastrado" in response.json()["detail"]


def test_register_duplicate_email(client, test_admin_user):
    """Testa registro com email já existente."""
    user_data = {
        "username": "differentuser",
        "email": test_admin_user.email,  # Usando o email real do usuário admin
        "password": "newpassword",
        "role": "user"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já cadastrado" in response.json()["detail"]


def test_protected_endpoint_with_valid_token(client, admin_headers):
    """Testa acesso a um endpoint protegido com token válido."""
    response = client.get("/clients", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK


def test_protected_endpoint_without_token(client):
    """Testa acesso a um endpoint protegido sem token."""
    response = client.get("/clients")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]


def test_protected_endpoint_with_invalid_token(client):
    """Testa acesso a um endpoint protegido com token inválido."""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/clients", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
