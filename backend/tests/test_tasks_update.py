def test_update_task_success(client, sample_task):
    task_id = sample_task["id"]
    res = client.put(f"/api/tasks/{task_id}", json={"status": "done"})
    assert res.status_code == 200
    assert res.json()["status"] == "done"


def test_update_task_partial(client, sample_task):
    # 전송하지 않은 필드는 변경되지 않아야 한다
    task_id = sample_task["id"]
    res = client.put(f"/api/tasks/{task_id}", json={"title": "수정된 제목"})
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "수정된 제목"
    assert data["status"] == "todo"


def test_update_task_invalid_status_returns_400(client, sample_task):
    # 잘못된 status 값 시 400 반환
    task_id = sample_task["id"]
    res = client.put(f"/api/tasks/{task_id}", json={"status": "invalid"})
    assert res.status_code == 400


def test_update_task_not_found_returns_404(client):
    # 존재하지 않는 id 시 404 반환
    res = client.put("/api/tasks/99999", json={"status": "done"})
    assert res.status_code == 404
