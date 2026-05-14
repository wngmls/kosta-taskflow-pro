def test_list_tasks_empty(client):
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert res.json() == []


def test_list_tasks_returns_items(client, sample_task):
    res = client.get("/api/tasks")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["title"] == "샘플 태스크"


def test_list_tasks_excludes_description(client, sample_task):
    # 목록 응답에 description 포함 불가 (02-specs.md)
    res = client.get("/api/tasks")
    assert "description" not in res.json()[0]


def test_get_task_success(client, sample_task):
    task_id = sample_task["id"]
    res = client.get(f"/api/tasks/{task_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == task_id
    assert "description" in data


def test_get_task_not_found_returns_404(client):
    # 존재하지 않는 id 시 404 반환
    res = client.get("/api/tasks/99999")
    assert res.status_code == 404
