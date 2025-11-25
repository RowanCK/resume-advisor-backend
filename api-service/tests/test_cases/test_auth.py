import jwt
from datetime import datetime, timedelta, timezone

# This test suite validates require_auth decorator behavior

def register_test_route(app, require_auth):
    """
    Dynamic fake route /protected
    Used to test the require_auth decorator
    """
    @app.route("/protected")
    @require_auth
    def protected_route(auth_user_id=None):
        return {"success": True, "user_id": auth_user_id}, 200


def test_missing_authorization_header(app, client):
    """Test: missing Authorization header should return 401"""
    from api.auth_utils import require_auth
    register_test_route(app, require_auth)

    resp = client.get("/protected")
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Authorization header is missing"


def test_invalid_header_format(app, client):
    """Test: Authorization header is not 'Bearer <token>'"""
    from api.auth_utils import require_auth
    register_test_route(app, require_auth)

    resp = client.get("/protected", headers={"Authorization": "InvalidHeader"})
    assert resp.status_code == 401
    assert "Invalid Authorization header format" in resp.get_json()["error"]


def test_invalid_token_type(app, client):
    """Test: not a Bearer token"""
    from api.auth_utils import require_auth
    register_test_route(app, require_auth)

    resp = client.get("/protected", headers={"Authorization": "Basic 123"})
