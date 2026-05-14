# 04 — Tasks

MVP를 3개 Phase로 순차 진행한다.
**확장 단계는 이 문서에 포함하지 않는다. 별도 문서에서 다룬다.**

---

## 진행 규칙

| 규칙 | 내용 |
|---|---|
| **순서 준수** | 단계는 위에서 아래로만 진행한다 |
| **병렬 금지** | 이전 단계 검증이 완료되기 전에 다음 단계를 시작하지 않는다 |
| **검증 필수** | 각 단계의 검증 방법을 통과해야 완료로 간주한다 |
| **Phase 간 게이트** | 각 Phase의 모든 체크리스트가 ✅ 되어야 다음 Phase로 넘어간다 |

---

## Phase 1 — 설계 ✅ 완료

> CLAUDE.md 및 docs/ 6종 문서 작성

| # | 단계 | 검증 방법 |
|---|---|---|
| 1 | `CLAUDE.md` 작성 — 역할·필독문서·절대규칙·모호요청 처리 | 파일 존재 확인 + 5개 절대규칙 항목 포함 여부 |
| 2 | `docs/00-overview.md` 작성 — 문서 지도·읽기 순서·관심사 분리 | 6개 파일 매핑표 + 읽기 순서 다이어그램 포함 여부 |
| 3 | `docs/01-product.md` 작성 — 목표·페르소나·MVP 범위 | 목표 1문장 + 페르소나 + 성공 기준 5개 포함 여부 |
| 4 | `docs/02-specs.md` 작성 — Task 모델·API 계약·화면 명세 | 필드 7개 + API 5개 + 화면 명세 4종 포함 여부 |
| 5 | `docs/03-design.md` 작성 — 기술 결정 8개 + 의존성 정책 | 결정표 8개 + 의존성 추가 정책 항목 포함 여부 |
| 6 | `docs/04-tasks.md` 작성 — Phase 1·2·3 체크리스트 | Phase별 단계 수 확인 (10·10·8) |
| 7 | `docs/05-conventions.md` 작성 — 코딩 컨벤션·브랜치·커밋 규칙 | 파일 존재 확인 + 브랜치 전략·커밋 규칙 포함 여부 |
| 8 | `.gitignore` 작성 — `.env`, `__pycache__`, `node_modules` 등 | `.env` 항목 포함 여부 |
| 9 | `README.md` 작성 — 프로젝트 소개·시작 방법 | 파일 존재 + 실행 방법 1개 이상 포함 여부 |
| 10 | 원격 저장소 푸시 (`main` 브랜치) | `git log --oneline` 으로 커밋 이력 확인, GitHub에서 파일 노출 확인 |

---

## Phase 2 — 백엔드

> FastAPI 기반 CRUD API 5개 구현 및 Swagger 검증

| # | 단계 | 검증 방법 |
|---|---|---|
| 1 | `backend/` 폴더 생성 + `requirements.txt` 작성 (fastapi, uvicorn, sqlalchemy, python-dotenv) | `requirements.txt` 존재 + 4개 패키지 명시 확인 |
| 2 | `.env` 파일 생성 (`DATABASE_URL` 등) + `.gitignore` 포함 확인 | `.env` 가 `git status`에서 untracked로 표시 안 되는지 확인 |
| 3 | `backend/database.py` — SQLAlchemy 엔진·세션 설정 (SQLite) | `python -c "from database import SessionLocal; print('ok')"` 오류 없음 |
| 4 | `backend/models.py` — `Task` 모델 정의 (7개 필드) | `Base.metadata.create_all()` 실행 후 `tasks` 테이블 생성 확인 |
| 5 | `backend/schemas.py` — Pydantic 스키마 (`TaskCreate`, `TaskUpdate`, `TaskResponse`) | import 오류 없음 + 필드 일치 확인 |
| 6 | `backend/crud.py` — DB CRUD 함수 5종 구현 | 단위 테스트 또는 Python 셸에서 create·read·update·delete 각 1회 실행 확인 |
| 7 | `backend/main.py` — FastAPI 앱 + 라우터 5개 등록 | `uvicorn main:app --reload` 실행 후 서버 기동 확인 |
| 8 | `POST /api/tasks` · `GET /api/tasks` 동작 확인 | Swagger UI (`/docs`) 또는 curl로 201·200 응답 확인 |
| 9 | `GET /api/tasks/:id` · `PUT /api/tasks/:id` · `DELETE /api/tasks/:id` 동작 확인 | 존재 id → 200/204, 없는 id → 404 응답 확인 |
| 10 | 검증 오류 케이스 확인 + `git push` | `title` 누락 → 400, `status` 오값 → 400 응답 확인 후 커밋·푸시 |

---

## Phase 3 — 프론트엔드

> Vanilla JS + Tailwind CDN으로 메인 화면 구현 및 API 연결

| # | 단계 | 검증 방법 |
|---|---|---|
| 1 | `frontend/` 폴더 생성 + `index.html` 기본 구조 (Tailwind CDN 포함) | 브라우저에서 파일 열기 — 빈 화면이라도 콘솔 오류 없음 |
| 2 | 헤더·레이아웃·카드 영역 마크업 + Mac OS 톤 스타일 적용 | 360px 뷰포트에서 레이아웃 미파괴 확인 (Chrome DevTools) |
| 3 | `frontend/app.js` — API 연결 모듈 작성 (`fetchTasks`, `createTask`, `updateTask`, `deleteTask`) | 콘솔에서 함수 호출 후 네트워크 탭 요청 확인 |
| 4 | 태스크 목록 렌더링 — `GET /api/tasks` 응답으로 카드 동적 생성 (status 배지 + D-N HH:MM) | 백엔드 실행 상태에서 목록 카드 정상 표시 확인 |
| 5 | 태스크 추가 폼 — `title` / `due_at` / `status` 입력 후 `POST /api/tasks` 호출 | 폼 제출 → 카드 즉시 추가 확인, 빈 title 제출 시 오류 메시지 확인 |
| 6 | 수정 모달 — 카드 클릭 → pre-fill → `PUT /api/tasks/:id` 호출 | 수정 저장 후 카드 내용 즉시 갱신 확인 |
| 7 | 삭제 — 휴지통 아이콘 → 확인 다이얼로그 → `DELETE /api/tasks/:id` 호출 | 삭제 후 카드 목록에서 제거 확인 |
| 8 | 라이트/다크 테마 토글 + 3초 폴링 + `git push` | 토글 후 새로고침 시 테마 유지 확인 (localStorage), 폴링으로 외부 변경 반영 확인 후 커밋·푸시 |
