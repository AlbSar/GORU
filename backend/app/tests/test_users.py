"""
User endpoint testleri.
"""

import pytest


def unique_email():
    """Benzersiz email oluştur."""
    import uuid

    return f"test-{uuid.uuid4()}@example.com"


def test_create_user(client, auth_headers):
    print("[TEST] test_create_user")
    email = unique_email()
    response = client.post(
        "/api/v1/users/",
        json={"name": "Test User", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == email


def test_create_user_missing_field(client, auth_headers):
    print("[TEST] test_create_user_missing_field")
    response = client.post(
        "/api/v1/users/", json={"name": "No Email"}, headers=auth_headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422
    response = client.post(
        "/api/v1/users/", json={"email": unique_email()}, headers=auth_headers
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_create_user_invalid_email(client, auth_headers):
    print("[TEST] test_create_user_invalid_email")
    response = client.post(
        "/api/v1/users/",
        json={"name": "Invalid Email", "email": "not-an-email"},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 422


def test_create_user_duplicate_email(client, auth_headers):
    email = unique_email()
    print(f"[TEST] test_create_user_duplicate_email: email={email}")
    client.post(
        "/api/v1/users/",
        json={"name": "User1", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    response = client.post(
        "/api/v1/users/",
        json={"name": "User2", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 400
    assert "already registered" in response.text or "kayıtlı" in response.text


def test_get_nonexistent_user(client, auth_headers):
    print("[TEST] test_get_nonexistent_user")
    response = client.get("/api/v1/users/9999999", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 404


def test_list_users(client, auth_headers):
    print("[TEST] test_list_users")
    response = client.get("/api/v1/users/", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user(client, auth_headers):
    email = unique_email()
    print(f"[TEST] test_get_user: email={email}")
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Detail User", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    user_id = user_resp.json()["id"]
    response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id


def test_update_user(client, auth_headers):
    email = unique_email()
    print(f"[TEST] test_update_user: email={email}")
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Update User", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    user_id = user_resp.json()["id"]
    new_email = unique_email()
    response = client.put(
        f"/api/v1/users/{user_id}",
        json={"name": "Updated", "email": new_email},
        headers=auth_headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["email"] == new_email


def test_delete_user(client, auth_headers):
    email = unique_email()
    print(f"[TEST] test_delete_user: email={email}")
    user_resp = client.post(
        "/api/v1/users/",
        json={"name": "Delete User", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    user_id = user_resp.json()["id"]
    response = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 204
    # Silinen user'ı get etmeye çalış
    get_response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert get_response.status_code == 404
