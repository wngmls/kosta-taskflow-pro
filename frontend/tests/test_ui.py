"""
프론트엔드 E2E 테스트 — Playwright
대상 서버: http://localhost:8001
"""
import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:8001"


@pytest.fixture(autouse=True)
def clean_db():
    """각 테스트 전 DB 초기화 — 기존 태스크 전부 삭제"""
    import requests
    tasks = requests.get(f"{BASE}/api/tasks").json()
    for t in tasks:
        requests.delete(f"{BASE}/api/tasks/{t['id']}")
    yield


# ── 1. 페이지 로딩 ─────────────────────────────────────────────────────────────
def test_page_loads(page: Page):
    page.goto(BASE)
    expect(page.locator("h1")).to_have_text("TaskFlow Pro")
    expect(page.locator("#addBtn")).to_be_visible()
    expect(page.locator("#themeToggle")).to_be_visible()


# ── 2. 360px 반응형 레이아웃 미파괴 ───────────────────────────────────────────
def test_layout_360px(page: Page):
    page.set_viewport_size({"width": 360, "height": 812})
    page.goto(BASE)
    # 헤더가 뷰포트 안에 있어야 함
    header = page.locator("header")
    expect(header).to_be_visible()
    box = header.bounding_box()
    assert box["width"] <= 360, f"헤더 너비 초과: {box['width']}"
    # 가로 스크롤 없어야 함
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    assert scroll_width <= 360, f"가로 스크롤 발생: scrollWidth={scroll_width}"


# ── 3. 태스크 추가 ─────────────────────────────────────────────────────────────
def test_add_task(page: Page):
    page.goto(BASE)
    page.locator("#addBtn").click()
    expect(page.locator("#modal")).to_be_visible()
    expect(page.locator("#modalTitle")).to_have_text("태스크 추가")

    page.locator("#fTitle").fill("E2E 테스트 태스크")
    page.locator("#fStatus").select_option("in_progress")
    page.locator("#fDueAt").fill("2026-12-31T18:00")
    page.locator("#taskForm button[type=submit]").click()

    # 모달 닫힘 확인
    expect(page.locator("#modal")).not_to_be_visible()
    # 카드가 진행 중 컬럼에 생성됨
    expect(page.locator("#col-inprogress [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-inprogress [data-task-id]")).to_contain_text("E2E 테스트 태스크")


# ── 4. status 배지 표시 ────────────────────────────────────────────────────────
def test_status_badge(page: Page):
    import requests
    requests.post(f"{BASE}/api/tasks", json={"title": "배지 테스트", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)
    badge = page.locator("#col-todo [data-task-id] span").first
    expect(badge).to_contain_text("할 일")


# ── 5. D-N HH:MM 마감 표시 ────────────────────────────────────────────────────
def test_due_display(page: Page):
    import requests
    requests.post(f"{BASE}/api/tasks", json={
        "title": "마감 테스트",
        "status": "todo",
        "due_at": "2099-01-01T09:00:00Z",
    })
    page.goto(BASE)
    page.wait_for_timeout(500)
    card = page.locator("#col-todo [data-task-id]").first
    # D- 형식이 카드 안에 있어야 함
    expect(card).to_contain_text("D-")


# ── 6. 수정 모달 — 카드 클릭 → pre-fill ───────────────────────────────────────
def test_edit_modal_prefill(page: Page):
    import requests
    requests.post(f"{BASE}/api/tasks", json={"title": "수정할 태스크", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    page.locator("#col-todo [data-task-id]").first.click()
    expect(page.locator("#modal")).to_be_visible()
    expect(page.locator("#modalTitle")).to_have_text("태스크 수정")
    expect(page.locator("#fTitle")).to_have_value("수정할 태스크")


def test_edit_task(page: Page):
    import requests
    requests.post(f"{BASE}/api/tasks", json={"title": "원래 제목", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    page.locator("#col-todo [data-task-id]").first.click()
    page.locator("#fTitle").fill("수정된 제목")
    page.locator("#fStatus").select_option("done")
    page.locator("#taskForm button[type=submit]").click()

    page.wait_for_timeout(500)
    expect(page.locator("#col-done [data-task-id]")).to_contain_text("수정된 제목")
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(0)


# ── 7. 삭제 — 휴지통 → confirm → 제거 ────────────────────────────────────────
def test_delete_task(page: Page):
    import requests
    requests.post(f"{BASE}/api/tasks", json={"title": "삭제할 태스크", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    # confirm 다이얼로그 자동 수락
    page.on("dialog", lambda d: d.accept())
    page.locator("#col-todo [data-task-id] .btn-delete").first.click()

    page.wait_for_timeout(500)
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(0)


def test_delete_cancel(page: Page):
    import requests
    requests.post(f"{BASE}/api/tasks", json={"title": "취소 테스트", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    # confirm 다이얼로그 취소
    page.on("dialog", lambda d: d.dismiss())
    page.locator("#col-todo [data-task-id] .btn-delete").first.click()

    page.wait_for_timeout(500)
    # 취소했으므로 카드 그대로 남아 있어야 함
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(1)


# ── 8. 테마 토글 ────────────────────────────────────────────────────────────────
def test_theme_toggle_dark(page: Page):
    page.goto(BASE)
    # 초기 상태: 라이트 (dark 클래스 없음)
    html_class = page.locator("html").get_attribute("class") or ""
    assert "dark" not in html_class

    page.locator("#themeToggle").click()
    html_class = page.locator("html").get_attribute("class") or ""
    assert "dark" in html_class

    # localStorage 저장 확인
    stored = page.evaluate("localStorage.getItem('theme')")
    assert stored == "dark"


def test_theme_persists_after_reload(page: Page):
    page.goto(BASE)
    page.locator("#themeToggle").click()
    assert "dark" in (page.locator("html").get_attribute("class") or "")

    # 새로고침 후에도 다크 유지
    page.reload()
    assert "dark" in (page.locator("html").get_attribute("class") or "")


# ── 9. 빈 title 제출 → 에러 메시지 ───────────────────────────────────────────
def test_add_task_empty_title_shows_error(page: Page):
    page.goto(BASE)
    page.locator("#addBtn").click()
    page.locator("#taskForm button[type=submit]").click()
    expect(page.locator("#formError")).to_be_visible()
    expect(page.locator("#formError")).to_contain_text("제목을 입력해주세요")


# ── 10. ESC 키로 모달 닫기 ────────────────────────────────────────────────────
def test_modal_close_on_escape(page: Page):
    page.goto(BASE)
    page.locator("#addBtn").click()
    expect(page.locator("#modal")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#modal")).not_to_be_visible()
