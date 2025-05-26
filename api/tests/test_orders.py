from src.models.order import Order, OrderItem
from datetime import datetime

import pytest
from faker import Faker
from fastapi import status

from src.models.order import OrderStatus

# Inicializa o Faker para gerar dados de teste
fake = Faker('pt_BR')


@pytest.fixture
def test_order(db_session, test_client, test_product):
    """Fixture para criar um pedido de teste"""

    order = Order(
        client_id=test_client.id,
        status=OrderStatus.PENDING,
        total_amount=fake.pyfloat(min_value=50, max_value=500, right_digits=2)
    )
    db_session.add(order)
    db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        quantity=2,
        unit_price=test_product.price
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)

    return order


def test_list_orders(client, test_order, admin_headers):
    """Testa a listagem de pedidos."""
    response = client.get("/orders", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] >= 1
    assert len(response.json()["items"]) >= 1


def test_get_order_by_id(client, test_order, admin_headers):
    """Testa obter um pedido pelo ID."""
    response = client.get(f"/orders/{test_order.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_order.id
    assert response.json()["status"] == test_order.status
    assert response.json()["total_amount"] == test_order.total_amount
    assert len(response.json()["items"]) >= 1


def test_get_order_not_found(client, admin_headers):
    """Testa obter um pedido que não existe."""
    response = client.get("/orders/9999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_order(client, test_client, test_product, admin_headers):
    """Testa a criação de um novo pedido."""
    # Usando Faker para gerar dados do pedido
    quantity = fake.random_int(min=1, max=5)
    payment_method = fake.random_element(["credit_card", "debit_card", "cash", "pix"])

    order_data = {
        "client_id": test_client.id,
        "items": [
            {
                "product_id": test_product.id,
                "quantity": quantity,
                "unit_price": test_product.price
            }
        ],
        "payment_method": payment_method,
        "notes": fake.text(max_nb_chars=50)
    }
    response = client.post("/orders", json=order_data, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["client_id"] == order_data["client_id"]
    assert response.json()["status"] == OrderStatus.PENDING
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["product_id"] == test_product.id
    assert response.json()["items"][0]["quantity"] == quantity
    assert "id" in response.json()


def test_create_order_invalid_client(client, test_product, admin_headers):
    """Testa criação de pedido com cliente inválido."""
    order_data = {
        "client_id": 9999,  # Cliente que não existe
        "items": [
            {
                "product_id": test_product.id,
                "quantity": 1,
                "unit_price": test_product.price
            }
        ],
        "payment_method": "cash"
    }
    response = client.post("/orders", json=order_data, headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Cliente" in response.json()["detail"] and "não encontrado" in response.json()["detail"]


def test_create_order_invalid_product(client, test_client, admin_headers):
    """Testa criação de pedido com produto inválido."""
    order_data = {
        "client_id": test_client.id,
        "items": [
            {
                "product_id": 9999,  # Produto que não existe
                "quantity": 1,
                "unit_price": 99.99
            }
        ],
        "payment_method": "cash"
    }
    response = client.post("/orders", json=order_data, headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Produto" in response.json()["detail"] and "não encontrado" in response.json()["detail"]


def test_create_order_insufficient_stock(client, test_client, test_product, admin_headers):
    """Testa criação de pedido com quantidade maior que o estoque."""
    # Primeiro, vamos garantir que sabemos qual o estoque atual
    stock_response = client.get(
        f"/products/{test_product.id}", headers=admin_headers)
    current_stock = stock_response.json()["stock"]

    order_data = {
        "client_id": test_client.id,
        "items": [
            {
                "product_id": test_product.id,
                "quantity": current_stock + 10,  # Maior que o estoque disponível
                "unit_price": test_product.price
            }
        ],
        "payment_method": "cash"
    }
    response = client.post("/orders", json=order_data, headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "estoque insuficiente" in response.json()["detail"].lower()


def test_update_order_status(client, test_order, admin_headers):
    """Testa atualização do status de um pedido."""
    update_data = {"status": OrderStatus.PROCESSING}
    response = client.put(
        f"/orders/{test_order.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == OrderStatus.PROCESSING


def test_update_order_status_invalid(client, test_order, admin_headers):
    """Testa atualização com status inválido."""
    update_data = {"status": "status_invalido"}
    response = client.put(
        f"/orders/{test_order.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_cancel_order(client, test_order, admin_headers):
    """Testa cancelamento de um pedido."""
    update_data = {"status": OrderStatus.CANCELLED}
    response = client.put(
        f"/orders/{test_order.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == OrderStatus.CANCELLED


def test_get_client_orders(client, test_order, test_client, admin_headers):
    """Testa obter pedidos de um cliente específico."""
    # Usando a rota /orders com filtro por client_id
    response = client.get(
        f"/orders?client_id={test_client.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) >= 1
    assert response.json()["items"][0]["client_id"] == test_client.id


def test_order_date_filter(client, test_order, admin_headers):
    """Testa filtrar pedidos por data."""
    today = datetime.now().date().isoformat()
    response = client.get(
        f"/orders?start_date={today}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) >= 1


def test_order_status_filter(client, test_order, admin_headers):
    """Testa filtrar pedidos por status."""
    status_value = test_order.status.value  # Obtém o valor do status do pedido de teste
    response = client.get(
        f"/orders?status={status_value}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) >= 1
    for item in response.json()["items"]:
        assert item["status"] == test_order.status
