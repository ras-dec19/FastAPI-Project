from app import models, schemas, utils


def test_root(client):
    res = client.get("/")

    assert res.status_code == 200
    assert res.json().get("Message") == "Welcome to my api!!"


def test_create_user(client, user_data):
    res = client.post("/users/", json=user_data)
    new_user = schemas.UserOut(**res.json())

    assert res.status_code == 201
    assert new_user.email == user_data["email"]


def test_create_user_password_is_hashed(client, db_session, user_data):
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201

    user_in_db = (
        db_session.query(models.User)
        .filter(models.User.email == user_data["email"])
        .first()
    )

    assert user_in_db is not None
    assert user_in_db.password != user_data["password"]
    assert utils.verify(user_data["password"], user_in_db.password)


def test_create_user_duplicate_email(client, test_user):
    res = client.post(
        "/users/",
        json={
            "email": test_user["email"],
            "password": "password123",
        },
    )

    assert res.status_code == 409
    assert res.json()["detail"] == "Email is already registered."


def test_get_user(client, test_user):
    res = client.get(f"/users/{test_user['id']}")
    found_user = schemas.UserOut(**res.json())

    assert res.status_code == 200
    assert found_user.id == test_user["id"]
    assert found_user.email == test_user["email"]


def test_get_user_not_found(client):
    res = client.get("/users/999999")

    assert res.status_code == 404
    assert res.json()["detail"] == "User with id: 999999 does not exist"
