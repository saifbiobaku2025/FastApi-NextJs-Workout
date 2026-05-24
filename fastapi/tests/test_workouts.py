def test_get_workouts_requires_auth(client):
    response = client.get("/workouts/workouts")
    assert response.status_code == 401


def test_create_and_list_workouts(client, auth_headers):
    create_response = client.post(
        "/workouts",
        json={"name": "Bench Press", "description": "Chest day"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    workout = create_response.json()
    assert workout["name"] == "Bench Press"
    assert workout["description"] == "Chest day"
    assert workout["id"] is not None
    assert set(workout.keys()) == {"id", "name", "description"}

    list_response = client.get("/workouts/workouts", headers=auth_headers)
    assert list_response.status_code == 200
    workouts = list_response.json()
    assert len(workouts) == 1
    assert workouts[0]["name"] == "Bench Press"


def test_get_workout_by_id(client, auth_headers):
    create_response = client.post(
        "/workouts",
        json={"name": "Squat", "description": "Leg day"},
        headers=auth_headers,
    )
    workout_id = create_response.json()["id"]

    get_response = client.get(f"/workouts/{workout_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Squat"


def test_get_workout_not_found(client, auth_headers):
    response = client.get("/workouts/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Workout not found"


def test_delete_workout(client, auth_headers):
    create_response = client.post(
        "/workouts",
        json={"name": "Deadlift", "description": "Back day"},
        headers=auth_headers,
    )
    workout_id = create_response.json()["id"]

    delete_response = client.delete(
        "/workouts/",
        params={"workout_id": workout_id},
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/workouts/{workout_id}", headers=auth_headers)
    assert get_response.status_code == 404
