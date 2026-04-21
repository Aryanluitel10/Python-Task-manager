# Python Task Manager

A multi-user command-line task manager built in Python. No installation or internet required — everything runs locally and saves to a plain file on your computer.

## Features

- Create personal accounts and log in securely
- Add tasks with a title, description, due date, priority, and status
- View, edit, delete, and mark tasks as complete
- Search tasks by keyword
- Filter tasks by priority (Low / Medium / High) or status (Todo / In Progress / Done)
- All data saved automatically — nothing is lost if the program closes unexpectedly
- Optional graphical interface (GUI) included

## Files

| File | Purpose |
|---|---|
| `main.py` | Command-line version — run this to use the app in the terminal |
| `gui.py` | Graphical version — run this for a clickable window interface |
| `test_main.py` | Automated tests — run this to verify everything works |
| `data.json` | Where all user accounts and tasks are saved |
| `project_report.md` | Full project write-up |

## How to Run

**Requirements:** Python 3.6 or newer. No extra packages needed.

**Terminal (CLI) version:**
```bash
python3 main.py
```

**Graphical (GUI) version:**
```bash
python3 gui.py
```

**Run tests:**
```bash
python3 -m unittest test_main -v
```

## How It Works

1. Start the program and create an account
2. Log in with your username and password
3. Use the numbered menu to manage your tasks
4. All changes are saved automatically to `data.json`

## Task Fields

| Field | Options |
|---|---|
| Title | Any text (required) |
| Description | Any text (optional) |
| Due Date | YYYY-MM-DD format (optional) |
| Priority | Low, Medium, High |
| Status | Todo, In Progress, Done |
