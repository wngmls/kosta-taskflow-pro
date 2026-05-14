"""
드래그&드롭 — 컬럼 간 태스크 이동 테스트
"""
import requests
import pytest
from playwright.sync_api import Page, expect

BASE = "http://127.0.0.1:8001"


@pytest.fixture(autouse=True)
def clean_db():
    tasks = requests.get(f"{BASE}/api/tasks").json()
    for t in tasks:
        requests.delete(f"{BASE}/api/tasks/{t['id']}")
    yield
    tasks = requests.get(f"{BASE}/api/tasks").json()
    for t in tasks:
        requests.delete(f"{BASE}/api/tasks/{t['id']}")


def drag_to_column(page: Page, card_locator, target_col_id: str):
    """카드를 지정 컬럼으로 드래그한다"""
    card_box = card_locator.bounding_box()
    target_box = page.locator(f"#{target_col_id}").bounding_box()

    src_x = card_box["x"] + card_box["width"] / 2
    src_y = card_box["y"] + card_box["height"] / 2
    dst_x = target_box["x"] + target_box["width"] / 2
    dst_y = target_box["y"] + target_box["height"] / 2

    page.mouse.move(src_x, src_y)
    page.mouse.down()
    page.mouse.move(dst_x, dst_y, steps=10)
    page.mouse.up()
    page.wait_for_timeout(600)


def test_drag_todo_to_inprogress(page: Page):
    """할 일 → 진행 중 이동"""
    requests.post(f"{BASE}/api/tasks", json={"title": "드래그 테스트", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    card = page.locator("#col-todo [data-task-id]").first
    expect(card).to_be_visible()
    drag_to_column(page, card, "col-inprogress")

    expect(page.locator("#col-inprogress [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-inprogress [data-task-id]")).to_contain_text("드래그 테스트")
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(0)


def test_drag_todo_to_done(page: Page):
    """할 일 → 완료 이동"""
    requests.post(f"{BASE}/api/tasks", json={"title": "완료로 이동", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    card = page.locator("#col-todo [data-task-id]").first
    drag_to_column(page, card, "col-done")

    expect(page.locator("#col-done [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(0)


def test_drag_inprogress_to_done(page: Page):
    """진행 중 → 완료 이동"""
    requests.post(f"{BASE}/api/tasks", json={"title": "진행→완료", "status": "in_progress"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    card = page.locator("#col-inprogress [data-task-id]").first
    drag_to_column(page, card, "col-done")

    expect(page.locator("#col-done [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-inprogress [data-task-id]")).to_have_count(0)


def test_drag_same_column_no_change(page: Page):
    """같은 컬럼으로 드래그 → 변경 없음"""
    requests.post(f"{BASE}/api/tasks", json={"title": "제자리 드래그", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    card = page.locator("#col-todo [data-task-id]").first
    drag_to_column(page, card, "col-todo")

    # API 호출 없이 그대로 유지
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(1)


def test_drag_persists_after_reload(page: Page):
    """드래그로 변경한 상태가 새로고침 후에도 유지된다"""
    requests.post(f"{BASE}/api/tasks", json={"title": "새로고침 유지", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    card = page.locator("#col-todo [data-task-id]").first
    drag_to_column(page, card, "col-inprogress")
    expect(page.locator("#col-inprogress [data-task-id]")).to_have_count(1)

    page.reload()
    page.wait_for_timeout(500)
    expect(page.locator("#col-inprogress [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(0)
