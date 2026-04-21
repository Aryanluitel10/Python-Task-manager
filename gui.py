#!/usr/bin/env python3
"""
gui.py  —  Tkinter GUI for the Task Manager.
Reuses load_data() and save_data() from main.py.
Run:  python3 gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import main as backend

# ── Colour palette ─────────────────────────────────────────────────────────────
BG       = "#f0f4f8"
CARD     = "#ffffff"
DARK     = "#1e293b"      # header / sidebar
HDR_FG   = "#f1f5f9"
ACCENT   = "#6366f1"      # indigo
ACCENT_D = "#4f46e5"
SUCCESS  = "#22c55e"      # green
DANGER   = "#f43f5e"      # rose
WARNING  = "#fb923c"      # orange
MUTED    = "#94a3b8"
BORDER   = "#e2e8f0"
TEXT     = "#0f172a"
TEXT2    = "#64748b"
ROW_A    = "#ffffff"
ROW_B    = "#f8fafc"      # alternate stripe

P_FG   = {"High": "#dc2626", "Medium": "#d97706", "Low": "#16a34a"}
S_FG   = {"Todo": "#64748b", "In Progress": "#2563eb", "Done": "#16a34a"}
P_ICON = {"High": "▲ ", "Medium": "◆ ", "Low": "▼ "}
S_ICON = {"Todo": "○ ", "In Progress": "▶ ", "Done": "✓ "}


# ── Helpers ────────────────────────────────────────────────────────────────────
def _darken(color, factor=0.82):
    """Return a slightly darker shade of a hex colour."""
    c = color.lstrip("#")
    r = max(0, int(int(c[0:2], 16) * factor))
    g = max(0, int(int(c[2:4], 16) * factor))
    b = max(0, int(int(c[4:6], 16) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _btn(parent, text, command, bg=ACCENT, fg="white",
         padx=16, pady=7, font_size=10, **kw):
    """Flat coloured button with automatic hover-darken effect."""
    dark = _darken(bg)
    b = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, relief="flat", cursor="hand2",
        padx=padx, pady=pady,
        font=("Helvetica", font_size, "bold"),
        activebackground=dark, activeforeground=fg,
        **kw
    )
    b.bind("<Enter>", lambda _: b.config(bg=dark))
    b.bind("<Leave>", lambda _: b.config(bg=bg))
    return b


# ── Login Screen ───────────────────────────────────────────────────────────────
class LoginFrame(tk.Frame):
    """Split-panel login / sign-up screen."""

    def __init__(self, parent, data, on_login):
        super().__init__(parent, bg=DARK)
        self.data = data
        self.on_login = on_login
        self._build()

    def _build(self):
        # ── Left dark branding panel ───────────────────────────────────────────
        left = tk.Frame(self, bg=DARK, width=340, padx=44)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Frame(left, bg=DARK).pack(expand=True)   # top spacer

        tk.Label(left, text="✔", font=("Helvetica", 52),
                 bg=DARK, fg=ACCENT).pack()
        tk.Label(left, text="Task Manager",
                 font=("Helvetica", 22, "bold"), bg=DARK, fg=HDR_FG).pack(pady=(8, 6))
        tk.Label(left, text="Stay organised.\nGet things done.",
                 font=("Helvetica", 11), bg=DARK, fg=MUTED,
                 justify="center").pack(pady=(0, 28))

        for feat in ["Multi-user accounts", "Priority & due dates",
                     "Search & filter tasks", "Auto-saves everything"]:
            row = tk.Frame(left, bg=DARK)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="›", font=("Helvetica", 13, "bold"),
                     bg=DARK, fg=ACCENT).pack(side="left")
            tk.Label(row, text=f"  {feat}", font=("Helvetica", 11),
                     bg=DARK, fg=MUTED).pack(side="left")

        tk.Frame(left, bg=DARK).pack(expand=True)   # bottom spacer

        # ── Right white form panel ─────────────────────────────────────────────
        right = tk.Frame(self, bg=CARD)
        right.pack(side="right", fill="both", expand=True)

        form = tk.Frame(right, bg=CARD, padx=56)
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form, text="Welcome back",
                 font=("Helvetica", 22, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
        tk.Label(form, text="Sign in or create a new account below",
                 font=("Helvetica", 10), bg=CARD, fg=TEXT2).pack(anchor="w", pady=(4, 30))

        # Username
        tk.Label(form, text="USERNAME", font=("Helvetica", 9, "bold"),
                 bg=CARD, fg=TEXT2, anchor="w").pack(fill="x")
        self._user_var = tk.StringVar()
        user_e = ttk.Entry(form, textvariable=self._user_var,
                           width=34, font=("Helvetica", 11))
        user_e.pack(pady=(4, 16), ipady=6)
        user_e.focus()

        # Password
        tk.Label(form, text="PASSWORD", font=("Helvetica", 9, "bold"),
                 bg=CARD, fg=TEXT2, anchor="w").pack(fill="x")
        self._pass_var = tk.StringVar()
        pw_e = ttk.Entry(form, textvariable=self._pass_var, show="*",
                         width=34, font=("Helvetica", 11))
        pw_e.pack(pady=(4, 8), ipady=6)

        user_e.bind("<Return>", lambda _: pw_e.focus())
        pw_e.bind("<Return>", lambda _: self._login())

        # Inline error message
        self._err_var = tk.StringVar()
        tk.Label(form, textvariable=self._err_var, fg=DANGER,
                 bg=CARD, font=("Helvetica", 9)).pack(pady=(0, 6))

        # Buttons
        bf = tk.Frame(form, bg=CARD)
        bf.pack(fill="x", pady=(6, 0))
        _btn(bf, "Sign In",       self._login,  bg=ACCENT, pady=9).pack(side="left", padx=(0, 8))
        _btn(bf, "Create Account",self._create, bg=SUCCESS, pady=9).pack(side="left")

    # ── handlers ──────────────────────────────────────────────────────────────
    def _login(self):
        u = self._user_var.get().strip()
        p = self._pass_var.get().strip()
        if not u or not p:
            self._err_var.set("Please enter your username and password.")
            return
        user = self.data["users"].get(u)
        if not user:
            self._err_var.set("No account found with that username.")
            return
        if user["password"] != p:
            self._err_var.set("Incorrect password. Please try again.")
            return
        self.on_login(u)

    def _create(self):
        u = self._user_var.get().strip()
        p = self._pass_var.get().strip()
        if not u:
            self._err_var.set("Username cannot be blank.")
            return
        if not p:
            self._err_var.set("Password cannot be blank.")
            return
        if u in self.data["users"]:
            self._err_var.set("That username is already taken.")
            return
        self.data["users"][u] = {"password": p, "tasks": []}
        backend.save_data(self.data)
        self.on_login(u)


# ── Task Dialog (Add / Edit) ───────────────────────────────────────────────────
class TaskDialog(tk.Toplevel):
    """Modal dialog for creating or editing a task."""

    def __init__(self, parent, dialog_title, task=None):
        super().__init__(parent)
        self.title(dialog_title)
        self.resizable(False, False)
        self.configure(bg=CARD)
        self.grab_set()
        self.result = None
        self._build(dialog_title, task or {})
        self._center(parent)
        self.wait_window()

    def _center(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h   = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    def _build(self, dialog_title, task):
        # Coloured top banner
        banner = tk.Frame(self, bg=ACCENT, pady=14)
        banner.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(banner, text=dialog_title, font=("Helvetica", 13, "bold"),
                 bg=ACCENT, fg="white").pack()

        PAD = {"padx": 24, "pady": 5}

        def lbl(text, row, col=0, span=2):
            tk.Label(self, text=text, font=("Helvetica", 9, "bold"),
                     bg=CARD, fg=TEXT2, anchor="w").grid(
                row=row, column=col, columnspan=span,
                sticky="w", padx=24, pady=(12, 2))

        # Title
        lbl("TITLE  *", 1)
        self._title_var = tk.StringVar(value=task.get("title", ""))
        title_e = ttk.Entry(self, textvariable=self._title_var,
                            width=46, font=("Helvetica", 11))
        title_e.grid(row=2, column=0, columnspan=2, **PAD, ipady=5)
        title_e.focus()

        # Description
        lbl("DESCRIPTION", 3)
        self._desc = tk.Text(self, width=46, height=4, font=("Helvetica", 11),
                             relief="solid", bd=1, wrap="word",
                             padx=8, pady=6, bg="#fafafa")
        self._desc.grid(row=4, column=0, columnspan=2, **PAD)
        self._desc.insert("1.0", task.get("description", ""))

        # Due date
        lbl("DUE DATE  (YYYY-MM-DD, optional)", 5)
        self._due_var = tk.StringVar(value=task.get("due_date", ""))
        ttk.Entry(self, textvariable=self._due_var, width=22,
                  font=("Helvetica", 11)).grid(
            row=6, column=0, columnspan=2, sticky="w", **PAD, ipady=5)

        # Priority & Status side by side
        lbl("PRIORITY", 7, col=0, span=1)
        lbl("STATUS",   7, col=1, span=1)

        self._pri_var = tk.StringVar(value=task.get("priority", "Medium"))
        ttk.Combobox(self, textvariable=self._pri_var,
                     values=["Low", "Medium", "High"],
                     state="readonly", width=20).grid(row=8, column=0, sticky="w", **PAD)

        self._sta_var = tk.StringVar(value=task.get("status", "Todo"))
        ttk.Combobox(self, textvariable=self._sta_var,
                     values=["Todo", "In Progress", "Done"],
                     state="readonly", width=20).grid(row=8, column=1, sticky="w", **PAD)

        # Error label
        self._err_var = tk.StringVar()
        tk.Label(self, textvariable=self._err_var, fg=DANGER,
                 bg=CARD, font=("Helvetica", 9)).grid(
            row=9, column=0, columnspan=2, pady=(6, 0))

        # Buttons
        bf = tk.Frame(self, bg=CARD)
        bf.grid(row=10, column=0, columnspan=2, pady=(8, 20))
        _btn(bf, "Save Task", self._save,    bg=SUCCESS, pady=8).pack(side="left", padx=6)
        _btn(bf, "Cancel",    self.destroy,  bg=MUTED,   pady=8).pack(side="left", padx=6)

    def _save(self):
        title = self._title_var.get().strip()
        if not title:
            self._err_var.set("Title cannot be blank.")
            return
        due = self._due_var.get().strip()
        if due:
            parts = due.split("-")
            if not (len(parts) == 3 and all(p.isdigit() for p in parts)
                    and len(parts[0]) == 4):
                self._err_var.set("Due date must be in YYYY-MM-DD format.")
                return
        self.result = {
            "title":       title,
            "description": self._desc.get("1.0", "end-1c").strip(),
            "due_date":    due,
            "priority":    self._pri_var.get(),
            "status":      self._sta_var.get(),
        }
        self.destroy()


# ── Main Task App ──────────────────────────────────────────────────────────────
class TaskApp(tk.Frame):
    """Post-login main task management screen."""

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
        self._build_stats()
        self._build_toolbar()
        self._build_tree()
        self._build_actions()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=DARK, pady=11)
        hdr.pack(fill="x")

        tk.Label(hdr, text="  ✔  Task Manager",
                 font=("Helvetica", 15, "bold"), bg=DARK, fg=HDR_FG).pack(side="left")

        # Logout button (far right)
        _btn(hdr, "Logout", self._logout, bg=DANGER, pady=5).pack(side="right", padx=14)

        # User avatar circle + name
        av_frame = tk.Frame(hdr, bg=DARK)
        av_frame.pack(side="right", padx=8)
        av = tk.Canvas(av_frame, width=30, height=30, bg=DARK, highlightthickness=0)
        av.create_oval(1, 1, 29, 29, fill=ACCENT, outline="")
        av.create_text(15, 15, text=self.username[0].upper(),
                       fill="white", font=("Helvetica", 12, "bold"))
        av.pack(side="left")
        tk.Label(av_frame, text=f"  {self.username}",
                 font=("Helvetica", 10), bg=DARK, fg=HDR_FG).pack(side="left")

    def _build_stats(self):
        """Live summary bar: Total · Done · In Progress · Todo."""
        bar = tk.Frame(self, bg=CARD,
                       highlightbackground=BORDER, highlightthickness=1)
        bar.pack(fill="x")

        self._stat_vars = {}
        entries = [
            ("Total",       TEXT,    "Total"),
            ("Done",        SUCCESS, "Done"),
            ("In Progress", ACCENT,  "In Progress"),
            ("Todo",        WARNING, "Todo"),
        ]
        for key, color, label in entries:
            cell = tk.Frame(bar, bg=CARD, padx=24, pady=10)
            cell.pack(side="left")
            var = tk.StringVar(value="0")
            self._stat_vars[key] = var
            tk.Label(cell, textvariable=var,
                     font=("Helvetica", 22, "bold"), bg=CARD, fg=color).pack()
            tk.Label(cell, text=label, font=("Helvetica", 8),
                     bg=CARD, fg=MUTED).pack()
            tk.Frame(bar, bg=BORDER, width=1).pack(side="left", fill="y", pady=8)

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG, pady=10, padx=14)
        bar.pack(fill="x")

        tk.Label(bar, text="Search:", font=("Helvetica", 10),
                 bg=BG, fg=TEXT2).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh())
        ttk.Entry(bar, textvariable=self._search_var,
                  width=24, font=("Helvetica", 10)).pack(
            side="left", padx=(4, 20), ipady=4)

        tk.Label(bar, text="Priority:", font=("Helvetica", 10),
                 bg=BG, fg=TEXT2).pack(side="left")
        self._pri_filter = tk.StringVar(value="All")
        cb_p = ttk.Combobox(bar, textvariable=self._pri_filter,
                             values=["All", "High", "Medium", "Low"],
                             state="readonly", width=10)
        cb_p.pack(side="left", padx=(4, 20))
        cb_p.bind("<<ComboboxSelected>>", lambda _: self._refresh())

        tk.Label(bar, text="Status:", font=("Helvetica", 10),
                 bg=BG, fg=TEXT2).pack(side="left")
        self._sta_filter = tk.StringVar(value="All")
        cb_s = ttk.Combobox(bar, textvariable=self._sta_filter,
                             values=["All", "Todo", "In Progress", "Done"],
                             state="readonly", width=12)
        cb_s.pack(side="left", padx=(4, 20))
        cb_s.bind("<<ComboboxSelected>>", lambda _: self._refresh())

        _btn(bar, "Clear", self._clear_filters,
             bg=CARD, fg=TEXT2, pady=5, padx=12, font_size=9).pack(side="left")

    def _build_tree(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=14, pady=(0, 4))

        cols = ("title", "priority", "status", "due_date", "description")
        self._tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  selectmode="browse")

        self._tree.heading("title",       text="Title")
        self._tree.heading("priority",    text="Priority")
        self._tree.heading("status",      text="Status")
        self._tree.heading("due_date",    text="Due Date")
        self._tree.heading("description", text="Description")

        self._tree.column("title",       width=220, anchor="w",      stretch=True)
        self._tree.column("priority",    width=95,  anchor="center", stretch=False)
        self._tree.column("status",      width=120, anchor="center", stretch=False)
        self._tree.column("due_date",    width=100, anchor="center", stretch=False)
        self._tree.column("description", width=280, anchor="w",      stretch=True)

        # Alternating row stripes
        self._tree.tag_configure("even", background=ROW_A)
        self._tree.tag_configure("odd",  background=ROW_B)
        # Priority foreground tags (combine with stripe)
        for pri, fg in P_FG.items():
            self._tree.tag_configure(f"p_{pri}", foreground=fg)
        # Done row: greyed out
        self._tree.tag_configure("done_row", foreground=MUTED)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._tree.bind("<Double-1>", lambda _: self._edit_task())

    def _build_actions(self):
        bar = tk.Frame(self, bg=CARD, pady=10, padx=14,
                       highlightbackground=BORDER, highlightthickness=1)
        bar.pack(fill="x", side="bottom")

        _btn(bar, "+ Add Task",   self._add_task,      bg=ACCENT).pack(side="left", padx=4)
        _btn(bar, "✏  Edit",      self._edit_task,     bg=WARNING).pack(side="left", padx=4)
        _btn(bar, "✔  Complete",  self._mark_complete, bg=SUCCESS).pack(side="left", padx=4)
        _btn(bar, "✖  Delete",    self._delete_task,   bg=DANGER).pack(side="left",  padx=4)

        tk.Label(bar, text="Double-click a row to edit",
                 font=("Helvetica", 9), bg=CARD, fg=MUTED).pack(side="right", padx=8)

    def _build_statusbar(self):
        self._status_var = tk.StringVar()
        tk.Label(self, textvariable=self._status_var,
                 bg=BG, fg=MUTED, font=("Helvetica", 9), anchor="w").pack(
            fill="x", padx=16, pady=(2, 6), side="bottom")

    # ── Refresh treeview + stats ────────────────────────────────────────────────
    def _refresh(self):
        self._tree.delete(*self._tree.get_children())

        query   = self._search_var.get().strip().lower()
        pri_flt = self._pri_filter.get()
        sta_flt = self._sta_filter.get()
        tasks   = self._tasks()
        shown   = 0

        for i, t in enumerate(tasks):
            pri = t.get("priority", "Medium")
            sta = t.get("status", "Todo")

            if pri_flt != "All" and pri != pri_flt:
                continue
            if sta_flt != "All" and sta != sta_flt:
                continue
            if query and not (
                query in t["title"].lower()
                or query in t.get("description", "").lower()
                or query in t.get("due_date", "").lower()
            ):
                continue

            stripe = "even" if shown % 2 == 0 else "odd"
            tags   = (stripe, "done_row") if sta == "Done" else (stripe, f"p_{pri}")

            self._tree.insert("", "end", iid=str(i), tags=tags, values=(
                t["title"],
                P_ICON.get(pri, "") + pri,
                S_ICON.get(sta, "") + sta,
                t.get("due_date") or "—",
                t.get("description", ""),
            ))
            shown += 1

        # Update the stats bar (always reflects all tasks, not just filtered)
        total  = len(tasks)
        done   = sum(1 for t in tasks if t.get("status") == "Done")
        inprog = sum(1 for t in tasks if t.get("status") == "In Progress")
        todo   = sum(1 for t in tasks if t.get("status", "Todo") == "Todo")
        self._stat_vars["Total"].set(str(total))
        self._stat_vars["Done"].set(str(done))
        self._stat_vars["In Progress"].set(str(inprog))
        self._stat_vars["Todo"].set(str(todo))

        hidden = total - shown
        self._status_var.set(
            f"Showing {shown} of {total} task{'s' if total != 1 else ''}"
            + (f"  ·  {hidden} hidden by filter" if hidden else "")
        )

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _selected_index(self):
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
        dlg = TaskDialog(self.winfo_toplevel(), "Add New Task")
        if dlg.result:
            self._tasks().append(dlg.result)
            backend.save_data(self.data)
            self._refresh()
            new_iid = str(len(self._tasks()) - 1)
            if self._tree.exists(new_iid):
                self._tree.focus(new_iid)
                self._tree.selection_set(new_iid)

    def _edit_task(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Edit Task", "Select a task first, then click Edit.")
            return
        dlg = TaskDialog(self.winfo_toplevel(), "Edit Task", task=self._tasks()[idx])
        if dlg.result:
            self._tasks()[idx] = dlg.result
            backend.save_data(self.data)
            self._refresh()
            if self._tree.exists(str(idx)):
                self._tree.focus(str(idx))
                self._tree.selection_set(str(idx))

    def _delete_task(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Delete Task", "Select a task first, then click Delete.")
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
            messagebox.showinfo("Mark Complete", "Select a task first.")
            return
        task = self._tasks()[idx]
        if task.get("status") == "Done":
            messagebox.showinfo("Already Done",
                                f"\"{task['title']}\" is already marked as Done.")
            return
        task["status"] = "Done"
        backend.save_data(self.data)
        self._refresh()


# ── Styles & Entry point ───────────────────────────────────────────────────────
def _apply_styles():
    """Configure ttk styles once at startup before any widgets are created."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    rowheight=32,
                    font=("Helvetica", 10),
                    background=ROW_A,
                    fieldbackground=ROW_A,
                    borderwidth=0)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 10, "bold"),
                    background=DARK,
                    foreground=HDR_FG,
                    relief="flat",
                    padding=8)
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])
    style.configure("TEntry",
                    fieldbackground=CARD,
                    bordercolor=BORDER,
                    borderwidth=1,
                    relief="flat",
                    padding=4)
    style.configure("TCombobox",
                    fieldbackground=CARD,
                    background=CARD,
                    bordercolor=BORDER)


def main():
    root = tk.Tk()
    root.title("Task Manager")
    root.geometry("1040x680")
    root.minsize(800, 540)
    root.configure(bg=BG)
    _apply_styles()

    data = backend.load_data()
    current = [None]

    def show_login():
        if current[0]:
            current[0].destroy()
        f = LoginFrame(root, data, on_login=show_app)
        f.pack(fill="both", expand=True)
        current[0] = f

    def show_app(username):
        if current[0]:
            current[0].destroy()
        f = TaskApp(root, data, username, on_logout=show_login)
        f.pack(fill="both", expand=True)
        current[0] = f

    show_login()
    root.mainloop()


if __name__ == "__main__":
    main()
