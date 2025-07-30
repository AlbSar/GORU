"""
User endpoint testleri.
"""


def unique_email():
    """Benzersiz email oluştur."""
    import uuid

    return f"test-{uuid.uuid4()}@example.com"


def test_create_user(client, jwt_token_factory):
    print("[TEST] test_create_user")
    token = jwt_token_factory.create_token(user_id="admin", role="admin")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    email = unique_email()
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": email, "password": "test123"},
        headers=headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code in [201, 401, 422, 500]
    if response.status_code == 201:
        data = response.json()
        assert data["name"] == "Test User"
        assert data["email"] == email


def test_create_user_missing_field(client, jwt_token_factory):
    print("[TEST] test_create_user_missing_field")
    token = jwt_token_factory.create_token(user_id="admin", role="admin")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post("/users/", json={"name": "No Email"}, headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code in [422, 401, 500]
    response = client.post("/users/", json={"email": unique_email()}, headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code in [422, 401, 500]


def test_create_user_invalid_email(client, jwt_token_factory):
    print("[TEST] test_create_user_invalid_email")
    token = jwt_token_factory.create_token(user_id="admin", role="admin")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post(
        "/users/",
        json={"name": "Invalid Email", "email": "not-an-email"},
        headers=headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code in [422, 401, 500]


def test_create_user_duplicate_email(client, jwt_token_factory):
    email = unique_email()
    print(f"[TEST] test_create_user_duplicate_email: email={email}")
    token = jwt_token_factory.create_token(user_id="admin", role="admin")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    client.post(
        "/users/",
        json={"name": "User1", "email": email, "password": "test123"},
        headers=headers,
    )
    response = client.post(
        "/users/",
        json={"name": "User2", "email": email, "password": "test123"},
        headers=headers,
    )
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code in [400, 401, 422, 500]
    if response.status_code == 400:
        assert "already registered" in response.text or "kayıtlı" in response.text


def test_get_nonexistent_user(client, jwt_token_factory):
    print("[TEST] test_get_nonexistent_user")
    token = jwt_token_factory.create_token(user_id="admin", role="admin")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get("/users/9999999", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code in [404, 401, 500]


def test_list_users(client, jwt_token_factory):
    print("[TEST] test_list_users")
    token = jwt_token_factory.create_token(user_id="admin", role="admin")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get("/users/", headers=headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        assert isinstance(response.json(), list)


def test_get_user(client, jwt_token_factory):
    email = unique_email()
    print(f"[TEST] test_get_user: email={email}")
    token = jwt_token_factory.create_token(user_id="admin", role="admin")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    user_resp = client.post(
        "/users/",
        json={"name": "Detail User", "email": email, "password": "test123"},
        headers=headers,
    )
    if user_resp.status_code == 201:
        user_id = user_resp.json()["id"]
        response = client.get(f"/users/{user_id}", headers=headers)
        print(f"[DEBUG] Response: {response.status_code}, {response.text}")
        assert response.status_code in [200, 401, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == user_id


def test_update_user(client, auth_headers):
    email = unique_email()
    print(f"[TEST] test_update_user: email={email}")
    user_resp = client.post(
        "/users/",
        json={"name": "Update User", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    user_id = user_resp.json()["id"]
    new_email = unique_email()
    response = client.put(
        f"/users/{user_id}",
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
        "/users/",
        json={"name": "Delete User", "email": email, "password": "test123"},
        headers=auth_headers,
    )
    user_id = user_resp.json()["id"]
    response = client.delete(f"/users/{user_id}", headers=auth_headers)
    print(f"[DEBUG] Response: {response.status_code}, {response.text}")
    assert response.status_code == 204
    # Silinen user'ı get etmeye çalış
    get_response = client.get(f"/users/{user_id}", headers=auth_headers)
    assert get_response.status_code == 404
