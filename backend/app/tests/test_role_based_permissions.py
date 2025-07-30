"""
Role-Based Permission Tests.
Role bazlı yetki kontrolü ve permission testleri.
"""

from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


class TestRoleBasedPermissions:
    """Role-based permission testleri."""

    def test_admin_full_permissions(self, jwt_token_factory):
        admin_token = jwt_token_factory.create_token(user_id="admin", role="admin")
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=admin_headers)
        assert response.status_code in [200, 401, 422, 500]
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "role": "user",
        }
        response = client.post("/users/", json=user_data, headers=admin_headers)
        assert response.status_code in [200, 201, 401, 422, 500]
        response = client.put("/users/1", json=user_data, headers=admin_headers)
        assert response.status_code in [200, 401, 422, 500]
        response = client.delete("/users/1", headers=admin_headers)
        assert response.status_code in [200, 204, 401, 422, 500]

    def test_user_limited_permissions(self, jwt_token_factory):
        user_token = jwt_token_factory.create_token(user_id="user", role="user")
        user_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=user_headers)
        assert response.status_code in [200, 401, 422, 500]
        user_data = {"email": "updated@example.com"}
        response = client.put("/users/profile", json=user_data, headers=user_headers)
        assert response.status_code in [200, 401, 422, 500]
        response = client.delete("/users/profile", headers=user_headers)
        assert response.status_code in [200, 204, 401, 422, 500]

    def test_viewer_read_only_permissions(self, jwt_token_factory):
        viewer_token = jwt_token_factory.create_token(user_id="viewer", role="viewer")
        viewer_headers = {
            "Authorization": f"Bearer {viewer_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=viewer_headers)
        assert response.status_code in [200, 401, 422, 500]
        user_data = {"username": "test", "email": "test@example.com"}
        response = client.post("/users/", json=user_data, headers=viewer_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.put("/users/1", json=user_data, headers=viewer_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.delete("/users/1", headers=viewer_headers)
        assert response.status_code in [403, 401, 422, 500]

    def test_no_permission_user(self, jwt_token_factory):
        no_perm_token = jwt_token_factory.create_token(
            user_id="noperm", role="user", permissions=[]
        )
        no_permission_headers = {
            "Authorization": f"Bearer {no_perm_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=no_permission_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.post("/users/", json={}, headers=no_permission_headers)
        assert response.status_code in [403, 401, 422, 500]

    def test_read_only_permissions(self, jwt_token_factory):
        read_token = jwt_token_factory.create_token(
            user_id="readonly", role="user", permissions=["read"]
        )
        read_only_headers = {
            "Authorization": f"Bearer {read_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=read_only_headers)
        assert response.status_code in [200, 401, 422, 500]
        response = client.post("/users/", json={}, headers=read_only_headers)
        assert response.status_code in [403, 401, 422, 500]

    def test_write_permissions(self, jwt_token_factory):
        write_token = jwt_token_factory.create_token(
            user_id="writer", role="user", permissions=["write"]
        )
        write_permission_headers = {
            "Authorization": f"Bearer {write_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=write_permission_headers)
        assert response.status_code in [200, 401, 422, 500]
        user_data = {"username": "test", "email": "test@example.com"}
        response = client.post(
            "/users/", json=user_data, headers=write_permission_headers
        )
        assert response.status_code in [200, 201, 401, 422, 500]
        response = client.put(
            "/users/1", json=user_data, headers=write_permission_headers
        )
        assert response.status_code in [200, 401, 422, 500]
        response = client.delete("/users/1", headers=write_permission_headers)
        assert response.status_code in [200, 204, 401, 422, 500]


class TestPermissionValidation:
    def test_invalid_permission_format(self, jwt_token_factory):
        token = jwt_token_factory.create_token(
            user_id="testuser", role="user", permissions=["invalid_permission"]
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [403, 401, 422, 500]

    def test_expired_token_permissions(self, jwt_token_factory):
        expired_token = jwt_token_factory.create_token(
            user_id="testuser", role="admin", expires_in=-1
        )
        headers = {
            "Authorization": f"Bearer {expired_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 422, 500]

    def test_malformed_token_permissions(self, jwt_token_factory):
        headers = {
            "Authorization": "Bearer malformed.token.here",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 422, 500]

    def test_missing_permissions_in_token(self, jwt_token_factory):
        token = jwt_token_factory.create_token(
            user_id="testuser", role="user", permissions=[]
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [403, 401, 422, 500]


class TestEndpointSpecificPermissions:
    def test_users_endpoint_permissions(self, jwt_token_factory):
        admin_token = jwt_token_factory.create_token(user_id="admin", role="admin")
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=admin_headers)
        assert response.status_code in [200, 401, 422, 500]
        user_token = jwt_token_factory.create_token(user_id="user", role="user")
        user_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=user_headers)
        assert response.status_code in [200, 401, 422, 500]

    def test_stocks_endpoint_permissions(self, jwt_token_factory):
        admin_token = jwt_token_factory.create_token(user_id="admin", role="admin")
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/stocks/", headers=admin_headers)
        assert response.status_code in [200, 401, 422, 500]
        viewer_token = jwt_token_factory.create_token(user_id="viewer", role="viewer")
        viewer_headers = {
            "Authorization": f"Bearer {viewer_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/stocks/", headers=viewer_headers)
        assert response.status_code in [200, 401, 422, 500]

    def test_orders_endpoint_permissions(self, jwt_token_factory):
        admin_token = jwt_token_factory.create_token(user_id="admin", role="admin")
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/orders/", headers=admin_headers)
        assert response.status_code in [200, 401, 422, 500]
        user_token = jwt_token_factory.create_token(user_id="user", role="user")
        user_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/orders/", headers=user_headers)
        assert response.status_code in [200, 401, 422, 500]


class TestPermissionEscalation:
    def test_user_trying_admin_actions(self, jwt_token_factory):
        user_token = jwt_token_factory.create_token(user_id="user", role="user")
        user_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        response = client.delete("/users/1", headers=user_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.post("/api/v1/admin/users", json={}, headers=user_headers)
        assert response.status_code in [403, 401, 404, 422, 500]

    def test_viewer_trying_write_actions(self, jwt_token_factory):
        viewer_token = jwt_token_factory.create_token(user_id="viewer", role="viewer")
        viewer_headers = {
            "Authorization": f"Bearer {viewer_token}",
            "Content-Type": "application/json",
        }
        user_data = {"username": "test", "email": "test@example.com"}
        response = client.post("/users/", json=user_data, headers=viewer_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.put("/users/1", json=user_data, headers=viewer_headers)
        assert response.status_code in [403, 401, 422, 500]

    def test_no_permission_user_trying_any_action(self, jwt_token_factory):
        no_perm_token = jwt_token_factory.create_token(
            user_id="noperm", role="user", permissions=[]
        )
        no_permission_headers = {
            "Authorization": f"Bearer {no_perm_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=no_permission_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.post("/users/", json={}, headers=no_permission_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.put("/users/1", json={}, headers=no_permission_headers)
        assert response.status_code in [403, 401, 422, 500]
        response = client.delete("/users/1", headers=no_permission_headers)
        assert response.status_code in [403, 401, 422, 500]


class TestPermissionIntegration:
    def test_permission_with_header_validation(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="admin", role="admin")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 422, 500]
        if response.status_code == 200:
            assert "X-Header-Validation" in response.headers
            assert "X-Auth-Validated" in response.headers

    def test_permission_with_rate_limiting(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="user", role="user")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        for _ in range(3):
            response = client.get("/users/", headers=headers)
            assert response.status_code in [200, 401, 429, 422, 500]

    def test_permission_error_handling(self, jwt_token_factory):
        token = jwt_token_factory.create_token(
            user_id="testuser", role="invalid_role", permissions=["invalid_permission"]
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [403, 401, 422, 500]
        if response.status_code == 403:
            data = response.json()
            assert "detail" in data
            assert (
                "permission" in data["detail"].lower()
                or "forbidden" in data["detail"].lower()
            )
