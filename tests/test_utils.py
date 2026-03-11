from app import utils


def test_hash():
    password = "password123"
    hashed_password = utils.hash(password)

    assert hashed_password != password


def test_verify():
    password = "password123"
    hashed_password = utils.hash(password)

    assert utils.verify(password, hashed_password)


def test_verify_wrong_password():
    password = "password123"
    wrong_password = "wrongpassword"
    hashed_password = utils.hash(password)

    assert not utils.verify(wrong_password, hashed_password)
