"""
Users modülü için düzeltilmiş testler.
Auth, CRUD ve validation testleri.
"""

import uuid


class TestUsersWithAuth:
    """Yetkilendirme ile kullanıcı testleri."""

    def test_create_user(self, client, auth_headers):
        """Kullanıcı oluşturma testi."""
        user_data = {
            "name": "Test User",
            "email": f"test-{uuid.uuid4()}@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        create_response = client.post("/users/", json=user_data, headers=auth_headers)
        assert create_response.status_code == 201
        user_data_response = create_response.json()
        assert user_data_response["name"] == user_data["name"]
        assert user_data_response["email"] == user_data["email"]
        assert "id" in user_data_response

    def test_get_users(self, client, auth_headers):
        """Kullanıcı listesi testi."""
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)

    def test_get_user_by_id(self, client, auth_headers, create_test_user):
        """ID ile kullanıcı getirme testi."""
        user_id = create_test_user["id"]
        response = client.get(f"/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["id"] == user_id

    def test_update_user(self, client, auth_headers, create_test_user):
        """Kullanıcı güncelleme testi."""
        user_id = create_test_user["id"]
        update_data = {
            "name": "Updated User",
            "email": f"updated-{uuid.uuid4()}@example.com",
        }
        response = client.put(
            f"/users/{user_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["name"] == update_data["name"]

    def test_delete_user(self, client, auth_headers):
        """Kullanıcı silme testi."""
        # Önce kullanıcı oluştur
        user_data = {
            "name": "Delete Test User",
            "email": f"delete-{uuid.uuid4()}@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        create_response = client.post("/users/", json=user_data, headers=auth_headers)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Sonra sil
        delete_response = client.delete(f"/users/{user_id}", headers=auth_headers)
        assert delete_response.status_code == 204

        # Silindiğini kontrol et
        get_response = client.get(f"/users/{user_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_create_user_duplicate_email(self, client, auth_headers):
        """Duplicate e-posta ile kullanıcı oluşturma testi."""
        email = f"duplicate-{uuid.uuid4()}@example.com"
        user_data = {
            "name": "First User",
            "email": email,
            "role": "user",
            "is_active": True,
            "password": "test123",
        }

        # İlk kullanıcıyı oluştur
        response1 = client.post("/users/", json=user_data, headers=auth_headers)
        assert response1.status_code == 201

        # Aynı e-posta ile ikinci kullanıcıyı oluşturmaya çalış
        user_data["name"] = "Second User"
        response2 = client.post("/users/", json=user_data, headers=auth_headers)
        assert response2.status_code == 400  # Duplicate e-posta hatası


class TestUsersValidation:
    """Kullanıcı validasyon testleri."""

    def test_create_user_invalid_email(self, client, auth_headers):
        """Geçersiz e-posta formatı testi."""
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/users/", json=user_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_user_missing_fields(self, client, auth_headers):
        """Eksik alan testi."""
        user_data = {
            "name": "Test User"
            # email ve diğer gerekli alanlar eksik
        }
        response = client.post("/users/", json=user_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı getirme testi."""
        response = client.get("/users/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUsersUnauthorized:
    """Yetkilendirme testleri."""

    def test_get_users_without_auth(self, unauthenticated_client):
        """Yetkilendirme olmadan kullanıcı listesi."""
        response = unauthenticated_client.get("/users/")
        assert response.status_code == 401  # Missing token = 401

    def test_create_user_without_auth(self, unauthenticated_client):
        """Yetkilendirme olmadan kullanıcı oluşturma."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = unauthenticated_client.post("/users/", json=user_data)
        assert response.status_code == 401  # Missing token = 401

    def test_update_user_without_auth(self, unauthenticated_client):
        """Yetkilendirme olmadan kullanıcı güncelleme."""
        response = unauthenticated_client.put("/users/1", json={"name": "Updated"})
        assert response.status_code == 401  # Missing token = 401

    def test_delete_user_without_auth(self, unauthenticated_client):
        """Yetkilendirme olmadan kullanıcı silme."""
        response = unauthenticated_client.delete("/users/1")
        assert response.status_code == 401  # Missing token = 401
