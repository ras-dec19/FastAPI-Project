import pytest
import uuid
from app import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

### Fixtures for database setup and test client ###


@pytest.fixture(autouse=True)
def set_testing_env(monkeypatch):
    monkeypatch.setenv("TESTING", "true")


@pytest.fixture(scope="function")
def db_session():
    from app.config import settings
    from app.database import Base

    engine = create_engine(settings.app_database_url)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    from app.main import app
    from app.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


### Fixtures for user creation and authentication ###


@pytest.fixture
def user_data():
    return {
        "email": f"test_{uuid.uuid4().hex}@gmail.com",
        "password": "password123",
    }


@pytest.fixture
def test_user(client, user_data):
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {
        "email": f"test2_{uuid.uuid4().hex}@gmail.com",
        "password": "password123",
    }

    res = client.post("/users/", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    from app.oauth2 import create_access_token

    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def token_2(test_user2):
    from app.oauth2 import create_access_token

    return create_access_token({"user_id": test_user2["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def test_posts(db_session, test_user, test_user2):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user["id"],
        },
        {
            "title": "second title",
            "content": "second content",
            "owner_id": test_user["id"],
        },
        {
            "title": "third title",
            "content": "third content",
            "owner_id": test_user2["id"],
        },
    ]

    posts = [models.Post(**post) for post in posts_data]
    db_session.add_all(posts)
    db_session.commit()

    return db_session.query(models.Post).order_by(models.Post.id).all()
