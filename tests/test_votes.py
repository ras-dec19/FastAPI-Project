def test_unauthorized_user_cannot_vote(client, test_posts):
    res = client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
    )

    assert res.status_code == 401


def test_vote_on_nonexistent_post(authorized_client):
    res = authorized_client.post(
        "/vote/",
        json={"post_id": 999999, "dir": 1},
    )

    assert res.status_code == 404
    assert res.json()["detail"] == "Post with id: 999999 does not exist"


def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
    )

    assert res.status_code == 201
    assert res.json()["message"] == "successfully added vote"


def test_vote_twice_on_post(authorized_client, test_posts, test_user):
    authorized_client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
    )

    res = authorized_client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
    )

    assert res.status_code == 409
    assert (
        res.json()["detail"]
        == f"user {test_user['id']} has already voted on post {test_posts[0].id}"
    )


def test_delete_vote(authorized_client, test_posts):
    authorized_client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
    )

    res = authorized_client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 0},
    )

    assert res.status_code == 204


def test_delete_vote_nonexistent(authorized_client, test_posts):
    res = authorized_client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 0},
    )

    assert res.status_code == 404
    assert res.json()["detail"] == "Vote does not exist"


def test_different_users_can_vote_on_same_post(client, test_posts, token, token_2):
    res1 = client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    res2 = client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
        headers={"Authorization": f"Bearer {token_2}"},
    )

    assert res1.status_code == 201
    assert res2.status_code == 201
