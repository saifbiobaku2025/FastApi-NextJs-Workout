import os
import sys
from pathlib import Path

import pytest

API_DIR = Path(__file__).resolve().parent.parent / "api"
PROJECT_ROOT = API_DIR.parent
DB_PATH = API_DIR / "workout_app.db"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _remove_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()


@pytest.fixture(scope="session", autouse=True)
def manage_database():
    """Delete workout_app.db before tests and again after the session."""
    os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-pytest"
    os.environ["AUTH_ALGORITHM"] = "HS256"

    _remove_db()

    original_cwd = os.getcwd()
    os.chdir(API_DIR)

    yield

    os.chdir(original_cwd)

    try:
        from api.database import engine

        engine.dispose()
    except ImportError:
        pass

    _remove_db()


@pytest.fixture(scope="session")
def client(manage_database):
    from fastapi.testclient import TestClient
    from api.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def registered_user(client):
    username = f"user_{os.urandom(4).hex()}"
    password = "testpassword123"
    response = client.post(
        "/auth",
        json={"username": username, "password": password},
    )
    assert response.status_code == 201
    return {"username": username, "password": password}


@pytest.fixture
def auth_headers(client, registered_user):
    response = client.post(
        "/auth/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
