import sys
import os
import uuid

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
headers = {"Authorization": "Bearer secret-token"}


def unique_email():
    return f"test_{uuid.uuid4()}@example.com"


def test_create_user():
    email = unique_email()
    print(f"[TEST] test_create_user: email={email}")
    response = client.post(
        "/users/", json={"name": "Test User", "email": email, "password": "test123"}, headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == email


def test_create_user_missing_field():
    print(f"[TEST] test_create_user_missing_field")
    response = client.post(
        "/users/", json={"name": "No Email"}, headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422
    response = client.post(
        "/users/", json={"email": unique_email()}, headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_create_user_invalid_email():
    print(f"[TEST] test_create_user_invalid_email")
    response = client.post(
        "/users/", json={"name": "Invalid Email", "email": "not-an-email"}, headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_create_user_duplicate_email():
    email = unique_email()
    print(f"[TEST] test_create_user_duplicate_email: email={email}")
    client.post(
        "/users/", json={"name": "User1", "email": email, "password": "test123"}, headers=headers
    )
    response = client.post(
        "/users/", json={"name": "User2", "email": email, "password": "test123"}, headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 400
    assert "already registered" in response.text or "kayıtlı" in response.text


def test_get_nonexistent_user():
    print(f"[TEST] test_get_nonexistent_user")
    response = client.get("/users/9999999", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 404


def test_list_users():
    print(f"[TEST] test_list_users")
    response = client.get("/users/", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user():
    email = unique_email()
    print(f"[TEST] test_get_user: email={email}")
    user_resp = client.post(
        "/users/", json={"name": "Detail User", "email": email, "password": "test123"}, headers=headers
    )
    user_id = user_resp.json()["id"]
    response = client.get(f"/users/{user_id}", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id


def test_update_user():
    email = unique_email()
    print(f"[TEST] test_update_user: email={email}")
    user_resp = client.post(
        "/users/", json={"name": "Update User", "email": email, "password": "test123"}, headers=headers
    )
    user_id = user_resp.json()["id"]
    new_email = unique_email()
    response = client.put(
        f"/users/{user_id}",
        json={"name": "Updated", "email": new_email},
        headers=headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    assert response.json()["email"] == new_email


def test_delete_user():
    email = unique_email()
    print(f"[TEST] test_delete_user: email={email}")
    user_resp = client.post(
        "/users/", json={"name": "Delete User", "email": email, "password": "test123"}, headers=headers
    )
    user_id = user_resp.json()["id"]
    response = client.delete(f"/users/{user_id}", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 204 