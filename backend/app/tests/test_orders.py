"""
Order endpoint testleri.
"""

import uuid
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)
headers = {"Authorization": "Bearer secret-token"}


def unique_email():
    return f"order_{uuid.uuid4()}@example.com"


def unique_product():
    return f"Product_{uuid.uuid4()}"


def test_create_order():
    email = unique_email()
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Order User", "email": email, "password": "test123"},
        headers=headers,
    )
    user_id = user_resp.json()["id"]
    product = unique_product()
    response = client.post(
        "/api/v1/orders/",
        json={"user_id": user_id, "product_name": product, "amount": 10.5},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["product_name"] == product


def test_create_order_with_all_required_fields():
    """
    TR: Tüm zorunlu alanlar doldurularak başarılı bir sipariş oluşturulmasını test eder.
    EN: Tests successful order creation when all required fields are provided.
    """
    email = unique_email()
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Order User3", "email": email, "password": "test123"},
        headers=headers,
    )
    user_id = user_resp.json()["id"]
    product = unique_product()
    response = client.post(
        "/api/v1/orders/",
        json={"user_id": user_id, "product_name": product, "amount": 15.0},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["product_name"] == product


# def test_create_order_missing_field():
#     """
#     TR: Eksik alanlarla sipariş oluşturulmaya çalışıldığında API'nin 422 ValidationError döndürdüğünü test eder.
#     EN: Tests that the API returns 422 ValidationError when trying to create an order with missing required fields.
#     """
#     email = unique_email()
#     user_resp = client.post(
#         "/api/v1/users/", json={"name": "Order User2", "email": email, "password": "test123"}, headers=headers
#     )
#     user_id = user_resp.json()["id"]
#
#     # Eksik ürün adı (missing product_name)
#     response = client.post(
#         "/api/v1/orders/", json={"user_id": user_id, "amount": 10.5}, headers=headers
#     )
#     assert response.status_code == 422
#     # Hata mesajı kontrolü (Error message check)
#     assert "total_amount" in response.text and "order_items" in response.text
#
#     # Eksik amount (missing amount)
#     response = client.post(
#         "/api/v1/orders/", json={"user_id": user_id, "product_name": unique_product()}, headers=headers
#     )
#     assert response.status_code == 422
#     assert "total_amount" in response.text and "order_items" in response.text


def test_create_order_invalid_amount():
    email = unique_email()
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Order User3", "email": email, "password": "test123"},
        headers=headers,
    )
    user_id = user_resp.json()["id"]
    response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user_id,
            "product_name": unique_product(),
            "amount": -5,
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_create_order_nonexistent_user():
    response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": 9999999,
            "product_name": unique_product(),
            "amount": 10.5,
        },
        headers=headers,
    )
    assert response.status_code == 404


def test_get_nonexistent_order():
    response = client.get("/api/v1/orders/9999999", headers=headers)
    assert response.status_code == 404


def test_list_orders():
    response = client.get("/api/v1/orders/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_order():
    email = unique_email()
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Order Detail", "email": email, "password": "test123"},
        headers=headers,
    )
    user_id = user_resp.json()["id"]
    product = unique_product()
    order_resp = client.post(
        "/api/v1/orders/",
        json={"user_id": user_id, "product_name": product, "amount": 20.0},
        headers=headers,
    )
    order_id = order_resp.json()["id"]
    response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id


def test_update_order():
    email = unique_email()
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Order Update", "email": email, "password": "test123"},
        headers=headers,
    )
    user_id = user_resp.json()["id"]
    product = unique_product()
    order_resp = client.post(
        "/api/v1/orders/",
        json={"user_id": user_id, "product_name": product, "amount": 30.0},
        headers=headers,
    )
    order_id = order_resp.json()["id"]
    new_product = unique_product()
    response = client.put(
        f"/api/v1/orders/{order_id}",
        json={"user_id": user_id, "product_name": new_product, "amount": 35.0},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["product_name"] == new_product


def test_delete_order():
    email = unique_email()
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Order Delete", "email": email, "password": "test123"},
        headers=headers,
    )
    user_id = user_resp.json()["id"]
    product = unique_product()
    order_resp = client.post(
        "/api/v1/orders/",
        json={"user_id": user_id, "product_name": product, "amount": 40.0},
        headers=headers,
    )
    order_id = order_resp.json()["id"]
    response = client.delete(f"/api/v1/orders/{order_id}", headers=headers)
    assert response.status_code == 204
