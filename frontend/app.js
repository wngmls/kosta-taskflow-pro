const API_BASE = '';

// ── 테마 ──────────────────────────────────────────────────────────────────────
const themeToggle = document.getElementById('themeToggle');
const iconMoon = document.getElementById('iconMoon');
const iconSun = document.getElementById('iconSun');

function applyTheme(isDark) {
    document.documentElement.classList.toggle('dark', isDark);
    iconMoon.classList.toggle('hidden', isDark);
    iconSun.classList.toggle('hidden', !isDark);
}

// 초기 테마 — localStorage 기준, 없으면 라이트
applyTheme(localStorage.getItem('theme') === 'dark');

themeToggle.addEventListener('click', () => {
    const isDark = !document.documentElement.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    applyTheme(isDark);
});

// ── API ───────────────────────────────────────────────────────────────────────
async function fetchTasks() {
    const res = await fetch(`${API_BASE}/api/tasks`);
    if (!res.ok) throw new Error('목록 조회 실패');
    return res.json();
}

async function createTask(payload) {
    const res = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw await res.json();
    return res.json();
}

async function updateTask(id, payload) {
    const res = await fetch(`${API_BASE}/api/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw await res.json();
    return res.json();
}

async function deleteTask(id) {
    const res = await fetch(`${API_BASE}/api/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('삭제 실패');
}

async function fetchCategories() {
    const res = await fetch(`${API_BASE}/api/categories`);
    if (!res.ok) return [];
    return res.json();
}

// ── 유틸 ──────────────────────────────────────────────────────────────────────
// D-N HH:MM 형식으로 변환
function formatDue(isoStr) {
    if (!isoStr) return null;
    const due = new Date(isoStr);
    const now = new Date();
    const dueDay = new Date(due.getFullYear(), due.getMonth(), due.getDate());
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const diffDays = Math.round((dueDay - today) / 86_400_000);
    const h = String(due.getHours()).padStart(2, '0');
    const m = String(due.getMinutes()).padStart(2, '0');
    const label = diffDays >= 0 ? `D-${diffDays}` : `D+${Math.abs(diffDays)}`;
    return `${label} ${h}:${m}`;
}

// UTC ISO → datetime-local 인풋 값 형식
function toDatetimeLocal(isoStr) {
    if (!isoStr) return '';
    const d = new Date(isoStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

const STATUS_LABEL = { todo: '할 일', in_progress: '진행 중', done: '완료' };

const STATUS_BADGE = {
    todo: 'bg-gray-100 text-gray-600 dark:bg-[#3A3A3C] dark:text-gray-300',
    in_progress: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
    done: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
};

// ── 렌더 ──────────────────────────────────────────────────────────────────────
let taskCache = [];
let activeCategory = null;

// 드래그 중인 태스크 id
let draggingId = null;

const COL_STATUS = { 'col-todo': 'todo', 'col-inprogress': 'in_progress', 'col-done': 'done' };

function renderFilterBar(tasks) {
    const categories = [...new Set(tasks.map(t => t.category).filter(Boolean))].sort();
    const bar = document.getElementById('filterBar');
    bar.innerHTML = ['전체', ...categories].map(cat => {
        const val = cat === '전체' ? null : cat;
        const isActive = activeCategory === val;
        return `<button data-cat="${cat === '전체' ? '' : escapeHtml(cat)}"
          class="px-3 py-1 rounded-full text-xs font-medium transition-colors
          ${isActive
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-[#3A3A3C] text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-[#4A4A4C]'
          }">${escapeHtml(cat)}</button>`;
    }).join('');
    bar.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            activeCategory = btn.dataset.cat || null;
            renderBoard(taskCache);
            renderFilterBar(taskCache);
        });
    });
}

function renderBoard(tasks) {
    taskCache = tasks;
    const visible = activeCategory ? tasks.filter(t => t.category === activeCategory) : tasks;

    const cols = { todo: [], in_progress: [], done: [] };
    visible.forEach(t => { if (cols[t.status]) cols[t.status].push(t); });

    const colEl = { todo: 'col-todo', in_progress: 'col-inprogress', done: 'col-done' };
    const cntEl = { todo: 'count-todo', in_progress: 'count-inprogress', done: 'count-done' };

    Object.keys(cols).forEach(status => {
        const list = cols[status];
        document.getElementById(colEl[status]).innerHTML =
            list.length ? list.map(renderCard).join('') : renderEmptySlot();
        document.getElementById(cntEl[status]).textContent = list.length || '';
    });

    // 카드 이벤트 연결
    document.querySelectorAll('[data-task-id]').forEach(card => {
        const id = Number(card.dataset.taskId);
        card.querySelector('.btn-edit').addEventListener('click', e => {
            e.stopPropagation();
            openEditModal(id);
        });
        card.querySelector('.btn-delete').addEventListener('click', e => {
            e.stopPropagation();
            handleDelete(id);
        });
        card.addEventListener('click', () => openEditModal(id));

        // 드래그 시작
        card.addEventListener('dragstart', e => {
            draggingId = id;
            e.dataTransfer.effectAllowed = 'move';
            // 반투명 효과 — 다음 프레임에서 적용해야 고스트 이미지에 영향 없음
            requestAnimationFrame(() => card.classList.add('opacity-40'));
        });
        card.addEventListener('dragend', () => {
            draggingId = null;
            card.classList.remove('opacity-40');
        });
    });

    // 컬럼 드롭존 이벤트 연결
    Object.keys(COL_STATUS).forEach(colId => {
        const col = document.getElementById(colId);
        col.addEventListener('dragover', e => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            col.classList.add('ring-2', 'ring-blue-400', 'ring-inset', 'rounded-xl');
        });
        col.addEventListener('dragleave', e => {
            // 자식 요소로 이동 시 이벤트 무시
            if (col.contains(e.relatedTarget)) return;
            col.classList.remove('ring-2', 'ring-blue-400', 'ring-inset', 'rounded-xl');
        });
        col.addEventListener('drop', async e => {
            e.preventDefault();
            col.classList.remove('ring-2', 'ring-blue-400', 'ring-inset', 'rounded-xl');
            if (!draggingId) return;
            const newStatus = COL_STATUS[colId];
            const task = taskCache.find(t => t.id === draggingId);
            if (!task || task.status === newStatus) return;
            try {
                await updateTask(draggingId, { status: newStatus });
                await loadAndRender();
            } catch {
                alert('상태 변경에 실패했습니다.');
            }
        });
    });
}

function renderCard(task) {
    const due = formatDue(task.due_at);
    const isOverdue = due?.startsWith('D+');
    const dueHtml = due
        ? `<span class="text-xs font-medium tabular-nums ${isOverdue
            ? 'text-red-500 dark:text-red-400'
            : 'text-gray-400 dark:text-gray-500'}">${due}</span>`
        : '';
    const catHtml = task.category
        ? `<span class="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300 font-medium">${escapeHtml(task.category)}</span>`
        : '';

    return `
    <article data-task-id="${task.id}" draggable="true"
      class="group bg-white/80 dark:bg-[#2C2C2E]/80 backdrop-blur-md border border-gray-200/60 dark:border-[#3A3A3C]/60
             rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-grab active:cursor-grabbing p-4 flex flex-col gap-2">
      <div class="flex items-start gap-2">
        <p class="flex-1 text-sm font-medium text-gray-900 dark:text-white leading-snug break-words">
          ${escapeHtml(task.title)}
        </p>
        <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
          <button class="btn-edit h-8 w-8 flex items-center justify-center rounded-lg
                         text-gray-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                  title="수정" aria-label="수정">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5
                   m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
          </button>
          <button class="btn-delete h-8 w-8 flex items-center justify-center rounded-lg
                         text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                  title="삭제" aria-label="삭제">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7
                   m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_BADGE[task.status]}">
          ${STATUS_LABEL[task.status]}
        </span>
        ${catHtml}
        ${dueHtml}
      </div>
    </article>`;
}

function renderEmptySlot() {
    return `<div class="rounded-xl border-2 border-dashed border-gray-200 dark:border-[#3A3A3C] h-16"></div>`;
}

// ── 폴링 ──────────────────────────────────────────────────────────────────────
async function loadAndRender() {
    try {
        const [tasks, categories] = await Promise.all([fetchTasks(), fetchCategories()]);
        const dl = document.getElementById('categoryList');
        dl.innerHTML = categories.map(c => `<option value="${escapeHtml(c)}"></option>`).join('');
        renderFilterBar(tasks);
        renderBoard(tasks);
    } catch {
        // 폴링 실패는 조용히 무시 — 다음 주기에 재시도
    }
}

loadAndRender();
setInterval(loadAndRender, 3_000);

// ── 모달 ──────────────────────────────────────────────────────────────────────
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const taskForm = document.getElementById('taskForm');
const fTitle = document.getElementById('fTitle');
const fDesc = document.getElementById('fDesc');
const fCategory = document.getElementById('fCategory');
const fStatus = document.getElementById('fStatus');
const fDueAt = document.getElementById('fDueAt');
const formError = document.getElementById('formError');
let editingId = null;

function openModal(title, values = {}) {
    modalTitle.textContent = title;
    fTitle.value = values.title ?? '';
    fDesc.value = values.description ?? '';
    fCategory.value = values.category ?? '';
    fStatus.value = values.status ?? 'todo';
    fDueAt.value = toDatetimeLocal(values.due_at);
    formError.classList.add('hidden');
    modal.classList.remove('hidden');
    requestAnimationFrame(() => fTitle.focus());
}

function closeModal() {
    modal.classList.add('hidden');
    editingId = null;
}

document.getElementById('addBtn').addEventListener('click', () => {
    editingId = null;
    openModal('태스크 추가');
});
document.getElementById('cancelBtn').addEventListener('click', closeModal);
document.getElementById('modalOverlay').addEventListener('click', closeModal);

// ESC 키로 모달 닫기
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});

function openEditModal(id) {
    const task = taskCache.find(t => t.id === id);
    if (!task) return;
    editingId = id;
    openModal('태스크 수정', task);
}

taskForm.addEventListener('submit', async e => {
    e.preventDefault();
    const title = fTitle.value.trim();
    if (!title) {
        showFormError('제목을 입력해주세요.');
        return;
    }
    const payload = {
        title,
        description: fDesc.value.trim() || null,
        category: fCategory.value.trim() || null,
        status: fStatus.value,
        due_at: fDueAt.value ? new Date(fDueAt.value).toISOString() : null,
    };
    try {
        if (editingId) {
            await updateTask(editingId, payload);
        } else {
            await createTask(payload);
        }
        closeModal();
        await loadAndRender();
    } catch {
        showFormError('저장에 실패했습니다. 다시 시도해주세요.');
    }
});

function showFormError(msg) {
    formError.textContent = msg;
    formError.classList.remove('hidden');
}

// ── 삭제 ──────────────────────────────────────────────────────────────────────
async function handleDelete(id) {
    const task = taskCache.find(t => t.id === id);
    if (!task) return;
    if (!confirm(`"${task.title}" 태스크를 삭제할까요?`)) return;
    try {
        await deleteTask(id);
        await loadAndRender();
    } catch {
        alert('삭제에 실패했습니다. 다시 시도해주세요.');
    }
}
