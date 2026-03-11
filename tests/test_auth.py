import pytest
from jose import jwt

from app import schemas
from app.config import settings


def test_login_user(client, test_user):
    res = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )

    login_res = schemas.Token(**res.json())

    payload = jwt.decode(
        login_res.access_token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    user_id = payload.get("user_id")

    assert res.status_code == 200
    assert user_id == test_user["id"]
    assert login_res.token_type == "bearer"


@pytest.mark.parametrize(
    "data, status_code",
    [
        ({"username": "wrongemail@gmail.com", "password": "password123"}, 401),
        ({"username": "correct_email", "password": "wrongpassword"}, 401),
        ({"username": "wrongemail@gmail.com", "password": "wrongpassword"}, 401),
        ({"password": "password123"}, 422),
        ({"username": "correct_email"}, 422),
    ],
)
def test_incorrect_login(client, test_user, data, status_code):
    login_data = data.copy()

    if login_data.get("username") == "correct_email":
        login_data["username"] = test_user["email"]

    res = client.post("/login", data=login_data)

    assert res.status_code == status_code

    if status_code == 401:
        assert res.json()["detail"] == "Invalid credentials"
    else:
        assert "detail" in res.json()
