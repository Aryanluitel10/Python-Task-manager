/* =============================================================================
   app.js — Task Manager frontend logic
   Single-page app: login/register screens + task dashboard.
   Communicates with the Flask API (app.py) via fetch().
   ============================================================================= */

// ── State ────────────────────────────────────────────────────────────────────

let currentUser        = null;
let allTasks           = [];
let selectedIdx        = null;   // currently highlighted table row
let editingIdx         = null;   // null = add mode, number = edit mode
let pendingDeleteIdx   = null;
let pendingCompleteIdx = null;

// ── API helper ───────────────────────────────────────────────────────────────

async function api(method, path, body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res  = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

// ── Toast notifications ───────────────────────────────────────────────────────

function toast(msg, type = "info") {
  const icons = { success: "✔", error: "✕", info: "ℹ", warning: "⚠" };
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span>${icons[type]}</span><span>${msg}</span>`;
  document.getElementById("toast-container").appendChild(el);
  setTimeout(() => {
    el.style.animation = "toast-out 0.25s ease forwards";
    setTimeout(() => el.remove(), 260);
  }, 3000);
}

// ── Screen switching ──────────────────────────────────────────────────────────

function showLogin() {
  document.getElementById("login-screen").classList.remove("hidden");
  document.getElementById("app-screen").classList.add("hidden");
  setTimeout(() => document.getElementById("login-user").focus(), 50);
}

function showApp(username) {
  currentUser = username;
  document.getElementById("login-screen").classList.add("hidden");
  document.getElementById("app-screen").classList.remove("hidden");
  document.getElementById("user-avatar").textContent     = username[0].toUpperCase();
  document.getElementById("user-name-label").textContent = username;
  loadTasks();
}

// ── Authentication ────────────────────────────────────────────────────────────

async function doLogin() {
  const u = document.getElementById("login-user").value.trim();
  const p = document.getElementById("login-pass").value;
  document.getElementById("login-error").textContent = "";
  try {
    const data = await api("POST", "/api/login", { username: u, password: p });
    showApp(data.username);
  } catch (e) {
    document.getElementById("login-error").textContent = e.message;
  }
}

async function doRegister() {
  const u     = document.getElementById("reg-user").value.trim();
  const p     = document.getElementById("reg-pass").value;
  const c     = document.getElementById("reg-confirm").value;
  const errEl = document.getElementById("reg-error");
  errEl.textContent = "";

  if (!u)           { errEl.textContent = "Username cannot be blank."; return; }
  if (!p)           { errEl.textContent = "Password cannot be blank."; return; }
  if (p.length < 6) { errEl.textContent = "Password must be at least 6 characters."; return; }
  if (p !== c)      { errEl.textContent = "Passwords do not match."; return; }

  try {
    const data = await api("POST", "/api/register", { username: u, password: p });
    closeRegisterDirect();
    showApp(data.username);
    toast(`Welcome, ${data.username}! Account created.`, "success");
  } catch (e) {
    errEl.textContent = e.message;
  }
}

function doLogout() {
  currentUser = null;
  allTasks    = [];
  selectedIdx = null;
  document.getElementById("login-user").value = "";
  document.getElementById("login-pass").value = "";
  showLogin();
}

// ── Register modal ────────────────────────────────────────────────────────────

function openRegisterModal() {
  ["reg-user", "reg-pass", "reg-confirm"].forEach(id => {
    document.getElementById(id).value = "";
  });
  document.getElementById("reg-error").textContent  = "";
  document.getElementById("match-hint").textContent = "";
  document.getElementById("match-hint").className   = "match-hint";
  setStrengthBar("");
  setRules("");
  document.getElementById("register-overlay").classList.remove("hidden");
  setTimeout(() => document.getElementById("reg-user").focus(), 50);
}

function closeRegisterModal(e) {
  if (e.target === document.getElementById("register-overlay")) closeRegisterDirect();
}

function closeRegisterDirect() {
  document.getElementById("register-overlay").classList.add("hidden");
}

// Password strength bar
function setStrengthBar(pw) {
  const fill  = document.getElementById("strength-fill");
  const label = document.getElementById("strength-label");
  if (!pw) { fill.style.width = "0%"; label.textContent = ""; return; }

  let score = 0;
  if (pw.length >= 6)           score++;
  if (pw.length >= 10)          score++;
  if (/[0-9]/.test(pw))         score++;
  if (/[A-Z]/.test(pw))         score++;
  if (/[^a-zA-Z0-9]/.test(pw))  score++;

  const colors = ["#f43f5e", "#fb923c", "#facc15", "#22c55e", "#16a34a"];
  const labels = ["Weak", "Fair", "Good", "Strong", "Very strong"];
  fill.style.width      = `${(score / 5) * 100}%`;
  fill.style.background = colors[score - 1] || "#f43f5e";
  label.textContent     = labels[score - 1] || "";
  label.style.color     = colors[score - 1] || "#f43f5e";
}

// Password rules checklist
function setRules(pw) {
  const mark = (id, pass) => document.getElementById(id).classList.toggle("pass", pass);
  mark("rule-len",  pw.length >= 6);
  mark("rule-num",  /[0-9]/.test(pw));
  mark("rule-case", /[A-Z]/.test(pw) && /[a-z]/.test(pw));
}

// Confirm password match hint
function updateMatchHint() {
  const p    = document.getElementById("reg-pass").value;
  const c    = document.getElementById("reg-confirm").value;
  const hint = document.getElementById("match-hint");
  if (!c) { hint.textContent = ""; hint.className = "match-hint"; return; }
  const match = p === c;
  hint.textContent = match ? "✓ Passwords match" : "✗ Passwords don't match";
  hint.className   = `match-hint ${match ? "match-ok" : "match-bad"}`;
}

// ── Task data ─────────────────────────────────────────────────────────────────

async function loadTasks() {
  try {
    const data = await api("GET", `/api/tasks/${encodeURIComponent(currentUser)}`);
    allTasks = data.tasks;
    renderTable();
  } catch (e) {
    toast("Could not load tasks.", "error");
  }
}

// ── Table rendering ───────────────────────────────────────────────────────────

const P_BADGE = { High: "badge-high", Medium: "badge-med", Low: "badge-low" };
const S_BADGE = { Todo: "badge-todo", "In Progress": "badge-prog", Done: "badge-done" };
const P_ICON  = { High: "▲", Medium: "◆", Low: "▼" };
const S_ICON  = { Todo: "○", "In Progress": "▶", Done: "✓" };

function renderTable() {
  const query  = document.getElementById("search-input").value.trim().toLowerCase();
  const priFlt = document.getElementById("filter-priority").value;
  const staFlt = document.getElementById("filter-status").value;
  const tbody  = document.getElementById("task-tbody");
  tbody.innerHTML = "";

  let shown = 0;
  const total = allTasks.length;

  allTasks.forEach((t, i) => {
    const pri = t.priority || "Medium";
    const sta = t.status   || "Todo";

    if (priFlt !== "All" && pri !== priFlt) return;
    if (staFlt !== "All" && sta !== staFlt) return;
    if (query && !(
      t.title.toLowerCase().includes(query) ||
      (t.description || "").toLowerCase().includes(query) ||
      (t.due_date    || "").toLowerCase().includes(query)
    )) return;

    const tr = document.createElement("tr");
    tr.dataset.idx = i;
    if (sta === "Done")    tr.classList.add("done-row");
    if (i === selectedIdx) tr.classList.add("selected");

    tr.innerHTML = `
      <td><div class="row-check">${i === selectedIdx ? "✓" : ""}</div></td>
      <td><span class="task-title">${escHtml(t.title)}</span></td>
      <td style="text-align:center">
        <span class="badge ${P_BADGE[pri] || ""}">${P_ICON[pri] || ""} ${escHtml(pri)}</span>
      </td>
      <td style="text-align:center">
        <span class="badge ${S_BADGE[sta] || ""}">${S_ICON[sta] || ""} ${escHtml(sta)}</span>
      </td>
      <td style="text-align:center;font-size:12px;color:var(--text2)">${escHtml(t.due_date || "—")}</td>
      <td style="color:var(--text2);font-size:12px">${escHtml(t.description || "")}</td>
      <td>
        <div class="row-actions">
          <button class="row-btn row-btn-edit" title="Edit"
            onclick="event.stopPropagation(); selectRow(${i}); editSelected()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          ${sta !== "Done" ? `
          <button class="row-btn row-btn-done" title="Mark complete"
            onclick="event.stopPropagation(); selectRow(${i}); completeSelected()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>` : ""}
          <button class="row-btn row-btn-delete" title="Delete"
            onclick="event.stopPropagation(); selectRow(${i}); deleteSelected()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            </svg>
          </button>
        </div>
      </td>
    `;

    tr.addEventListener("click",   () => selectRow(i));
    tr.addEventListener("dblclick", () => { selectRow(i); editSelected(); });
    tbody.appendChild(tr);
    shown++;
  });

  updateStats(total);

  const hidden = total - shown;
  document.getElementById("status-text").textContent =
    `${shown} of ${total} task${total !== 1 ? "s" : ""}` +
    (hidden ? `  ·  ${hidden} filtered` : "");

  const empty = document.getElementById("empty-state");
  const table = document.querySelector(".task-table");
  if (shown === 0) {
    empty.classList.remove("hidden");
    empty.querySelector(".empty-title").textContent = total === 0 ? "No tasks yet" : "No tasks match";
    empty.querySelector(".empty-sub").innerHTML = total === 0
      ? 'Click <strong>+ Add Task</strong> to create your first task'
      : "Try adjusting your search or filters";
    table.style.display = "none";
  } else {
    empty.classList.add("hidden");
    table.style.display = "";
  }
}

function updateStats(total) {
  const done   = allTasks.filter(t => t.status === "Done").length;
  const inprog = allTasks.filter(t => t.status === "In Progress").length;
  const todo   = allTasks.filter(t => (t.status || "Todo") === "Todo").length;
  const pct    = total > 0 ? Math.round((done / total) * 100) : 0;

  document.getElementById("stat-total").textContent  = total;
  document.getElementById("stat-done").textContent   = done;
  document.getElementById("stat-inprog").textContent = inprog;
  document.getElementById("stat-todo").textContent   = todo;
  document.getElementById("stat-pct").textContent    = `${pct}% complete`;
  document.getElementById("stat-progress-fill").style.width = `${pct}%`;
}

function selectRow(i) {
  selectedIdx = selectedIdx === i ? null : i;
  renderTable();
}

function clearFilters() {
  document.getElementById("search-input").value     = "";
  document.getElementById("filter-priority").value  = "All";
  document.getElementById("filter-status").value    = "All";
  renderTable();
}

// ── Add / Edit task modal ─────────────────────────────────────────────────────

function openAddModal() {
  editingIdx = null;
  document.getElementById("modal-header-icon").textContent = "✚";
  document.getElementById("modal-header-text").textContent = "Add New Task";
  document.getElementById("modal-save-btn").textContent    = "Save Task";
  document.getElementById("modal-title").value    = "";
  document.getElementById("modal-desc").value     = "";
  document.getElementById("modal-due").value      = "";
  document.getElementById("modal-priority").value = "Medium";
  document.getElementById("modal-status").value   = "Todo";
  document.getElementById("modal-error").textContent = "";
  document.getElementById("modal-overlay").classList.remove("hidden");
  setTimeout(() => document.getElementById("modal-title").focus(), 50);
}

function openEditModal(idx) {
  const t = allTasks[idx];
  editingIdx = idx;
  document.getElementById("modal-header-icon").textContent = "✏";
  document.getElementById("modal-header-text").textContent = "Edit Task";
  document.getElementById("modal-save-btn").textContent    = "Save Changes";
  document.getElementById("modal-title").value    = t.title       || "";
  document.getElementById("modal-desc").value     = t.description || "";
  document.getElementById("modal-due").value      = t.due_date    || "";
  document.getElementById("modal-priority").value = t.priority    || "Medium";
  document.getElementById("modal-status").value   = t.status      || "Todo";
  document.getElementById("modal-error").textContent = "";
  document.getElementById("modal-overlay").classList.remove("hidden");
  setTimeout(() => document.getElementById("modal-title").focus(), 50);
}

function closeModal(e) {
  if (e.target === document.getElementById("modal-overlay")) closeModalDirect();
}

function closeModalDirect() {
  document.getElementById("modal-overlay").classList.add("hidden");
}

async function saveModal() {
  const title = document.getElementById("modal-title").value.trim();
  const errEl = document.getElementById("modal-error");
  if (!title) { errEl.textContent = "Title cannot be blank."; return; }
  errEl.textContent = "";

  const body = {
    title,
    description: document.getElementById("modal-desc").value.trim(),
    due_date:    document.getElementById("modal-due").value.trim(),
    priority:    document.getElementById("modal-priority").value,
    status:      document.getElementById("modal-status").value,
  };

  try {
    if (editingIdx === null) {
      await api("POST", `/api/tasks/${encodeURIComponent(currentUser)}`, body);
      toast("Task added successfully!", "success");
    } else {
      await api("PUT", `/api/tasks/${encodeURIComponent(currentUser)}/${editingIdx}`, body);
      toast("Task updated!", "success");
    }
    closeModalDirect();
    selectedIdx = null;
    await loadTasks();
  } catch (e) {
    errEl.textContent = e.message;
  }
}

// ── Action buttons ────────────────────────────────────────────────────────────

function editSelected() {
  if (selectedIdx === null) { toast("Select a task first, then click Edit.", "warning"); return; }
  openEditModal(selectedIdx);
}

function completeSelected() {
  if (selectedIdx === null) { toast("Select a task to mark as complete.", "warning"); return; }
  const task = allTasks[selectedIdx];
  if (task.status === "Done") { toast(`"${task.title}" is already done.`, "info"); return; }
  pendingCompleteIdx = selectedIdx;
  document.getElementById("complete-task-name").textContent = `"${task.title}"`;
  document.getElementById("complete-overlay").classList.remove("hidden");
}

function closeCompleteConfirm(e) {
  if (e.target === document.getElementById("complete-overlay")) closeCompleteConfirmDirect();
}

function closeCompleteConfirmDirect() {
  document.getElementById("complete-overlay").classList.add("hidden");
  pendingCompleteIdx = null;
}

async function confirmCompleteYes() {
  if (pendingCompleteIdx === null) return;
  const idx = pendingCompleteIdx;
  closeCompleteConfirmDirect();
  try {
    await api("PATCH", `/api/tasks/${encodeURIComponent(currentUser)}/${idx}/complete`);
    toast("Task marked as complete!", "success");
    selectedIdx = null;
    await loadTasks();
  } catch (e) {
    toast(e.message, "error");
  }
}

function deleteSelected() {
  if (selectedIdx === null) { toast("Select a task first, then click Delete.", "warning"); return; }
  pendingDeleteIdx = selectedIdx;
  document.getElementById("confirm-task-name").textContent = `"${allTasks[selectedIdx].title}"`;
  document.getElementById("confirm-overlay").classList.remove("hidden");
}

function closeConfirm(e) {
  if (!e || e.target === document.getElementById("confirm-overlay")) closeConfirmDirect();
}

function closeConfirmDirect() {
  document.getElementById("confirm-overlay").classList.add("hidden");
  pendingDeleteIdx = null;
}

async function confirmDeleteYes() {
  if (pendingDeleteIdx === null) return;
  const idx = pendingDeleteIdx;
  closeConfirmDirect();
  try {
    await api("DELETE", `/api/tasks/${encodeURIComponent(currentUser)}/${idx}`);
    toast("Task deleted.", "info");
    selectedIdx = null;
    await loadTasks();
  } catch (e) {
    toast(e.message, "error");
  }
}

// ── Keyboard shortcuts ────────────────────────────────────────────────────────

document.addEventListener("keydown", e => {
  const active = name => !document.getElementById(name).classList.contains("hidden");

  if (e.key === "Escape") {
    if (active("register-overlay"))  { closeRegisterDirect();       return; }
    if (active("modal-overlay"))     { closeModalDirect();          return; }
    if (active("complete-overlay"))  { closeCompleteConfirmDirect();return; }
    if (active("confirm-overlay"))   { closeConfirmDirect();        return; }
  }

  if (e.key === "Enter" && e.target.tagName !== "TEXTAREA") {
    if (active("login-screen") && !active("register-overlay")) { doLogin();            return; }
    if (active("register-overlay"))  { doRegister();           return; }
    if (active("modal-overlay"))     { saveModal();            return; }
    if (active("complete-overlay"))  { confirmCompleteYes();   return; }
  }
});

// ── Live register field feedback (wired once on load) ────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("reg-pass").addEventListener("input", e => {
    setStrengthBar(e.target.value);
    setRules(e.target.value);
    updateMatchHint();
  });
  document.getElementById("reg-confirm").addEventListener("input", updateMatchHint);
});

// ── Utility ───────────────────────────────────────────────────────────────────

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Boot ──────────────────────────────────────────────────────────────────────

showLogin();
