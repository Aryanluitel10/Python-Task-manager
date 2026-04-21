#!/usr/bin/env python3
"""
gui.py — Tkinter GUI frontend for the Task Manager.
Reuses load_data() and save_data() from main.py.
Run with: python3 gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import main as backend

# ── Palette ────────────────────────────────────────────────────────────────────
BG        = "#f0f2f5"
CARD      = "#ffffff"
HEADER_BG = "#2c3e50"
HEADER_FG = "#ecf0f1"
ACCENT    = "#3498db"
ACCENT_D  = "#2980b9"
SUCCESS   = "#27ae60"
DANGER    = "#e74c3c"
WARNING   = "#e67e22"
MUTED     = "#7f8c8d"
BORDER    = "#dfe6e9"
TEXT      = "#2c3e50"

PRIORITY_FG = {"High": DANGER,  "Medium": WARNING, "Low": SUCCESS}
STATUS_FG   = {"Todo": MUTED,   "In Progress": ACCENT, "Done": SUCCESS}


def _btn(parent, text, command, bg=ACCENT, width=None, **kw):
    """Flat, colored tk.Button that works consistently across platforms."""
    opts = dict(
        text=text, command=command,
        bg=bg, fg="white", relief="flat", cursor="hand2",
        padx=14, pady=6, font=("Helvetica", 10),
        activebackground=bg, activeforeground="white",
    )
    if width:
        opts["width"] = width
    opts.update(kw)
    return tk.Button(parent, **opts)


def _label(parent, text, font=("Helvetica", 10), fg=TEXT, **kw):
    return tk.Label(parent, text=text, font=font, bg=CARD, fg=fg, **kw)


# ── Login Screen ───────────────────────────────────────────────────────────────
class LoginFrame(tk.Frame):
    """Full-screen login / create-account panel."""

    def __init__(self, parent, data, on_login):
        super().__init__(parent, bg=BG)
        self.data = data
        self.on_login = on_login
        self._build()

    def _build(self):
        card = tk.Frame(self, bg=CARD, padx=52, pady=44,
                        highlightbackground=BORDER, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Task Manager", font=("Helvetica", 26, "bold"),
                 bg=CARD, fg=HEADER_BG).pack(pady=(0, 4))
        tk.Label(card, text="Sign in or create a new account",
                 font=("Helvetica", 10), bg=CARD, fg=MUTED).pack(pady=(0, 28))

        # Username
        tk.Label(card, text="Username", font=("Helvetica", 10, "bold"),
                 bg=CARD, fg=TEXT, anchor="w").pack(fill="x")
        self._user_var = tk.StringVar()
        user_entry = ttk.Entry(card, textvariable=self._user_var,
                               width=32, font=("Helvetica", 11))
        user_entry.pack(pady=(4, 14), ipady=5)
        user_entry.focus()

        # Password
        tk.Label(card, text="Password", font=("Helvetica", 10, "bold"),
                 bg=CARD, fg=TEXT, anchor="w").pack(fill="x")
        self._pass_var = tk.StringVar()
        pw_entry = ttk.Entry(card, textvariable=self._pass_var, show="*",
                             width=32, font=("Helvetica", 11))
        pw_entry.pack(pady=(4, 6), ipady=5)

        # Tab / Enter navigation
        user_entry.bind("<Return>", lambda _: pw_entry.focus())
        pw_entry.bind("<Return>", lambda _: self._login())

        # Inline error
        self._error_var = tk.StringVar()
        tk.Label(card, textvariable=self._error_var, fg=DANGER,
                 bg=CARD, font=("Helvetica", 9)).pack(pady=(2, 0))

        # Buttons
        bf = tk.Frame(card, bg=CARD)
        bf.pack(pady=(18, 0))
        _btn(bf, "Login",          self._login,  bg=ACCENT).pack(side="left", padx=5)
        _btn(bf, "Create Account", self._create, bg=SUCCESS).pack(side="left", padx=5)

    # ── handlers ──────────────────────────────────────────────────────────────
    def _set_error(self, msg):
        self._error_var.set(msg)

    def _login(self):
        u = self._user_var.get().strip()
        p = self._pass_var.get().strip()
        if not u or not p:
            self._set_error("Please enter username and password.")
            return
        user = self.data["users"].get(u)
        if not user:
            self._set_error("Username not found.")
            return
        if user["password"] != p:
            self._set_error("Incorrect password.")
            return
        self.on_login(u)

    def _create(self):
        u = self._user_var.get().strip()
        p = self._pass_var.get().strip()
        if not u:
            self._set_error("Username cannot be blank.")
            return
        if not p:
            self._set_error("Password cannot be blank.")
            return
        if u in self.data["users"]:
            self._set_error("Username already exists. Try another.")
            return
        self.data["users"][u] = {"password": p, "tasks": []}
        backend.save_data(self.data)
        self.on_login(u)


# ── Task Dialog (Add / Edit) ───────────────────────────────────────────────────
class TaskDialog(tk.Toplevel):
    """Modal dialog for creating or editing a task."""

    def __init__(self, parent, title, task=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=CARD)
        self.grab_set()
        self.result = None

        self._build(task or {})
        self._center(parent)
        self.wait_window()

    def _center(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h   = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _field_label(self, text, row):
        tk.Label(self, text=text, font=("Helvetica", 10, "bold"),
                 bg=CARD, fg=TEXT, anchor="w").grid(
            row=row, column=0, columnspan=2, sticky="w", padx=24, pady=(10, 2))

    def _build(self, task):
        PAD = {"padx": 24, "pady": 4}

        # Title
        self._field_label("Title  *", 0)
        self._title_var = tk.StringVar(value=task.get("title", ""))
        title_e = ttk.Entry(self, textvariable=self._title_var,
                            width=44, font=("Helvetica", 11))
        title_e.grid(row=1, column=0, columnspan=2, **PAD, ipady=4)
        title_e.focus()

        # Description
        self._field_label("Description", 2)
        self._desc = tk.Text(self, width=44, height=4, font=("Helvetica", 11),
                             relief="solid", bd=1, wrap="word",
                             padx=6, pady=4)
        self._desc.grid(row=3, column=0, columnspan=2, **PAD)
        self._desc.insert("1.0", task.get("description", ""))

        # Due date
        self._field_label("Due Date  (YYYY-MM-DD, optional)", 4)
        self._due_var = tk.StringVar(value=task.get("due_date", ""))
        ttk.Entry(self, textvariable=self._due_var,
                  width=20, font=("Helvetica", 11)).grid(
            row=5, column=0, sticky="w", **PAD, ipady=4)

        # Priority + Status side by side
        tk.Label(self, text="Priority", font=("Helvetica", 10, "bold"),
                 bg=CARD, fg=TEXT).grid(row=6, column=0, sticky="w", padx=24, pady=(10, 2))
        tk.Label(self, text="Status", font=("Helvetica", 10, "bold"),
                 bg=CARD, fg=TEXT).grid(row=6, column=1, sticky="w", padx=24, pady=(10, 2))

        self._priority_var = tk.StringVar(value=task.get("priority", "Medium"))
        ttk.Combobox(self, textvariable=self._priority_var,
                     values=["Low", "Medium", "High"],
                     state="readonly", width=18).grid(row=7, column=0, sticky="w", **PAD)

        self._status_var = tk.StringVar(value=task.get("status", "Todo"))
        ttk.Combobox(self, textvariable=self._status_var,
                     values=["Todo", "In Progress", "Done"],
                     state="readonly", width=18).grid(row=7, column=1, sticky="w", **PAD)

        # Error
        self._error_var = tk.StringVar()
        tk.Label(self, textvariable=self._error_var, fg=DANGER,
                 bg=CARD, font=("Helvetica", 9)).grid(
            row=8, column=0, columnspan=2, pady=(4, 0))

        # Buttons
        bf = tk.Frame(self, bg=CARD)
        bf.grid(row=9, column=0, columnspan=2, pady=(10, 20))
        _btn(bf, "Save",   self._save,    bg=SUCCESS).pack(side="left", padx=6)
        _btn(bf, "Cancel", self.destroy,  bg=MUTED).pack(side="left", padx=6)

    def _save(self):
        title = self._title_var.get().strip()
        if not title:
            self._error_var.set("Title cannot be blank.")
            return
        due = self._due_var.get().strip()
        if due:
            parts = due.split("-")
            if not (len(parts) == 3 and all(p.isdigit() for p in parts)
                    and len(parts[0]) == 4):
                self._error_var.set("Due date must be YYYY-MM-DD.")
                return
        self.result = {
            "title":       title,
            "description": self._desc.get("1.0", "end-1c").strip(),
            "due_date":    due,
            "priority":    self._priority_var.get(),
            "status":      self._status_var.get(),
        }
        self.destroy()


# ── Main Task App ──────────────────────────────────────────────────────────────
class TaskApp(tk.Frame):
    """Post-login task management screen."""

    def __init__(self, parent, data, username, on_logout):
        super().__init__(parent, bg=BG)
        self.data      = data
        self.username  = username
        self.on_logout = on_logout
        self._build()
        self._refresh()

    def _tasks(self):
        return self.data["users"][self.username]["tasks"]

    # ── Build UI ───────────────────────────────────────────────────────────────
    def _build(self):
        self._build_header()
        self._build_toolbar()
        self._build_tree()
        self._build_actions()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=HEADER_BG, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="  Task Manager", font=("Helvetica", 16, "bold"),
                 bg=HEADER_BG, fg=HEADER_FG).pack(side="left")
        _btn(hdr, "Logout", self._logout, bg=DANGER).pack(side="right", padx=14)
        tk.Label(hdr, text=f"User: {self.username}",
                 font=("Helvetica", 10), bg=HEADER_BG, fg=HEADER_FG).pack(side="right", padx=4)

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=CARD, pady=9, padx=14,
                       highlightbackground=BORDER, highlightthickness=1)
        bar.pack(fill="x")

        tk.Label(bar, text="Search:", font=("Helvetica", 10),
                 bg=CARD, fg=TEXT).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh())
        ttk.Entry(bar, textvariable=self._search_var,
                  width=22, font=("Helvetica", 10)).pack(side="left", padx=(4, 18), ipady=3)

        tk.Label(bar, text="Priority:", font=("Helvetica", 10),
                 bg=CARD, fg=TEXT).pack(side="left")
        self._pri_filter = tk.StringVar(value="All")
        cb_p = ttk.Combobox(bar, textvariable=self._pri_filter,
                             values=["All", "High", "Medium", "Low"],
                             state="readonly", width=10)
        cb_p.pack(side="left", padx=(4, 18))
        cb_p.bind("<<ComboboxSelected>>", lambda _: self._refresh())

        tk.Label(bar, text="Status:", font=("Helvetica", 10),
                 bg=CARD, fg=TEXT).pack(side="left")
        self._sta_filter = tk.StringVar(value="All")
        cb_s = ttk.Combobox(bar, textvariable=self._sta_filter,
                             values=["All", "Todo", "In Progress", "Done"],
                             state="readonly", width=12)
        cb_s.pack(side="left", padx=(4, 18))
        cb_s.bind("<<ComboboxSelected>>", lambda _: self._refresh())

        _btn(bar, "Clear Filters", self._clear_filters, bg=MUTED).pack(side="left")

    def _build_tree(self):

        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=14, pady=10)

        cols = ("title", "priority", "status", "due_date", "description")
        self._tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  selectmode="browse")

        self._tree.heading("title",       text="Title")
        self._tree.heading("priority",    text="Priority")
        self._tree.heading("status",      text="Status")
        self._tree.heading("due_date",    text="Due Date")
        self._tree.heading("description", text="Description")

        self._tree.column("title",       width=230, anchor="w", stretch=True)
        self._tree.column("priority",    width=80,  anchor="center", stretch=False)
        self._tree.column("status",      width=110, anchor="center", stretch=False)
        self._tree.column("due_date",    width=100, anchor="center", stretch=False)
        self._tree.column("description", width=300, anchor="w",      stretch=True)

        # Tags for color-coded rows
        self._tree.tag_configure("High",        foreground=DANGER)
        self._tree.tag_configure("Medium",      foreground=WARNING)
        self._tree.tag_configure("Low",         foreground=SUCCESS)
        self._tree.tag_configure("Done_row",    foreground=MUTED)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Double-click opens edit dialog
        self._tree.bind("<Double-1>", lambda _: self._edit_task())

    def _build_actions(self):
        bar = tk.Frame(self, bg=CARD, pady=9, padx=14,
                       highlightbackground=BORDER, highlightthickness=1)
        bar.pack(fill="x", side="bottom")
        _btn(bar, "+ Add Task",      self._add_task,      bg=ACCENT).pack(side="left", padx=4)
        _btn(bar, "Edit",            self._edit_task,     bg=WARNING).pack(side="left", padx=4)
        _btn(bar, "Mark Complete",   self._mark_complete, bg=SUCCESS).pack(side="left", padx=4)
        _btn(bar, "Delete",          self._delete_task,   bg=DANGER).pack(side="left", padx=4)

    def _build_statusbar(self):
        self._status_var = tk.StringVar()
        tk.Label(self, textvariable=self._status_var,
                 bg=BG, fg=MUTED, font=("Helvetica", 9), anchor="w").pack(
            fill="x", padx=14, pady=(0, 6), side="bottom")

    # ── Refresh treeview ───────────────────────────────────────────────────────
    def _refresh(self):
        self._tree.delete(*self._tree.get_children())

        query   = self._search_var.get().strip().lower()
        pri_flt = self._pri_filter.get()
        sta_flt = self._sta_filter.get()
        tasks   = self._tasks()
        shown   = 0

        for i, t in enumerate(tasks):
            if pri_flt != "All" and t.get("priority", "Medium") != pri_flt:
                continue
            if sta_flt != "All" and t.get("status", "Todo") != sta_flt:
                continue
            if query and not (
                query in t["title"].lower()
                or query in t.get("description", "").lower()
                or query in t.get("due_date", "").lower()
            ):
                continue

            priority = t.get("priority", "Medium")
            status   = t.get("status", "Todo")
            tag      = "Done_row" if status == "Done" else priority

            self._tree.insert("", "end", iid=str(i), tags=(tag,), values=(
                t["title"],
                priority,
                status,
                t.get("due_date") or "—",
                t.get("description", ""),
            ))
            shown += 1

        total = len(tasks)
        hidden = total - shown
        self._status_var.set(
            f"{shown} of {total} task{'s' if total != 1 else ''} shown"
            + (f"  ·  {hidden} hidden by filter" if hidden else "")
        )

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _selected_index(self):
        """Return the original task-list index of the selected row, or None."""
        sel = self._tree.focus()
        return int(sel) if sel else None

    def _clear_filters(self):
        self._search_var.set("")
        self._pri_filter.set("All")
        self._sta_filter.set("All")
        self._refresh()

    def _logout(self):
        self.on_logout()

    # ── CRUD ───────────────────────────────────────────────────────────────────
    def _add_task(self):
        dlg = TaskDialog(self.winfo_toplevel(), "Add Task")
        if dlg.result:
            self._tasks().append(dlg.result)
            backend.save_data(self.data)
            self._refresh()
            # Only select the new row if it is visible under the current filters
            new_iid = str(len(self._tasks()) - 1)
            if self._tree.exists(new_iid):
                self._tree.focus(new_iid)
                self._tree.selection_set(new_iid)

    def _edit_task(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Edit Task", "Please select a task to edit.")
            return
        dlg = TaskDialog(self.winfo_toplevel(), "Edit Task",
                         task=self._tasks()[idx])
        if dlg.result:
            self._tasks()[idx] = dlg.result
            backend.save_data(self.data)
            self._refresh()
            # Re-select same row if still visible
            if self._tree.exists(str(idx)):
                self._tree.focus(str(idx))
                self._tree.selection_set(str(idx))

    def _delete_task(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Delete Task", "Please select a task to delete.")
            return
        task = self._tasks()[idx]
        if messagebox.askyesno("Delete Task",
                               f"Delete \"{task['title']}\"?\nThis cannot be undone.",
                               icon="warning"):
            self._tasks().pop(idx)
            backend.save_data(self.data)
            self._refresh()

    def _mark_complete(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Mark Complete", "Please select a task first.")
            return
        task = self._tasks()[idx]
        if task.get("status") == "Done":
            messagebox.showinfo("Mark Complete",
                                f"\"{task['title']}\" is already marked as Done.")
            return
        task["status"] = "Done"
        backend.save_data(self.data)
        self._refresh()


# ── Entry point ────────────────────────────────────────────────────────────────
def _apply_styles():
    """Configure ttk styles once at startup, before any widgets are created."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    rowheight=30,
                    font=("Helvetica", 10),
                    background=CARD,
                    fieldbackground=CARD,
                    borderwidth=0)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 10, "bold"),
                    background=HEADER_BG,
                    foreground=HEADER_FG,
                    relief="flat")
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])


def main():
    root = tk.Tk()
    root.title("Task Manager")
    root.geometry("980x640")
    root.minsize(720, 500)
    root.configure(bg=BG)
    _apply_styles()

    data = backend.load_data()
    current = [None]

    def show_login():
        if current[0]:
            current[0].destroy()
        frame = LoginFrame(root, data, on_login=show_app)
        frame.pack(fill="both", expand=True)
        current[0] = frame

    def show_app(username):
        if current[0]:
            current[0].destroy()
        frame = TaskApp(root, data, username, on_logout=show_login)
        frame.pack(fill="both", expand=True)
        current[0] = frame

    show_login()
    root.mainloop()


if __name__ == "__main__":
    main()
