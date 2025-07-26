"""
Kullanıcı API endpoint testleri (Auth Token'lı).
CRUD işlemleri ve edge case'leri test eder.
"""

import pytest
import uuid


class TestUsersWithAuth:
    """Auth token'lı kullanıcı testleri."""

    def test_create_user(self, client, auth_headers):
        """Kullanıcı oluşturma testi."""
        user_data = {
            "name": "Test User",
            "email": f"test-{uuid.uuid4()}@example.com",
            "role": "admin",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]
        assert "id" in data

    def test_get_users(self, client, auth_headers):
        """Kullanıcı listesi getirme testi."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)

    def test_get_user_by_id(self, client, auth_headers, create_test_user):
        """ID'ye göre kullanıcı getirme testi."""
        if create_test_user:
            response = client.get(
                f"/api/v1/users/{create_test_user}", headers=auth_headers
            )
            assert response.status_code == 200
            user = response.json()
            assert user["id"] == create_test_user

    def test_update_user(self, client, auth_headers, create_test_user):
        """Kullanıcı güncelleme testi."""
        if create_test_user:
            update_data = {"name": "Updated User Name"}
            response = client.put(
                f"/api/v1/users/{create_test_user}",
                json=update_data,
                headers=auth_headers,
            )
            assert response.status_code == 200
            updated_user = response.json()
            assert updated_user["name"] == "Updated User Name"

    def test_delete_user(self, client, auth_headers):
        """Kullanıcı silme testi."""
        # Önce bir kullanıcı oluştur
        user_data = {
            "name": "Delete Test User",
            "email": f"delete-{uuid.uuid4()}@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        create_response = client.post(
            "/api/v1/users/", json=user_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Sonra sil
        delete_response = client.delete(
            f"/api/v1/users/{user_id}", headers=auth_headers
        )
        assert delete_response.status_code == 204

        # Silindiğini kontrol et
        get_response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
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
        response1 = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response1.status_code == 201

        # Aynı e-posta ile ikinci kullanıcıyı oluşturmaya çalış
        user_data["name"] = "Second User"
        response2 = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
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
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_user_missing_fields(self, client, auth_headers):
        """Eksik alan testi."""
        user_data = {
            "name": "Test User"
            # email ve diğer gerekli alanlar eksik
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı getirme testi."""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUsersUnauthorized:
    """Yetkilendirme testleri."""

    def test_get_users_without_auth(self, client):
        """Yetkilendirme olmadan kullanıcı listesi."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 403

    def test_create_user_without_auth(self, client):
        """Yetkilendirme olmadan kullanıcı oluşturma."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 403

    def test_update_user_without_auth(self, client):
        """Yetkilendirme olmadan kullanıcı güncelleme."""
        response = client.put("/api/v1/users/1", json={"name": "Updated"})
        assert response.status_code == 403

    def test_delete_user_without_auth(self, client):
        """Yetkilendirme olmadan kullanıcı silme."""
        response = client.delete("/api/v1/users/1")
        assert response.status_code == 403
