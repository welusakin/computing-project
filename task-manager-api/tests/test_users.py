def _make_user(client, name="Ada", email="ada@example.com"):
    return client.post("/users", json={"name": name, "email": email})


def test_create_user(client):
    res = _make_user(client)
    assert res.status_code == 201
    assert res.get_json() == {
        "id": 1,
        "name": "Ada",
        "email": "ada@example.com",
        "notification_pref": "none",
    }


def test_create_user_rejects_duplicate_email(client):
    _make_user(client)
    res = _make_user(client, name="Other")
    assert res.status_code == 422
    assert res.get_json()["field"] == "email"


def test_create_user_rejects_bad_email(client):
    assert _make_user(client, email="nope").status_code == 422


def test_list_and_get_user(client):
    _make_user(client)
    _make_user(client, name="Bo", email="bo@example.com")
    assert [u["name"] for u in client.get("/users").get_json()] == ["Ada", "Bo"]
    assert client.get("/users/2").get_json()["email"] == "bo@example.com"


def test_get_missing_user_returns_404(client):
    assert client.get("/users/9").status_code == 404
