def test_create_task_success(client):
    res = client.post("/api/tasks", json={"title": "새 태스크"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "새 태스크"
    assert data["status"] == "todo"
    assert data["description"] is None
    assert "id" in data
    assert "created_at" in data


def test_create_task_with_all_fields(client):
    res = client.post("/api/tasks", json={
        "title": "전체 필드 태스크",
        "description": "상세 설명",
        "status": "in_progress",
        "due_at": "2026-12-31T18:00:00Z",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["description"] == "상세 설명"
    assert data["status"] == "in_progress"


def test_create_task_missing_title_returns_400(client):
    # title 누락 시 400 반환
    res = client.post("/api/tasks", json={})
    assert res.status_code == 400


def test_create_task_empty_title_returns_400(client):
    # 빈 문자열 title 시 400 반환
    res = client.post("/api/tasks", json={"title": ""})
    assert res.status_code == 400


def test_create_task_title_too_long_returns_400(client):
    # 200자 초과 시 400 반환
    res = client.post("/api/tasks", json={"title": "a" * 201})
    assert res.status_code == 400


def test_create_task_invalid_status_returns_400(client):
    # 허용되지 않는 status 값 시 400 반환
    res = client.post("/api/tasks", json={"title": "태스크", "status": "invalid_status"})
    assert res.status_code == 400
