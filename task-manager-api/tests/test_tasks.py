def test_create_task_returns_201_with_defaults(client):
    res = client.post("/tasks", json={"title": "Write report"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["title"] == "Write report"
    assert body["done"] is False
    assert body["user_id"] is None


def test_create_task_rejects_blank_title(client):
    res = client.post("/tasks", json={"title": "   "})
    assert res.status_code == 422
    assert res.get_json()["error"] == "ValidationError"


def test_create_task_rejects_unknown_user(client):
    res = client.post("/tasks", json={"title": "x", "user_id": 99})
    assert res.status_code == 422
    assert res.get_json()["field"] == "user_id"


def test_list_tasks_filters_by_done(client):
    client.post("/tasks", json={"title": "a"})
    second = client.post("/tasks", json={"title": "b"}).get_json()
    client.patch(f"/tasks/{second['id']}", json={"done": True})

    assert [t["title"] for t in client.get("/tasks?done=true").get_json()] == ["b"]
    assert [t["title"] for t in client.get("/tasks?done=false").get_json()] == ["a"]
    assert len(client.get("/tasks").get_json()) == 2


def test_patch_task_updates_fields(client):
    task = client.post("/tasks", json={"title": "old"}).get_json()
    res = client.patch(f"/tasks/{task['id']}", json={"title": "new", "done": True})
    assert res.status_code == 200
    assert res.get_json()["title"] == "new"
    assert res.get_json()["done"] is True


def test_get_missing_task_returns_404(client):
    assert client.get("/tasks/123").status_code == 404


def test_delete_task(client):
    task = client.post("/tasks", json={"title": "temp"}).get_json()
    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_create_task_defaults_priority_to_3(client):
    res = client.post("/tasks", json={"title": "no priority given"})
    assert res.status_code == 201
    assert res.get_json()["priority"] == 3


def test_create_task_accepts_priority(client):
    res = client.post("/tasks", json={"title": "urgent", "priority": 1})
    assert res.status_code == 201
    assert res.get_json()["priority"] == 1


def test_create_task_rejects_out_of_range_priority(client):
    for bad in (0, 6):
        res = client.post("/tasks", json={"title": "x", "priority": bad})
        assert res.status_code == 422
        assert res.get_json()["field"] == "priority"


def test_patch_task_updates_priority(client):
    task = client.post("/tasks", json={"title": "t"}).get_json()
    res = client.patch(f"/tasks/{task['id']}", json={"priority": 1})
    assert res.status_code == 200
    assert res.get_json()["priority"] == 1


def test_patch_task_rejects_invalid_priority(client):
    task = client.post("/tasks", json={"title": "t"}).get_json()
    for bad in (9, "high"):
        res = client.patch(f"/tasks/{task['id']}", json={"priority": bad})
        assert res.status_code == 422
        assert res.get_json()["field"] == "priority"
    assert client.get(f"/tasks/{task['id']}").get_json()["priority"] == 3


def test_patch_task_null_priority_is_ignored(client):
    task = client.post("/tasks", json={"title": "t", "priority": 2}).get_json()
    res = client.patch(f"/tasks/{task['id']}", json={"priority": None})
    assert res.status_code == 200
    assert res.get_json()["priority"] == 2


def test_list_tasks_filters_by_priority(client):
    client.post("/tasks", json={"title": "a", "priority": 1})
    client.post("/tasks", json={"title": "b", "priority": 3})
    client.post("/tasks", json={"title": "c", "priority": 1})

    res = client.get("/tasks?priority=1")
    assert res.status_code == 200
    assert [t["title"] for t in res.get_json()] == ["a", "c"]


def test_list_tasks_priority_filter_returns_empty_when_no_match(client):
    client.post("/tasks", json={"title": "a", "priority": 2})
    res = client.get("/tasks?priority=5")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_tasks_rejects_invalid_priority_filter(client):
    for bad in ("9", "abc"):
        res = client.get(f"/tasks?priority={bad}")
        assert res.status_code == 422
        assert res.get_json()["field"] == "priority"


def test_list_tasks_combines_done_and_priority_filters(client):
    first = client.post("/tasks", json={"title": "a", "priority": 1}).get_json()
    client.post("/tasks", json={"title": "b", "priority": 1})
    client.patch(f"/tasks/{first['id']}", json={"done": True})

    res = client.get("/tasks?priority=1&done=true")
    assert [t["title"] for t in res.get_json()] == ["a"]


def test_create_task_rejects_non_integer_priority(client):
    for bad in ("2", 2.5, True):
        res = client.post("/tasks", json={"title": "x", "priority": bad})
        assert res.status_code == 422
        assert res.get_json()["field"] == "priority"


def test_priority_is_returned_by_get_and_list(client):
    task = client.post("/tasks", json={"title": "x", "priority": 4}).get_json()
    assert client.get(f"/tasks/{task['id']}").get_json()["priority"] == 4
    assert client.get("/tasks").get_json()[0]["priority"] == 4


def test_list_tasks_rejects_empty_priority_filter(client):
    res = client.get("/tasks?priority=")
    assert res.status_code == 422
    assert res.get_json()["field"] == "priority"


def _make_three(client):
    client.post("/tasks", json={"title": "low", "priority": 5})
    client.post("/tasks", json={"title": "urgent", "priority": 1})
    client.post("/tasks", json={"title": "normal", "priority": 3})


def test_list_tasks_default_order_is_by_id(client):
    _make_three(client)
    assert [t["title"] for t in client.get("/tasks").get_json()] == ["low", "urgent", "normal"]


def test_list_tasks_sort_by_priority(client):
    _make_three(client)
    client.post("/tasks", json={"title": "urgent-2", "priority": 1})
    res = client.get("/tasks?sort=priority")
    assert res.status_code == 200
    assert [t["title"] for t in res.get_json()] == ["urgent", "urgent-2", "normal", "low"]


def test_list_tasks_rejects_unknown_sort(client):
    res = client.get("/tasks?sort=title")
    assert res.status_code == 422
    assert res.get_json()["field"] == "sort"


def test_list_tasks_sort_combines_with_done_filter(client):
    _make_three(client)
    client.patch("/tasks/1", json={"done": True})
    client.patch("/tasks/3", json={"done": True})
    res = client.get("/tasks?sort=priority&done=true")
    assert [t["title"] for t in res.get_json()] == ["normal", "low"]
