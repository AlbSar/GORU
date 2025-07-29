"""
Stock endpoint testleri.
"""

import uuid

import pytest


def unique_product():
    return f"Product_{uuid.uuid4()}"


def test_create_stock(client, auth_headers):
    product = unique_product()
    print(f"[TEST] test_create_stock: product_name={product}")
    response = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 10},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product_name"] == product
    assert data["quantity"] == 10


def test_create_stock_duplicate_product(client, auth_headers):
    product = unique_product()
    print(f"[TEST] test_create_stock_duplicate_product: product_name={product}")
    client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 5},
        headers=auth_headers,
    )
    response = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 7},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 400
    assert "already exists" in response.text or "zaten kayıtlı" in response.text


def test_create_stock_negative_quantity(client, auth_headers):
    product = unique_product()
    print(f"[TEST] test_create_stock_negative_quantity: product_name={product}")
    response = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": -1},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_create_stock_empty_name(client, auth_headers):
    print("[TEST] test_create_stock_empty_name")
    response = client.post(
        "/api/v1/stocks/",
        json={"product_name": "", "quantity": 5},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_list_stocks(client, auth_headers):
    print("[TEST] test_list_stocks")
    response = client.get("/api/v1/stocks/", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_stock(client, auth_headers):
    product = unique_product()
    print(f"[TEST] test_get_stock: product_name={product}")
    create_resp = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 3},
        headers=auth_headers,
    )
    stock_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/stocks/{stock_id}", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert response.json()["product_name"] == product


def test_get_nonexistent_stock(client, auth_headers):
    print("[TEST] test_get_nonexistent_stock")
    response = client.get("/api/v1/stocks/9999999", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 404


def test_update_stock(client, auth_headers):
    product = unique_product()
    print(f"[TEST] test_update_stock: product_name={product}")
    create_resp = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 2},
        headers=auth_headers,
    )
    stock_id = create_resp.json()["id"]
    new_product = unique_product()
    response = client.put(
        f"/api/v1/stocks/{stock_id}",
        json={"product_name": new_product, "quantity": 5},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == new_product
    assert data["quantity"] == 5


def test_update_stock_duplicate_product(client, auth_headers):
    product1 = unique_product()
    product2 = unique_product()
    print(
        f"[TEST] test_update_stock_duplicate_product: "
        f"product1={product1}, product2={product2}"
    )
    client.post(
        "/api/v1/stocks/",
        json={"product_name": product1, "quantity": 1},
        headers=auth_headers,
    )
    resp2 = client.post(
        "/api/v1/stocks/",
        json={"product_name": product2, "quantity": 2},
        headers=auth_headers,
    )
    id2 = resp2.json()["id"]
    response = client.put(
        f"/api/v1/stocks/{id2}",
        json={"product_name": product1, "quantity": 3},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 400
    assert "already exists" in response.text or "zaten kayıtlı" in response.text


def test_delete_stock(client, auth_headers):
    product = unique_product()
    print(f"[TEST] test_delete_stock: product_name={product}")
    create_resp = client.post(
        "/api/v1/stocks/",
        json={"product_name": product, "quantity": 4},
        headers=auth_headers,
    )
    stock_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/stocks/{stock_id}", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 204
    # Silinen stock'ı get etmeye çalış
    get_response = client.get(f"/api/v1/stocks/{stock_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_nonexistent_stock(client, auth_headers):
    print("[TEST] test_delete_nonexistent_stock")
    response = client.delete("/api/v1/stocks/9999999", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 404
