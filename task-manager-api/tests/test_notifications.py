import pytest


def _make_user(client, name="Ada", email="ada@example.com"):
    return client.post("/users", json={"name": name, "email": email})


def test_new_user_defaults_to_none(client):
    res = _make_user(client)
    assert res.status_code == 201
    assert res.get_json()["notification_pref"] == "none"


def test_get_notifications_shape(client):
    _make_user(client)
    res = client.get("/users/1/notifications")
    assert res.status_code == 200
    assert res.get_json() == {"user_id": 1, "notification_pref": "none"}


@pytest.mark.parametrize("value", ["email", "sms", "none"])
def test_patch_accepts_valid_values(client, value):
    _make_user(client)
    if value == "none":
        # Move away from the default first so the change is observable.
        assert client.patch(
            "/users/1/notifications", json={"notification_pref": "email"}
        ).status_code == 200

    res = client.patch("/users/1/notifications", json={"notification_pref": value})
    assert res.status_code == 200
    assert res.get_json() == {"user_id": 1, "notification_pref": value}
    assert client.get("/users/1/notifications").get_json() == {
        "user_id": 1,
        "notification_pref": value,
    }


@pytest.mark.parametrize("value", ["push", "", "EMAIL", None, 1, ["email"]])
def test_patch_rejects_invalid_value_and_keeps_stored_value(client, value):
    _make_user(client)
    assert client.patch(
        "/users/1/notifications", json={"notification_pref": "email"}
    ).status_code == 200

    res = client.patch("/users/1/notifications", json={"notification_pref": value})
    assert res.status_code == 422
    assert res.get_json()["error"] == "ValidationError"

    assert client.get("/users/1/notifications").get_json() == {
        "user_id": 1,
        "notification_pref": "email",
    }
    assert client.get("/users/1").get_json()["notification_pref"] == "email"


def test_patch_missing_key_returns_422(client):
    _make_user(client)
    res = client.patch("/users/1/notifications", json={})
    assert res.status_code == 422
    assert res.get_json()["error"] == "ValidationError"
    assert client.get("/users/1/notifications").get_json()["notification_pref"] == "none"


def test_get_notifications_unknown_user_returns_404(client):
    assert client.get("/users/9/notifications").status_code == 404


def test_patch_notifications_unknown_user_returns_404(client):
    res = client.patch("/users/9/notifications", json={"notification_pref": "email"})
    assert res.status_code == 404


def test_user_endpoints_include_notification_pref(client):
    _make_user(client)
    _make_user(client, name="Bo", email="bo@example.com")
    assert client.patch(
        "/users/2/notifications", json={"notification_pref": "sms"}
    ).status_code == 200

    listed = client.get("/users").get_json()
    assert [u["notification_pref"] for u in listed] == ["none", "sms"]
    assert client.get("/users/1").get_json()["notification_pref"] == "none"
    assert client.get("/users/2").get_json()["notification_pref"] == "sms"
