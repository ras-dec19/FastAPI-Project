import pytest
from app import schemas


@pytest.mark.parametrize(
    "method, url, body",
    [
        ("get", "/posts/", None),
        (
            "post",
            "/posts/",
            {"title": "title", "content": "content", "published": True},
        ),
        ("get", "/posts/1", None),
        ("delete", "/posts/1", None),
        (
            "put",
            "/posts/1",
            {
                "title": "updated title",
                "content": "updated content",
                "published": False,
            },
        ),
    ],
)
def test_unauthorized_user_cannot_access_posts(client, method, url, body):
    if method == "get":
        res = client.get(url)
    elif method == "post":
        res = client.post(url, json=body)
    elif method == "delete":
        res = client.delete(url)
    else:
        res = client.put(url, json=body)

    assert res.status_code == 401


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    posts = [schemas.PostOut(**post) for post in res.json()]

    assert res.status_code == 200
    assert len(posts) == len(test_posts)
    assert posts[0].Post.title == test_posts[0].title
    assert posts[0].votes == 0


def test_get_posts_limit(authorized_client, test_posts):
    res = authorized_client.get("/posts/?limit=2")

    posts = [schemas.PostOut(**post) for post in res.json()]

    assert res.status_code == 200
    assert len(posts) == 2


def test_get_posts_search(authorized_client, test_posts):
    res = authorized_client.get("/posts/?search=first")

    posts = [schemas.PostOut(**post) for post in res.json()]

    assert res.status_code == 200
    assert len(posts) == 1
    assert posts[0].Post.title == "first title"


def test_get_posts_limit_and_skip(authorized_client, test_posts):
    res = authorized_client.get("/posts/?limit=2&skip=1")

    posts = [schemas.PostOut(**post) for post in res.json()]

    assert res.status_code == 200
    assert len(posts) == 2


def test_get_single_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")

    post = schemas.PostOut(**res.json())

    assert res.status_code == 200
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.votes == 0


def test_get_single_post_not_found(authorized_client):
    res = authorized_client.get("/posts/999999")

    assert res.status_code == 404
    assert res.json()["detail"] == "Post with id: 999999 was not found"


def test_get_other_users_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[2].id}")

    post = schemas.PostOut(**res.json())

    assert res.status_code == 200
    assert post.Post.id == test_posts[2].id
    assert post.Post.owner_id == test_posts[2].owner_id


def test_create_post(authorized_client, test_user):
    post_data = {
        "title": "new title",
        "content": "new content",
        "published": True,
    }

    res = authorized_client.post("/posts/", json=post_data)

    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == post_data["title"]
    assert created_post.content == post_data["content"]
    assert created_post.published == post_data["published"]
    assert created_post.owner_id == test_user["id"]


def test_delete_own_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 204


def test_delete_post_not_found(authorized_client):
    res = authorized_client.delete("/posts/999999")

    assert res.status_code == 404
    assert res.json()["detail"] == "Post with id: 999999 was not found"


def test_delete_other_users_post(client, test_posts, token_2):
    res = client.delete(
        f"/posts/{test_posts[0].id}",
        headers={"Authorization": f"Bearer {token_2}"},
    )

    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to perform requested action"


def test_update_own_post(authorized_client, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": False,
    }

    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)

    updated_post = schemas.Post(**res.json())

    assert res.status_code == 200
    assert updated_post.id == test_posts[0].id
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]
    assert updated_post.published == data["published"]


def test_update_post_not_found(authorized_client):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": False,
    }

    res = authorized_client.put("/posts/999999", json=data)

    assert res.status_code == 404
    assert res.json()["detail"] == "Post with id: 999999 was not found"


def test_update_other_users_post(client, test_posts, token_2):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": False,
    }

    res = client.put(
        f"/posts/{test_posts[0].id}",
        json=data,
        headers={"Authorization": f"Bearer {token_2}"},
    )

    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to perform requested action"
