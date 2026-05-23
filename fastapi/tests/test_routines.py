def test_get_routines_requires_auth(client):
    response = client.get("/routines/")
    assert response.status_code == 401


def test_create_and_list_routines(client, auth_headers):
    create_response = client.post(
        "/routines/",
        json={"name": "Push Day", "description": "Upper body", "workout_ids": []},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    routine = create_response.json()
    assert routine["name"] == "Push Day"
    assert routine["description"] == "Upper body"
    assert routine["workouts"] == []

    list_response = client.get("/routines/", headers=auth_headers)
    assert list_response.status_code == 200
    routines = list_response.json()
    assert len(routines) == 1
    assert routines[0]["name"] == "Push Day"


def test_get_routine_by_id(client, auth_headers):
    create_response = client.post(
        "/routines/",
        json={"name": "Pull Day", "description": "Back and biceps", "workout_ids": []},
        headers=auth_headers,
    )
    routine_id = create_response.json()["id"]

    get_response = client.get(f"/routines/{routine_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Pull Day"


def test_create_routine_with_workouts(client, auth_headers):
    workout_response = client.post(
        "/workouts/",
        json={"name": "Row", "description": "Back exercise"},
        headers=auth_headers,
    )
    workout_id = workout_response.json()["id"]

    routine_response = client.post(
        "/routines/",
        json={
            "name": "Back Routine",
            "description": "Rows and pulls",
            "workout_ids": [workout_id],
        },
        headers=auth_headers,
    )
    assert routine_response.status_code == 201
    routine = routine_response.json()
    assert len(routine["workouts"]) == 1
    assert routine["workouts"][0]["id"] == workout_id
    assert routine["workouts"][0]["name"] == "Row"


def test_get_routine_not_found(client, auth_headers):
    response = client.get("/routines/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Routine not found"


def test_delete_routine(client, auth_headers):
    create_response = client.post(
        "/routines/",
        json={"name": "Leg Day", "description": "Squats", "workout_ids": []},
        headers=auth_headers,
    )
    routine_id = create_response.json()["id"]

    delete_response = client.delete(
        "/routines/",
        params={"routine_id": routine_id},
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/routines/{routine_id}", headers=auth_headers)
    assert get_response.status_code == 404
