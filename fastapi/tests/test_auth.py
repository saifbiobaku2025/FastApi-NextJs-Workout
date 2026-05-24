def test_create_user(client):
    response = client.post(
        "/auth",
        json={"username": "new_user", "password": "securepass123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "new_user"
    assert isinstance(body["id"], int)
