import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
headers = {"Authorization": "Bearer secret-token"}

def unique_email():
    return f"order_{uuid.uuid4()}@example.com"

def unique_product():
    return f"Product_{uuid.uuid4()}"

def test_create_order():
    email = unique_email()
    user_resp = client.post("/users/", json={"name": "Order User", "email": email}, headers=headers)
    user_id = user_resp.json()["id"]
    product = unique_product()
    response = client.post("/orders/", json={"user_id": user_id, "product_name": product, "amount": 10.5}, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["product_name"] == product

def test_create_order_missing_field():
    # Eksik ürün adı
    email = unique_email()
    user_resp = client.post("/users/", json={"name": "Order User2", "email": email}, headers=headers)
    user_id = user_resp.json()["id"]
    response = client.post("/orders/", json={"user_id": user_id, "amount": 10.5}, headers=headers)
    assert response.status_code == 422
    # Eksik amount
    response = client.post("/orders/", json={"user_id": user_id, "product_name": unique_product()}, headers=headers)
    assert response.status_code == 422

def test_create_order_invalid_amount():
    email = unique_email()
    user_resp = client.post("/users/", json={"name": "Order User3", "email": email}, headers=headers)
    user_id = user_resp.json()["id"]
    response = client.post("/orders/", json={"user_id": user_id, "product_name": unique_product(), "amount": -5}, headers=headers)
    assert response.status_code == 422

def test_create_order_nonexistent_user():
    response = client.post("/orders/", json={"user_id": 9999999, "product_name": unique_product(), "amount": 10.5}, headers=headers)
    assert response.status_code == 404

def test_get_nonexistent_order():
    response = client.get("/orders/9999999", headers=headers)
    assert response.status_code == 404

def test_list_orders():
    response = client.get("/orders/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order():
    email = unique_email()
    user_resp = client.post("/users/", json={"name": "Order Detail", "email": email}, headers=headers)
    user_id = user_resp.json()["id"]
    product = unique_product()
    order_resp = client.post("/orders/", json={"user_id": user_id, "product_name": product, "amount": 20.0}, headers=headers)
    order_id = order_resp.json()["id"]
    response = client.get(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id

def test_update_order():
    email = unique_email()
    user_resp = client.post("/users/", json={"name": "Order Update", "email": email}, headers=headers)
    user_id = user_resp.json()["id"]
    product = unique_product()
    order_resp = client.post("/orders/", json={"user_id": user_id, "product_name": product, "amount": 30.0}, headers=headers)
    order_id = order_resp.json()["id"]
    new_product = unique_product()
    response = client.put(f"/orders/{order_id}", json={"user_id": user_id, "product_name": new_product, "amount": 35.0}, headers=headers)
    assert response.status_code == 200
    assert response.json()["product_name"] == new_product

def test_delete_order():
    email = unique_email()
    user_resp = client.post("/users/", json={"name": "Order Delete", "email": email}, headers=headers)
    user_id = user_resp.json()["id"]
    product = unique_product()
    order_resp = client.post("/orders/", json={"user_id": user_id, "product_name": product, "amount": 40.0}, headers=headers)
    order_id = order_resp.json()["id"]
    response = client.delete(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 204 