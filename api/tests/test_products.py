import pytest
from faker import Faker
from fastapi import status

# Inicializa o Faker para gerar dados de teste
fake = Faker('pt_BR')


def test_list_products(client, test_product, admin_headers):
    """Testa a listagem de produtos."""
    response = client.get("/products", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] >= 1
    assert len(response.json()["items"]) >= 1


def test_get_product_by_id(client, test_product, admin_headers):
    """Testa obter um produto pelo ID."""
    response = client.get(
        f"/products/{test_product.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_product.id
    assert response.json()["description"] == test_product.description
    assert response.json()["price"] == test_product.price
    assert response.json()["barcode"] == test_product.barcode


def test_get_product_not_found(client, admin_headers):
    """Testa obter um produto que não existe."""
    response = client.get("/products/9999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_product(client, admin_headers):
    """Testa a criação de um novo produto."""
    product_data = {
        "description": fake.sentence(nb_words=3),
        "price": float(fake.random_number(digits=2) + fake.random_number(digits=2) / 100),
        "barcode": fake.ean13(),
        "section": fake.random_element(elements=["Roupas", "Calçados", "Acessórios"]),
        "stock": fake.random_int(min=1, max=100),
    }
    response = client.post(
        "/products", json=product_data, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["description"] == product_data["description"]
    assert response.json()["price"] == product_data["price"]
    assert response.json()["barcode"] == product_data["barcode"]
    assert response.json()["section"] == product_data["section"]
    assert response.json()["stock"] == product_data["stock"]
    assert "id" in response.json()


def test_create_product_duplicate_barcode(client, test_product, admin_headers):
    """Testa criação de produto com código de barras já existente."""
    product_data = {
        "description": fake.sentence(nb_words=3),
        "price": float(fake.random_number(digits=2)),
        "barcode": test_product.barcode,  # Barcode que já existe
        "section": fake.random_element(["Roupas", "Calçados", "Acessórios"]),
        "stock": fake.random_int(min=1, max=100),
    }
    response = client.post(
        "/products", json=product_data, headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já cadastrado" in response.json()["detail"]


def test_update_product(client, test_product, admin_headers):
    """Testa atualização de informações do produto."""
    update_data = {
        "description": "Produto Atualizado",
        "price": 129.99,
        "stock": 15,
        # Certificando-se de não enviar image_urls
        "image_urls": None
    }
    response = client.put(
        f"/products/{test_product.id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == update_data["description"]
    assert response.json()["price"] == update_data["price"]
    assert response.json()["stock"] == update_data["stock"]
    # Barcode e section não devem ser alterados
    assert response.json()["barcode"] == test_product.barcode
    assert response.json()["section"] == test_product.section


def test_update_product_not_found(client, admin_headers):
    """Testa atualização de um produto que não existe."""
    update_data = {"description": "Produto Inexistente"}
    response = client.put(
        "/products/9999",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_product(client, test_product, admin_headers):
    """Testa exclusão de um produto."""
    response = client.delete(
        f"/products/{test_product.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verificar se o produto foi realmente excluído
    response = client.get(
        f"/products/{test_product.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_product_not_found(client, admin_headers):
    """Testa exclusão de um produto que não existe."""
    response = client.delete("/products/9999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_filter_products_by_description(client, test_product, admin_headers):
    """Testa filtragem de produtos por descrição."""    # Usar parte da descrição real do produto
    description_part = test_product.description.split()[0]
    response = client.get(
        f"/products?description={description_part}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) >= 1
    assert description_part in response.json()["items"][0]["description"]


def test_filter_products_by_section(client, test_product, admin_headers):
    """Testa filtragem de produtos por seção."""
    # Usar a seção real do produto de teste
    section = test_product.section
    response = client.get(
        f"/products?section={section}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) >= 1
    assert response.json()["items"][0]["section"] == section


def test_filter_products_by_price_range(client, test_product, admin_headers):
    """Testa filtragem de produtos por faixa de preço."""
    response = client.get(
        "/products?min_price=50&max_price=150",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    for item in response.json()["items"]:
        assert 50 <= item["price"] <= 150


def test_product_stock_update(client, test_product, admin_headers):
    """Testa atualização específica do estoque de um produto."""
    stock_data = {
        "stock": 25,
        # Certificando-se de não enviar image_urls
        "image_urls": None
    }
    # Usar a rota PUT padrão para atualizações
    response = client.put(
        f"/products/{test_product.id}",
        json=stock_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["stock"] == stock_data["stock"]


def test_product_stock_update_negative(client, test_product, admin_headers):
    """Testa que não é possível definir estoque negativo."""
    stock_data = {
        "stock": -5,
        # Certificando-se de não enviar image_urls
        "image_urls": None
    }
    # Usar a rota PUT padrão para atualizações
    response = client.put(
        f"/products/{test_product.id}",
        json=stock_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Imprimir a resposta para ver sua estrutura
    print(f"Resposta: {response.json()}")    # Se detail é uma lista, verificamos se algum item contém a mensagem de validação
    if isinstance(response.json()["detail"], list):
        found = False
        for error in response.json()["detail"]:
            # Verificar se é um erro de validação de valor mínimo (greater_than_equal)
            if ("msg" in error and "greater than or equal to 0" in error["msg"]) or \
               ("type" in error and error["type"] == "greater_than_equal"):
                found = True
                break
        assert found, "Nenhuma mensagem de validação de valor mínimo encontrada nos erros"
    else:
        # Caso seja uma string simples
        assert "greater than or equal to 0" in response.json()["detail"] or "negativo" in response.json()["detail"].lower()
