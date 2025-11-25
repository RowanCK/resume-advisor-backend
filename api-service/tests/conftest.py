import pytest
from datetime import datetime, timedelta, timezone
import jwt
from api.app import create_app

@pytest.fixture
def app():
    # Testing config
    test_config = {
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret-key", 
    }

    app = create_app(test_config)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def jwt_token(app):
    """Create a valid JWT token for testing"""
    payload = {
        "user_id": 999,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(
        payload,
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )
    return token


@pytest.fixture
def auth_header(jwt_token):
    """Return Authorization header for authenticated requests"""
    return {"Authorization": f"Bearer {jwt_token}"}
