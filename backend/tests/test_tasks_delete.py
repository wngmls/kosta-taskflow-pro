def test_delete_task_success(client, sample_task):
    task_id = sample_task["id"]
    res = client.delete(f"/api/tasks/{task_id}")
    assert res.status_code == 204


def test_delete_task_removed_from_list(client, sample_task):
    # 삭제 후 목록에서 사라져야 한다
    task_id = sample_task["id"]
    client.delete(f"/api/tasks/{task_id}")
    res = client.get("/api/tasks")
    assert res.json() == []


def test_delete_task_not_found_returns_404(client):
    # 존재하지 않는 id 시 404 반환
    res = client.delete("/api/tasks/99999")
    assert res.status_code == 404
