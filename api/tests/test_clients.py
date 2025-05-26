import pytest
from faker import Faker
from fastapi import status

# Inicializa o Faker para gerar dados de teste
fake = Faker('pt_BR')


def test_list_clients(client, test_client, admin_headers):
    """Testa a listagem de clientes."""
    response = client.get("/clients", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] >= 1
    assert len(response.json()["items"]) >= 1


def test_get_client_by_id(client, test_client, admin_headers):
    """Testa obter um cliente pelo ID."""
    response = client.get(f"/clients/{test_client.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_client.id
    assert response.json()["name"] == test_client.name
    assert response.json()["email"] == test_client.email
    assert response.json()["cpf"] == test_client.cpf


def test_get_client_not_found(client, admin_headers):
    """Testa obter um cliente que não existe."""
    response = client.get("/clients/9999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_client(client, admin_headers):
    """Testa a criação de um novo cliente."""
    client_data = {
        "name": fake.name(),
        "email": fake.email(),
        "cpf": fake.cpf().replace('.', '').replace('-', ''),
        "phone": fake.phone_number(),
        "address": fake.address()
    }
    response = client.post("/clients", json=client_data, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == client_data["name"]
    assert response.json()["email"] == client_data["email"]
    assert response.json()["cpf"] == client_data["cpf"]
    assert "id" in response.json()


def test_create_client_duplicate_email(client, test_client, admin_headers):
    """Testa criação de cliente com email já existente."""
    client_data = {
        "name": "Cliente Duplicado",
        "email": test_client.email,
        "cpf": "45678912300",
        "phone": "11912345678",
        "address": "Av. Duplicada, 789"
    }
    response = client.post("/clients", json=client_data, headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email já cadastrado" in response.json()["detail"]


def test_create_client_duplicate_cpf(client, test_client, admin_headers):
    """Testa criação de cliente com CPF já existente."""
    client_data = {
        "name": "Cliente Duplicado",
        "email": "outro@teste.com",
        "cpf": test_client.cpf,
        "phone": "11912345678",
        "address": "Av. Duplicada, 789"
    }
    response = client.post("/clients", json=client_data, headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "CPF já cadastrado" in response.json()["detail"]


def test_update_client(client, test_client, admin_headers):
    """Testa atualização de informações do cliente."""
    update_data = {
        "name": "Cliente Atualizado",
        "phone": "11999998888",
        "address": "Rua Atualizada, 321"
    }

    response = client.put(
        f"/clients/{test_client.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == update_data["name"]
    assert response.json()["phone"] == update_data["phone"]
    assert response.json()["address"] == update_data["address"]
    # Email e CPF não devem ser alterados
    assert response.json()["email"] == test_client.email
    assert response.json()["cpf"] == test_client.cpf


def test_update_client_not_found(client, admin_headers):
    """Testa atualização de um cliente que não existe."""
    update_data = {"name": "Cliente Inexistente"}
    response = client.put(
        "/clients/9999",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_client(client, test_client, admin_headers):
    """Testa exclusão de um cliente."""
    response = client.delete(
        f"/clients/{test_client.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verificar se o cliente foi realmente excluído
    response = client.get(
        f"/clients/{test_client.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_client_not_found(client, admin_headers):
    """Testa exclusão de um cliente que não existe."""
    response = client.delete("/clients/9999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_filter_clients_by_name(client, test_client, admin_headers):
    """Testa filtragem de clientes por nome."""
    # Usar parte do nome real do cliente de teste para garantir uma correspondência
    name_part = test_client.name.split()[0]
    response = client.get(
        f"/clients?name={name_part}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) >= 1
    assert name_part in response.json()["items"][0]["name"]


def test_filter_clients_by_email(client, test_client, admin_headers):
    """Testa filtragem de clientes por email."""
    # Usar parte do email real do cliente de teste para garantir uma correspondência
    email_part = test_client.email.split('@')[0]  # Pegar a parte antes do @
    response = client.get(
        f"/clients?email={email_part}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) >= 1
    assert email_part in response.json()["items"][0]["email"]
