"""
MVP 성공 기준 검증 — 01-product.md 5개 기준 전부 확인

기준 1. 새로고침 후 테마·데이터 유지
기준 2. 360px 레이아웃 미파괴
기준 3. API CRUD 4종 응답시간 200ms 이하
기준 4. CRUD 4종 화면 동작
기준 5. 테마 토글 작동 + localStorage 유지
"""
import time
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


# ── 기준 1. 새로고침 후 테마·데이터 유지 ─────────────────────────────────────
def test_criteria1_data_persists_after_reload(page: Page):
    """새로고침 후 데이터(태스크)가 유지되어야 한다"""
    requests.post(f"{BASE}/api/tasks", json={"title": "새로고침 유지 테스트", "status": "todo"})

    page.goto(BASE)
    page.wait_for_timeout(500)
    expect(page.locator("[data-task-id]")).to_have_count(1)

    page.reload()
    page.wait_for_timeout(500)
    # 새로고침 후에도 카드가 그대로 있어야 함
    expect(page.locator("[data-task-id]")).to_have_count(1)
    expect(page.locator("[data-task-id]")).to_contain_text("새로고침 유지 테스트")


def test_criteria1_theme_persists_after_reload(page: Page):
    """새로고침 후 테마가 유지되어야 한다"""
    page.goto(BASE)
    page.locator("#themeToggle").click()
    assert "dark" in (page.locator("html").get_attribute("class") or "")

    page.reload()
    # 새로고침 후에도 다크 모드 유지
    assert "dark" in (page.locator("html").get_attribute("class") or "")

    stored = page.evaluate("localStorage.getItem('theme')")
    assert stored == "dark", f"localStorage theme={stored}"


# ── 기준 2. 360px 레이아웃 미파괴 ────────────────────────────────────────────
def test_criteria2_layout_360px_no_overflow(page: Page):
    """360px 뷰포트에서 가로 스크롤 없이 레이아웃이 유지되어야 한다"""
    requests.post(f"{BASE}/api/tasks", json={"title": "360px 테스트 태스크", "status": "todo"})

    page.set_viewport_size({"width": 360, "height": 812})
    page.goto(BASE)
    page.wait_for_timeout(500)

    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    client_width = page.evaluate("document.documentElement.clientWidth")

    assert scroll_width <= 360, f"가로 스크롤 발생: scrollWidth={scroll_width}px"
    assert client_width <= 360, f"clientWidth 초과: {client_width}px"

    # 헤더·버튼이 뷰포트 안에 있어야 함
    header_box = page.locator("header").bounding_box()
    assert header_box["x"] >= 0
    assert header_box["width"] <= 360

    add_btn_box = page.locator("#addBtn").bounding_box()
    assert add_btn_box["x"] + add_btn_box["width"] <= 360 + 1  # 1px 허용


def test_criteria2_modal_360px(page: Page):
    """360px에서 모달이 뷰포트 안에 표시되어야 한다"""
    page.set_viewport_size({"width": 360, "height": 812})
    page.goto(BASE)
    page.locator("#addBtn").click()

    modal_box = page.locator("#modal .relative").bounding_box()
    assert modal_box["width"] <= 360, f"모달 너비 초과: {modal_box['width']}px"


# ── 기준 3. API CRUD 4종 응답시간 200ms 이하 ─────────────────────────────────
def test_criteria3_api_response_time_under_200ms():
    """CRUD 4종 API 응답시간이 모두 200ms 이하여야 한다"""
    results = {}

    # POST
    t0 = time.perf_counter()
    res = requests.post(f"{BASE}/api/tasks",
                        json={"title": "응답속도 테스트", "status": "todo"})
    results["POST /api/tasks"] = (time.perf_counter() - t0) * 1000
    task_id = res.json()["id"]

    # GET 목록
    t0 = time.perf_counter()
    requests.get(f"{BASE}/api/tasks")
    results["GET /api/tasks"] = (time.perf_counter() - t0) * 1000

    # GET 단건
    t0 = time.perf_counter()
    requests.get(f"{BASE}/api/tasks/{task_id}")
    results[f"GET /api/tasks/{task_id}"] = (time.perf_counter() - t0) * 1000

    # PUT
    t0 = time.perf_counter()
    requests.put(f"{BASE}/api/tasks/{task_id}", json={"status": "done"})
    results[f"PUT /api/tasks/{task_id}"] = (time.perf_counter() - t0) * 1000

    # DELETE
    t0 = time.perf_counter()
    requests.delete(f"{BASE}/api/tasks/{task_id}")
    results[f"DELETE /api/tasks/{task_id}"] = (time.perf_counter() - t0) * 1000

    print("\n  [응답시간 측정]")
    for endpoint, ms in results.items():
        mark = "PASS" if ms < 200 else "FAIL"
        print(f"  [{mark}] {endpoint}: {ms:.1f}ms")

    failures = {k: v for k, v in results.items() if v >= 200}
    assert not failures, f"200ms 초과 엔드포인트: {failures}"


# ── 기준 4. CRUD 4종 화면 동작 ────────────────────────────────────────────────
def test_criteria4_create_ui(page: Page):
    """추가 — 폼 입력 후 카드가 화면에 나타나야 한다"""
    page.goto(BASE)
    page.locator("#addBtn").click()
    page.locator("#fTitle").fill("UI 추가 테스트")
    page.locator("#fStatus").select_option("in_progress")
    page.locator("#fDueAt").fill("2026-12-31T18:00")
    page.locator("#taskForm button[type=submit]").click()

    page.wait_for_timeout(500)
    expect(page.locator("#col-inprogress [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-inprogress [data-task-id]")).to_contain_text("UI 추가 테스트")


def test_criteria4_list_ui(page: Page):
    """목록 — 서버 데이터가 상태별 컬럼에 카드로 표시되어야 한다"""
    requests.post(f"{BASE}/api/tasks", json={"title": "할일 카드", "status": "todo"})
    requests.post(f"{BASE}/api/tasks", json={"title": "진행 카드", "status": "in_progress"})
    requests.post(f"{BASE}/api/tasks", json={"title": "완료 카드", "status": "done"})

    page.goto(BASE)
    page.wait_for_timeout(500)

    expect(page.locator("#col-todo [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-inprogress [data-task-id]")).to_have_count(1)
    expect(page.locator("#col-done [data-task-id]")).to_have_count(1)


def test_criteria4_update_ui(page: Page):
    """수정 — 카드 클릭 → 모달 → 저장 후 변경사항이 반영되어야 한다"""
    requests.post(f"{BASE}/api/tasks", json={"title": "수정 전 제목", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    page.locator("#col-todo [data-task-id]").first.click()
    expect(page.locator("#fTitle")).to_have_value("수정 전 제목")

    page.locator("#fTitle").fill("수정 후 제목")
    page.locator("#fStatus").select_option("done")
    page.locator("#taskForm button[type=submit]").click()
    page.wait_for_timeout(500)

    expect(page.locator("#col-done [data-task-id]")).to_contain_text("수정 후 제목")
    expect(page.locator("#col-todo [data-task-id]")).to_have_count(0)


def test_criteria4_delete_ui(page: Page):
    """삭제 — 휴지통 → 확인 → 카드가 사라져야 한다"""
    requests.post(f"{BASE}/api/tasks", json={"title": "삭제 테스트", "status": "todo"})
    page.goto(BASE)
    page.wait_for_timeout(500)

    page.on("dialog", lambda d: d.accept())
    page.locator("#col-todo [data-task-id] .btn-delete").first.click()
    page.wait_for_timeout(500)

    expect(page.locator("[data-task-id]")).to_have_count(0)


# ── 기준 5. 테마 토글 작동 ────────────────────────────────────────────────────
def test_criteria5_theme_toggle_light_to_dark(page: Page):
    """라이트 → 다크 토글 시 dark 클래스가 적용되어야 한다"""
    page.goto(BASE)
    assert "dark" not in (page.locator("html").get_attribute("class") or "")

    page.locator("#themeToggle").click()
    assert "dark" in (page.locator("html").get_attribute("class") or "")
    assert page.evaluate("localStorage.getItem('theme')") == "dark"


def test_criteria5_theme_toggle_dark_to_light(page: Page):
    """다크 → 라이트 재토글 시 dark 클래스가 제거되어야 한다"""
    page.goto(BASE)
    page.locator("#themeToggle").click()
    page.locator("#themeToggle").click()
    assert "dark" not in (page.locator("html").get_attribute("class") or "")
    assert page.evaluate("localStorage.getItem('theme')") == "light"


def test_criteria5_theme_persists_reload(page: Page):
    """다크 설정이 새로고침 후에도 유지되어야 한다"""
    page.goto(BASE)
    page.locator("#themeToggle").click()
    page.reload()
    assert "dark" in (page.locator("html").get_attribute("class") or "")
