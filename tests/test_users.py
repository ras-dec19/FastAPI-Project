from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    res = client.get("/")
    print(res.json().get("Message"))
    assert res.json().get("Message") == "Welcome to my api!!!"
    assert res.status_code == 200


def test_create_user():
    res = client.post(
        "/users/", json={"email": "test123@gmail.com", "password": "password123"}
    )
    print(res.json())
    assert res.status_code == 201
