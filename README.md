# Python Task Manager

A multi-user task manager built in Python — available as a **web app**, a **graphical desktop app (GUI)**, and a **command-line app (CLI)**.

---

## Features

- Create personal accounts and sign in securely
- Add tasks with title, description, due date, priority, and status
- Edit, delete, and mark tasks as complete
- Search tasks by keyword
- Filter by priority (Low / Medium / High) or status (Todo / In Progress / Done)
- Live stats bar with completion progress
- All data saved automatically to a local file

---

## Project Structure

| File / Folder     | Purpose                                                   |
|-------------------|-----------------------------------------------------------|
| `app.py`          | Flask web server — REST API + serves the frontend         |
| `main.py`         | Core data logic (load/save) + CLI version                 |
| `gui.py`          | Tkinter desktop GUI version                               |
| `test_main.py`    | Automated unit tests                                      |
| `templates/`      | HTML template for the web app                             |
| `static/`         | CSS and JavaScript for the web app                        |
| `project_report.md` | Full project write-up                                   |

> `data.json` is created automatically on first run and is excluded from version control (contains user passwords).

---

## How to Run

### Web App (recommended)

**Requirements:** Python 3.6+ and Flask

```bash
pip3 install flask
python3 app.py
```

Then open **http://localhost:8080** in your browser.

---

### Desktop GUI

**Requirements:** Python 3.6+ (Tkinter is included with Python)

```bash
python3 gui.py
```

---

### Command-Line (CLI)

**Requirements:** Python 3.6+, no extra packages

```bash
python3 main.py
```

---

### Run Tests

```bash
python3 -m unittest test_main -v
```

---

## Task Fields

| Field       | Options / Format               |
|-------------|-------------------------------|
| Title       | Any text (required)           |
| Description | Any text (optional)           |
| Due Date    | YYYY-MM-DD (optional)         |
| Priority    | Low · Medium · High           |
| Status      | Todo · In Progress · Done     |
