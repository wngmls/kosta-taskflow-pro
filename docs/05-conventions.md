# 05 — Conventions

---

## 명명 규칙

| 대상 | 규칙 | 예시 |
|---|---|---|
| 백엔드 변수·함수·파일 | `snake_case` | `task_id`, `get_task_by_id`, `crud.py` |
| 프론트엔드 변수·함수 | `camelCase` | `taskList`, `fetchTasks`, `handleDelete` |
| 프론트엔드 컴포넌트·클래스 | `PascalCase` | `TaskCard`, `ModalDialog` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_TITLE_LENGTH`, `POLL_INTERVAL_MS` |
| DB 테이블·컬럼 | `snake_case` | `tasks`, `due_at`, `created_at` |
| CSS 클래스 | Tailwind 유틸리티 우선, 커스텀 시 `kebab-case` | `task-card`, `status-badge` |

**식별자는 반드시 영어**로 작성한다. **주석은 한국어**로 작성한다.

```python
# 마감시각이 지난 태스크를 필터링한다
def filter_overdue_tasks(tasks: list[Task]) -> list[Task]:
    ...
```

---

## 금지 목록

| 금지 | 이유 | 대안 |
|---|---|---|
| `print()` 디버깅 | 운영 환경 로그 오염, 삭제 누락 시 노이즈 발생 | `logging` 모듈 사용 (`logger.debug()`, `logger.info()`) |
| `bare except` (`except:`) | 모든 예외를 삼켜 원인 추적 불가, 시스템 종료 신호(KeyboardInterrupt)까지 차단 | `except SpecificError as e:` 로 예외 범위를 명시 |
| 비밀번호·키 하드코딩 | 코드·git 이력에 노출 시 보안 사고로 직결 | `.env` 파일에 저장 + `os.getenv('KEY')` 로 읽기 |
| `any` 타입 (TypeScript) | 타입 정보를 제거해 타입 체커의 의미가 사라짐 | 명시적 타입 또는 `unknown` 후 타입 가드 사용 |
| `!important` (CSS) | 캐스케이드 우선순위 구조를 파괴해 유지보수 시 원인 추적 불가 | 셀렉터 명시도를 높이거나 Tailwind 유틸리티 클래스 재구성 |

---

## 테스트

### 도구

- **백엔드**: `pytest` + `httpx` (FastAPI TestClient)
- **프론트**: 수동 E2E (MVP 단계), 자동화는 확장 단계에서 도입

### 테스트 파일 위치

```
backend/
└── tests/
    ├── test_tasks_create.py
    ├── test_tasks_read.py
    ├── test_tasks_update.py
    └── test_tasks_delete.py
```

### 필수 케이스

각 API 엔드포인트마다 아래 3가지 케이스를 반드시 작성한다.

| 케이스 | 설명 | 기대 상태 코드 |
|---|---|---|
| **정상** | 유효한 입력으로 성공 경로 검증 | 200 / 201 / 204 |
| **400** | 필수 필드 누락·형식 위반 등 클라이언트 오류 | 400 Bad Request |
| **404** | 존재하지 않는 `id` 요청 | 404 Not Found |

### 테스트 예시

```python
def test_create_task_success(client):
    res = client.post("/api/tasks", json={"title": "테스트 태스크"})
    assert res.status_code == 201
    assert res.json()["title"] == "테스트 태스크"

def test_create_task_missing_title(client):
    # title 누락 시 400 반환 검증
    res = client.post("/api/tasks", json={})
    assert res.status_code == 400

def test_get_task_not_found(client):
    # 없는 id 요청 시 404 반환 검증
    res = client.get("/api/tasks/99999")
    assert res.status_code == 404
```

### 실행

```bash
cd backend
pytest tests/ -v
```

---

## Git 커밋 규칙

### 형식

```
<type>: <한국어 요약>
```

### 타입 목록

| 타입 | 용도 | 예시 |
|---|---|---|
| `feat` | 새 기능 추가 | `feat: 태스크 삭제 API 구현` |
| `fix` | 버그 수정 | `fix: due_at 형식 검증 누락 수정` |
| `docs` | 문서 변경 (코드 변경 없음) | `docs: 03-design.md 의존성 정책 보완` |
| `refactor` | 동작 변경 없는 코드 개선 | `refactor: crud.py 중복 쿼리 제거` |
| `test` | 테스트 추가·수정 | `test: GET /api/tasks 404 케이스 추가` |
| `chore` | 빌드·설정·패키지 변경 | `chore: requirements.txt python-dotenv 추가` |

### 규칙

- 요약은 **한국어**, 50자 이내
- 코드 식별자(함수명·파일명)는 요약 안에서도 **영어** 유지
- 현재형으로 작성 (`추가했다` ❌ → `추가` ✅)
- `main` 브랜치에 직접 push하지 않는다 — Phase 2부터 feature 브랜치 사용

### 브랜치 전략

```
main          — 검증된 코드만 머지
└── feat/backend-task-api    — Phase 2 백엔드 작업
└── feat/frontend-main-ui    — Phase 3 프론트 작업
└── fix/<이슈-요약>           — 버그 수정
```
