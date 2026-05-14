# 02 — Specs

---

## Task 모델

### 필드 정의

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|---|---|---|---|---|
| `id` | INTEGER (PK, AUTO_INCREMENT) | — | 자동 생성 | 태스크 고유 식별자 |
| `title` | VARCHAR(200) | ✅ | — | 태스크 제목 |
| `description` | TEXT | — | `NULL` | 태스크 상세 설명 |
| `status` | ENUM | — | `todo` | `todo` / `in_progress` / `done` |
| `due_at` | DATETIME (UTC) | — | `NULL` | 마감시각 (날짜+시간, ISO 8601) |
| `created_at` | DATETIME (UTC) | — | 자동 생성 | 생성 시각 |
| `updated_at` | DATETIME (UTC) | — | 자동 갱신 | 마지막 수정 시각 |

### 검증 규칙

| 조건 | 응답 코드 | 설명 |
|---|---|---|
| `title` 누락 또는 빈 문자열 | `400 Bad Request` | 필수 필드 |
| `title` 길이 200자 초과 | `400 Bad Request` | VARCHAR(200) 제한 |
| `status` 허용값 외 입력 | `400 Bad Request` | `todo` / `in_progress` / `done` 만 허용 |
| `due_at` ISO 8601 형식 불일치 | `400 Bad Request` | 예: `2026-05-12T18:00:00Z` 형식 필요 |
| 존재하지 않는 `id` 요청 | `404 Not Found` | GET 단건 · PUT · DELETE 공통 |

---

## REST API

Base URL: `/api/tasks`

### 엔드포인트 목록

| 메서드 | 경로 | 상태 코드 | 설명 |
|---|---|---|---|
| `POST` | `/api/tasks` | `201 Created` | 태스크 생성 |
| `GET` | `/api/tasks` | `200 OK` | 태스크 목록 조회 |
| `GET` | `/api/tasks/:id` | `200 OK` | 태스크 단건 조회 |
| `PUT` | `/api/tasks/:id` | `200 OK` | 태스크 수정 (부분 수정 허용) |
| `DELETE` | `/api/tasks/:id` | `204 No Content` | 태스크 삭제 |

### 응답 필드 차이

| 엔드포인트 | `description` 포함 여부 |
|---|---|
| `GET /api/tasks` (목록) | ❌ 제외 — 목록 렌더링 성능 고려 |
| `GET /api/tasks/:id` (단건) | ✅ 포함 |

### 요청/응답 예시

**POST /api/tasks**
```json
// Request Body
{
  "title": "API 설계 완료",
  "description": "REST 5개 엔드포인트 명세 작성",
  "status": "in_progress",
  "due_at": "2026-05-12T18:00:00Z"
}

// Response 201
{
  "id": 1,
  "title": "API 설계 완료",
  "description": "REST 5개 엔드포인트 명세 작성",
  "status": "in_progress",
  "due_at": "2026-05-12T18:00:00Z",
  "created_at": "2026-05-14T09:00:00Z",
  "updated_at": "2026-05-14T09:00:00Z"
}
```

**GET /api/tasks**
```json
// Response 200 — description 제외
[
  {
    "id": 1,
    "title": "API 설계 완료",
    "status": "in_progress",
    "due_at": "2026-05-12T18:00:00Z",
    "created_at": "2026-05-14T09:00:00Z",
    "updated_at": "2026-05-14T09:00:00Z"
  }
]
```

**PUT /api/tasks/:id** — 부분 수정 허용 (보내지 않은 필드는 변경하지 않음)
```json
// Request Body (일부 필드만 전송 가능)
{
  "status": "done"
}

// Response 200
{
  "id": 1,
  "title": "API 설계 완료",
  "description": "REST 5개 엔드포인트 명세 작성",
  "status": "done",
  "due_at": "2026-05-12T18:00:00Z",
  "created_at": "2026-05-14T09:00:00Z",
  "updated_at": "2026-05-14T10:30:00Z"
}
```

---

## 화면 명세

CRUD 4종 모두 **페이지 이동 없이 한 화면**에서 완결된다.

### 추가 — 입력 폼

| 요소 | 설명 |
|---|---|
| `title` 입력 | 텍스트 인풋, 필수, placeholder: "태스크 제목" |
| `due_at` 입력 | `datetime-local` 인풋, 선택 |
| `status` 선택 | 셀렉트박스, `todo` / `in_progress` / `done`, 기본 `todo` |
| 저장 버튼 | `POST /api/tasks` 호출 → 목록 갱신 |

### 목록 — 태스크 카드

카드 1장이 태스크 1개를 나타낸다.

| 요소 | 설명 |
|---|---|
| `status` 배지 | 상태별 색상 구분 (todo: 회색 / in_progress: 파랑 / done: 초록) |
| 마감 표시 | `D-N HH:MM` 형식 — 예: `D-3 18:00` / `D-0 09:30` / 기한 초과 시 `D+N` |
| 카드 클릭 | 수정 모달 진입 |
| 휴지통 아이콘 | 삭제 흐름 진입 |

### 수정 — 카드 클릭 → 모달

1. 카드 클릭 시 수정 모달 오픈
2. 기존 값이 폼 필드에 pre-fill
3. `title` / `description` / `status` / `due_at` 수정 가능
4. 저장 → `PUT /api/tasks/:id` 호출 → 모달 닫힘 → 목록 갱신

### 삭제 — 휴지통 → 확인 → DELETE

1. 카드의 휴지통 아이콘 클릭
2. 확인 다이얼로그 노출: "정말 삭제하시겠습니까?"
3. 확인 → `DELETE /api/tasks/:id` 호출 → 목록에서 카드 제거
4. 취소 → 다이얼로그 닫힘, 변경 없음
