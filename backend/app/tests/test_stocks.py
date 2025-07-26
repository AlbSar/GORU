"""
Stok Testleri / Stock Tests

TR: Stok CRUD endpointleri için birim ve edge-case testleri.
EN: Unit and edge-case tests for Stock CRUD endpoints.
"""

import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
headers = {"Authorization": "Bearer secret-token"}


def unique_product():
    return f"Product_{uuid.uuid4()}"


def test_create_stock():
    product = unique_product()
    print(f"[TEST] test_create_stock: product_name={product}")
    response = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 10},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product_name"] == product
    assert data["quantity"] == 10


def test_create_stock_duplicate_product():
    product = unique_product()
    print(f"[TEST] test_create_stock_duplicate_product: product_name={product}")
    client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 5},
        headers=headers,
    )
    response = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 7},
        headers=headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 400
    assert "already exists" in response.text or "zaten kayıtlı" in response.text


def test_create_stock_negative_quantity():
    product = unique_product()
    print(f"[TEST] test_create_stock_negative_quantity: product_name={product}")
    response = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": -1},
        headers=headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_create_stock_empty_name():
    print("[TEST] test_create_stock_empty_name")
    response = client.post(
        "/api/v1/stocks/", json={"product_name": "", "quantity": 5}, headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_list_stocks():
    print("[TEST] test_list_stocks")
    response = client.get("/api/v1/stocks/", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_stock():
    product = unique_product()
    print(f"[TEST] test_get_stock: product_name={product}")
    create_resp = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 3},
        headers=headers,
    )
    stock_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/stocks/{stock_id}", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert response.json()["product_name"] == product


def test_get_nonexistent_stock():
    print("[TEST] test_get_nonexistent_stock")
    response = client.get("/api/v1/stocks/9999999", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 404


def test_update_stock():
    product = unique_product()
    print(f"[TEST] test_update_stock: product_name={product}")
    create_resp = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 2},
        headers=headers,
    )
    stock_id = create_resp.json()["id"]
    new_product = unique_product()
    response = client.put(
        f"/api/v1/stocks/{stock_id}",
        json={"product_name": new_product, "quantity": 5},
        headers=headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert response.json()["product_name"] == new_product
    assert response.json()["quantity"] == 5


def test_update_stock_duplicate_product():
    product1 = unique_product()
    product2 = unique_product()
    print(
        f"[TEST] test_update_stock_duplicate_product: product1={product1}, product2={product2}"
    )
    client.post(
        "/api/v1/stocks/",
        json={"product_name": product1, "quantity": 1},
        headers=headers,
    )
    resp2 = client.post(
        "/api/v1/stocks/",
        json={"product_name": product2, "quantity": 2},
        headers=headers,
    )
    id2 = resp2.json()["id"]
    response = client.put(
        f"/api/v1/stocks/{id2}", json={"product_name": product1}, headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 400


def test_delete_stock():
    product = unique_product()
    print(f"[TEST] test_delete_stock: product_name={product}")
    create_resp = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 4},
        headers=headers,
    )
    stock_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/stocks/{stock_id}", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 204


def test_delete_nonexistent_stock():
    print("[TEST] test_delete_nonexistent_stock")
    response = client.delete("/api/v1/stocks/9999999", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 404
