"""카테고리 기능 Playwright E2E 테스트"""
import pytest
from playwright.sync_api import Page, expect

BASE = "http://127.0.0.1:8001"


@pytest.fixture(autouse=True)
def clean_tasks(page: Page):
    """각 테스트 전 DB 클리어"""
    import requests
    tasks = requests.get(f"{BASE}/api/tasks").json()
    for t in tasks:
        requests.delete(f"{BASE}/api/tasks/{t['id']}")
    yield


def add_task(page: Page, title: str, category: str = "", status: str = "todo"):
    page.get_by_role("button", name="+ 새 태스크").click()
    page.locator("#fTitle").fill(title)
    if category:
        page.locator("#fCategory").fill(category)
    page.locator("#fStatus").select_option(status)
    page.get_by_role("button", name="저장").click()
    page.wait_for_timeout(400)


def test_category_input_visible_in_modal(page: Page):
    """모달에 카테고리 입력 필드가 표시된다"""
    page.goto(BASE)
    page.get_by_role("button", name="+ 새 태스크").click()
    expect(page.locator("#fCategory")).to_be_visible()
    page.keyboard.press("Escape")


def test_category_saved_and_shown_on_card(page: Page):
    """카테고리를 입력하면 카드에 뱃지로 표시된다"""
    page.goto(BASE)
    add_task(page, "카테고리 테스트", category="디자인")
    page.wait_for_timeout(500)
    expect(page.locator("#col-todo")).to_contain_text("디자인")


def test_no_category_no_badge(page: Page):
    """카테고리 없는 태스크는 카드에 카테고리 뱃지가 없다"""
    page.goto(BASE)
    add_task(page, "뱃지 없는 태스크")
    page.wait_for_timeout(500)
    # 카드 영역에 카테고리 뱃지 클래스(bg-purple)가 없어야 함
    cards = page.locator("#col-todo article")
    assert "bg-purple" not in cards.inner_html()


def test_filter_bar_shows_category_pill(page: Page):
    """카테고리가 있는 태스크 추가 시 필터 바에 해당 카테고리 버튼이 생긴다"""
    page.goto(BASE)
    add_task(page, "필터 테스트", category="백엔드")
    page.wait_for_timeout(600)
    expect(page.locator("#filterBar")).to_contain_text("백엔드")
    expect(page.locator("#filterBar")).to_contain_text("전체")


def test_filter_shows_only_matching_tasks(page: Page):
    """카테고리 필터 클릭 시 해당 카테고리 태스크만 표시된다"""
    page.goto(BASE)
    add_task(page, "백엔드 태스크", category="백엔드")
    add_task(page, "프론트 태스크", category="프론트")
    page.wait_for_timeout(600)

    page.locator("#filterBar button", has_text="백엔드").click()
    page.wait_for_timeout(300)

    expect(page.locator("#col-todo")).to_contain_text("백엔드 태스크")
    expect(page.locator("#col-todo")).not_to_contain_text("프론트 태스크")


def test_filter_all_resets_to_full_list(page: Page):
    """'전체' 필터 클릭 시 모든 태스크가 다시 표시된다"""
    page.goto(BASE)
    add_task(page, "태스크 A", category="A")
    add_task(page, "태스크 B", category="B")
    page.wait_for_timeout(600)

    page.locator("#filterBar button", has_text="A").click()
    page.wait_for_timeout(300)
    expect(page.locator("#col-todo")).not_to_contain_text("태스크 B")

    page.locator("#filterBar button", has_text="전체").click()
    page.wait_for_timeout(300)
    expect(page.locator("#col-todo")).to_contain_text("태스크 A")
    expect(page.locator("#col-todo")).to_contain_text("태스크 B")


def test_datalist_populated_with_existing_categories(page: Page):
    """기존 카테고리가 datalist 옵션으로 채워진다"""
    page.goto(BASE)
    add_task(page, "기존 카테고리 태스크", category="운영")
    page.wait_for_timeout(600)

    page.get_by_role("button", name="+ 새 태스크").click()
    # datalist에 "운영" 옵션이 있는지 확인
    options = page.locator("#categoryList option")
    values = [options.nth(i).get_attribute("value") for i in range(options.count())]
    assert "운영" in values
    page.keyboard.press("Escape")


def test_category_editable_on_existing_task(page: Page):
    """기존 태스크의 카테고리를 수정 모달에서 변경할 수 있다"""
    page.goto(BASE)
    add_task(page, "수정 태스크", category="구버전")
    page.wait_for_timeout(500)

    page.locator("#col-todo article").first.click()
    page.wait_for_timeout(300)
    cat_input = page.locator("#fCategory")
    expect(cat_input).to_have_value("구버전")

    cat_input.fill("신버전")
    page.get_by_role("button", name="저장").click()
    page.wait_for_timeout(500)

    expect(page.locator("#col-todo")).to_contain_text("신버전")
    expect(page.locator("#col-todo")).not_to_contain_text("구버전")
