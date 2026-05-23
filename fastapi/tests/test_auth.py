def test_create_user(client):
    response = client.post(
        "/auth/",
        json={"username": "new_user", "password": "securepass123"},
    )
    assert response.status_code == 201


def test_login_success(client, registered_user):
    response = client.post(
        "/auth/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


def test_login_wrong_password(client, registered_user):
    response = client.post(
        "/auth/token",
        data={
            "username": registered_user["username"],
            "password": "wrong-password",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate user"


def test_login_unknown_user(client):
    response = client.post(
        "/auth/token",
        data={"username": "nobody", "password": "anypassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate user"
