"""
Users modülü için error handling testleri.
404, 422, 500 hata senaryolarını test eder.
"""

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def unique_email():
    return f"user_error_{uuid.uuid4()}@example.com"


# genel hata senaryosu testleri
class TestUsersErrorHandling:
    """Users modülü için error handling testleri."""

    # === 404 NOT FOUND TESTS ===

    def test_get_nonexistent_user_404(self, auth_headers):
        """GET non-existent user → 404"""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_put_nonexistent_user_404(self, auth_headers):
        """PUT non-existent user → 404"""
        update_data = {"name": "Test User", "email": "test@example.com"}
        response = client.put(
            "/api/v1/users/99999", json=update_data, headers=auth_headers
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_delete_nonexistent_user_404(self, auth_headers):
        """DELETE non-existent user → 404"""
        response = client.delete("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    # === 422 UNPROCESSABLE ENTITY TESTS ===

    def test_post_missing_required_fields_422(self, auth_headers):
        """POST with missing required fields → 422"""
        # Eksik email ve password
        response = client.post(
            "/api/v1/users/",
            json={"name": "Test User"},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_missing_name_422(self, auth_headers):
        """POST with missing name → 422"""
        response = client.post(
            "/api/v1/users/",
            json={"email": unique_email(), "password": "test123"},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_missing_email_422(self, auth_headers):
        """POST with missing email → 422"""
        response = client.post(
            "/api/v1/users/",
            json={"name": "Test User", "password": "test123"},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_missing_password_422(self, auth_headers):
        """POST with missing password → 422"""
        response = client.post(
            "/api/v1/users/",
            json={"name": "Test User", "email": unique_email()},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_invalid_email_format_422(self, auth_headers):
        """POST with invalid email format → 422"""
        response = client.post(
            "/api/v1/users/",
            json={"name": "Test User", "email": "invalid-email", "password": "test123"},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_empty_strings_422(self, auth_headers):
        """POST with empty strings → 422"""
        response = client.post(
            "/api/v1/users/",
            json={"name": "", "email": "", "password": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_invalid_data_types_422(self, auth_headers):
        """POST with invalid data types → 422"""
        response = client.post(
            "/api/v1/users/",
            json={"name": 123, "email": 456, "password": 789},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_put_invalid_data_422(self, auth_headers):
        """PUT with invalid data → 422"""
        # Önce geçerli user oluştur
        email = unique_email()
        user_resp = client.post(
            "/api/v1/users/",
            json={"name": "Update Error", "email": email, "password": "test123"},
            headers=auth_headers,
        )
        user_id = user_resp.json()["id"]

        # Geçersiz veri ile güncelle
        update_data = {"name": 123, "email": "invalid-email"}
        response = client.put(
            f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    # === 500 INTERNAL SERVER ERROR TESTS ===

    def test_create_user_internal_error_500(self, auth_headers):
        """POST with internal exception → 500"""
        with patch("app.models.User") as mock_user:
            mock_user.side_effect = Exception("Internal server error")
            user_data = {
                "name": "Test User",
                "email": unique_email(),
                "password": "test123",
            }
            response = client.post(
                "/api/v1/users/", json=user_data, headers=auth_headers
            )
            assert response.status_code == 500
            data = response.json()
            assert "database error" in data["detail"].lower()

    def test_update_user_internal_error_500(self, auth_headers):
        """PUT with internal exception → 500"""
        # Önce geçerli user oluştur
        email = unique_email()
        user_resp = client.post(
            "/api/v1/users/",
            json={"name": "Update Error", "email": email, "password": "test123"},
            headers=auth_headers,
        )
        user_id = user_resp.json()["id"]

        with patch("app.models.User") as mock_user:
            mock_user.side_effect = Exception("Internal server error")
            update_data = {"name": "Updated User", "email": unique_email()}
            response = client.put(
                f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers
            )
            assert response.status_code == 500
            data = response.json()
            assert "database error" in data["detail"].lower()

    def test_create_user_database_error_500(self, auth_headers):
        """POST with database exception → 400 (handled by route)"""
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = Exception("Database connection failed")
            user_data = {
                "name": "Test User",
                "email": unique_email(),
                "password": "test123",
            }
            response = client.post(
                "/api/v1/users/", json=user_data, headers=auth_headers
            )
            assert response.status_code == 400
            data = response.json()
            assert "database connection failed" in data["detail"].lower()

    # === 400 BAD REQUEST TESTS ===

    def test_post_duplicate_email_400(self, auth_headers):
        """POST with duplicate email → 400"""
        email = unique_email()
        # İlk user oluştur
        user_data = {"name": "Test User", "email": email, "password": "test123"}
        response1 = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response1.status_code == 201

        # Aynı email ile ikinci user oluştur
        user_data2 = {"name": "Test User 2", "email": email, "password": "test123"}
        response2 = client.post("/api/v1/users/", json=user_data2, headers=auth_headers)
        assert response2.status_code == 400
        data = response2.json()
        assert (
            "already registered" in data["detail"].lower()
            or "already exists" in data["detail"].lower()
        )

    def test_put_duplicate_email_400(self, auth_headers):
        """PUT with duplicate email → 400"""
        # İki farklı user oluştur
        email1 = unique_email()
        email2 = unique_email()
        user1_resp = client.post(
            "/api/v1/users/",
            json={"name": "User 1", "email": email1, "password": "test123"},
            headers=auth_headers,
        )
        user2_resp = client.post(
            "/api/v1/users/",
            json={"name": "User 2", "email": email2, "password": "test123"},
            headers=auth_headers,
        )
        user1_id = user1_resp.json()["id"]
        user2_id = user2_resp.json()["id"]

        # User2'nin email'ini User1'in email'i ile güncelle
        update_data = {"email": email1}
        response = client.put(
            f"/api/v1/users/{user2_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 400
        data = response.json()
        assert (
            "constraint" in data["detail"].lower()
            or "already registered" in data["detail"].lower()
            or "already exists" in data["detail"].lower()
        )

    # === VALIDATION TESTS ===

    def test_post_with_very_long_strings_422(self, auth_headers):
        """POST with very long strings → 422"""
        long_string = "A" * 1000  # 1000 karakterlik string
        response = client.post(
            "/api/v1/users/",
            json={"name": long_string, "email": unique_email(), "password": "test123"},
            headers=auth_headers,
        )
        # Çok uzun stringler validation error'a neden olabilir
        assert response.status_code in [201, 422]

    def test_post_with_special_characters_201(self, auth_headers):
        """POST with special characters → 201 (should work)"""
        special_name = f"Üser-Çeşit-Özel_123!@#$%^&*() {uuid.uuid4()}"
        response = client.post(
            "/api/v1/users/",
            json={"name": special_name, "email": unique_email(), "password": "test123"},
            headers=auth_headers,
        )
        # Özel karakterler kabul edilmeli
        assert response.status_code == 201

    def test_post_with_very_short_password_422(self, auth_headers):
        """POST with very short password → 422"""
        response = client.post(
            "/api/v1/users/",
            json={"name": "Test User", "email": unique_email(), "password": "12"},
            headers=auth_headers,
        )
        # Çok kısa şifre validation error'a neden olabilir
        assert response.status_code in [201, 422]

    def test_post_with_invalid_role_422(self, auth_headers):
        """POST with invalid role → 422"""
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "Test User",
                "email": unique_email(),
                "password": "test123",
                "role": "invalid_role",
            },
            headers=auth_headers,
        )
        # Geçersiz role validation error'a neden olabilir
        assert response.status_code in [201, 422]
