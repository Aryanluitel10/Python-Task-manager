# Python Task Manager — Project Report

**Course:** Software Engineering
**Date:** April 20, 2026

---

## Table of Contents

1. Introduction
2. Requirements
3. System Design
4. Implementation
5. Testing
6. Conclusion

---

## 1. Introduction

### 1.1 Background

Most people have too many things to remember and not enough time. Whether it's homework, work tasks, or personal errands, keeping track of everything is hard. Tools like sticky notes help, but they get lost. Apps like Trello or Notion are powerful, but they need an internet connection, require creating an account on someone else's server, and can be overwhelming for simple needs.

This project solves that problem in a simple way: a task manager that runs directly on your computer, needs no internet, and stores everything in a plain file on your own machine.

### 1.2 What Was Built

This project is a **Task Manager program** written in Python. It works through a text-based menu — you type a number to choose what you want to do. Multiple people can use it on the same computer, each with their own account and private task list.

Each task can have:
- A **title** (short name for the task)
- A **description** (more detail about what needs to be done)
- A **due date** (when it needs to be finished)
- A **priority** (Low, Medium, or High — how urgent it is)
- A **status** (Todo, In Progress, or Done — how far along it is)

Everything is saved automatically to a file called `data.json` so your tasks are still there the next time you open the program.

### 1.3 Goals

The project set out to achieve the following:

- Build a working task manager that real people could actually use.
- Keep the code organized so each piece does one clear job.
- Make sure data is never lost — not even if the program crashes mid-save.
- Write tests that automatically check the program works correctly.
- Keep it simple: no complicated setup, no extra software to install.

### 1.4 What It Doesn't Do

This program runs in a text window (terminal). It does not have clickable buttons or images — though a visual version (`gui.py`) was also created as a bonus. It stores data on the local computer only and is designed for one person using one computer at a time.

---

## 2. Requirements

Think of requirements as a checklist written before building anything — they describe exactly what the finished product must be able to do.

### 2.1 What the Program Must Do

These are the features users need:

| # | Feature |
|---|---------|
| 1 | A new user can create an account with a unique username and password. |
| 2 | Two users cannot have the same username. |
| 3 | A registered user can log in with their username and password. |
| 4 | If the username or password is wrong, login is blocked. |
| 5 | A logged-in user can add a task with a title, description, due date, priority, and status. |
| 6 | A user can see all their tasks, or only the ones not yet finished. |
| 7 | A user can edit any detail of a task they already created. |
| 8 | A user can delete a task they no longer need. |
| 9 | A user can mark a task as "Done." |
| 10 | A user can search for tasks by typing a keyword. |
| 11 | A user can filter tasks by priority (Low / Medium / High) or status (Todo / In Progress / Done). |
| 12 | Any change — adding, editing, deleting — is saved to the file immediately. |
| 13 | When the program starts, it loads all previously saved tasks automatically. |

### 2.2 How Well It Must Work

Beyond what the program does, there are rules about how it must behave:

| Rule | Explanation |
|---|---|
| Works on any computer | As long as Python 3.6 or newer is installed, the program runs — no other software needed. |
| No extra installs | Only tools that come built into Python are used. Nothing needs to be downloaded. |
| Safe saving | If the program crashes while saving, the file must not get corrupted or wiped. |
| Automatic backup | The program always keeps a backup copy of your data from the last successful save. |
| Input checking | If you type something wrong (like a blank task name or a bad date), the program catches it and asks again instead of crashing. |
| Clean code | Each feature has its own small, focused section of code, making it easy to read and fix. |

### 2.3 Limitations Accepted From the Start

- **Passwords are stored as plain text.** This means someone who opens the data file could read them. Encrypting passwords is a known improvement for a future version.
- **One computer only.** If two people tried to save changes at exactly the same moment from two different windows, they could overwrite each other. This is fine for a personal tool.
- **All code in one file.** Everything lives in `main.py` to keep things simple.

---

## 3. System Design

This section explains how the program is structured — like a blueprint before building a house.

### 3.1 How the Program Is Organized

The program is divided into three layers, each with a different job:

```
┌──────────────────────────────────────────┐
│  What the user sees and types            │  Shows menus, reads your input
├──────────────────────────────────────────┤
│  The brain — what the program does       │  Adds, edits, deletes, searches tasks
├──────────────────────────────────────────┤
│  Storage — reading and writing the file  │  Loads and saves data.json
└──────────────────────────────────────────┘
```

Every action that changes data (like adding a task) immediately triggers a save to the file. This way the program never has unsaved changes sitting around.

### 3.2 How Data Is Stored

All data is kept in a file called `data.json`. JSON is a simple, human-readable format that looks like this — you could even open it in a text editor and read it:

```
data.json
│
└── users
    └── alice
        ├── password: "mypassword"
        └── tasks
            ├── Task 1: "Finish report" | High | In Progress | Due: 2026-05-01
            └── Task 2: "Buy groceries" | Low  | Todo        | Due: (none)
```

Each user has their own private list of tasks stored under their name.

### 3.3 What Each Function Does

The program is built from small, named pieces called **functions** — each one does exactly one job:

| Function | What it does in plain English |
|---|---|
| `load_data()` | Opens the saved file when the program starts |
| `save_data()` | Safely writes all data to the file |
| `create_account()` | Signs up a new user |
| `login()` | Checks the username and password |
| `add_task()` | Asks for task details and saves the new task |
| `view_tasks()` | Shows the task list (all or incomplete only) |
| `edit_task()` | Changes details on an existing task |
| `delete_task()` | Removes a task from the list |
| `mark_complete()` | Sets a task's status to "Done" |
| `search_tasks()` | Finds tasks that contain a keyword |
| `filter_by_priority()` | Shows only tasks of a chosen priority |
| `filter_by_status()` | Shows only tasks with a chosen status |
| `user_menu()` | Shows the main menu after login |
| `main()` | Starts the program and keeps it running |

There are also a few smaller helper pieces that handle things like asking for a date or displaying a task — they're shared across multiple functions so the same logic doesn't have to be written twice.

### 3.4 How the Program Flows

Here is the step-by-step journey from opening the program to getting things done:

1. Program starts → loads saved data from `data.json`
2. Main menu appears → user picks: Login, Create Account, or Exit
3. After a successful login → Task Menu appears with 10 options
4. User picks an action (add, edit, delete, etc.) → action runs → Task Menu appears again
5. User picks Logout → back to Main Menu
6. User picks Exit → program closes

### 3.5 How Saving Works (and Why It's Safe)

Saving might seem simple — just write to the file. But what if the program crashes halfway through writing? The file could end up half-written and corrupted, losing all your data.

To prevent this, the program uses a safer three-step approach:

1. **Write to a temporary "draft" file** — the original `data.json` is untouched at this point.
2. **Copy the current `data.json` to `data.json.bak`** — this is your backup, always one save behind.
3. **Swap the draft file in** — the draft replaces `data.json` in one instant operation. There is no moment where the file is half-written.

When opening the program, it tries to read `data.json` first. If that file is missing or broken, it automatically falls back to the backup `data.json.bak`. If neither file exists, it starts fresh.

---

## 4. Implementation

This section explains how the key parts were actually built.

### 4.1 Tools Used

| What | Choice | Why |
|---|---|---|
| Programming language | Python 3 | Easy to read, great built-in tools |
| Data storage | A `.json` text file | Simple, no database needed, human-readable |
| User interaction | Text menus in the terminal | Works everywhere, no installation |
| Automated tests | Python's built-in test tools | No extra software needed |

### 4.2 Creating and Logging Into Accounts

**Creating an account:** The program asks for a username and password. It will not accept a blank username or a name that's already taken — it keeps asking until you give a valid one. Once accepted, the account is saved immediately.

**Logging in:** The program checks two things: does the username exist, and does the password match? If either check fails, it says so and goes back to the menu. It does not give hints about which one was wrong (for security).

### 4.3 Task Features

**Adding a task:** The program walks you through each field one by one — title, description, due date, priority, and status. Each field has its own validation. For example:
- Due date must be in the format `YYYY-MM-DD` (e.g., `2026-05-15`), or you can leave it blank.
- Priority and status are chosen from a numbered menu, so you can't type something invalid.

**Editing a task:** The program shows what the task currently says for each field. You can type a new value, or just press Enter to keep the existing one. This way you don't have to retype everything just to change one detail.

**Deleting a task:** The program shows the full task list, you pick a number, and it removes that task. If you pick a number that doesn't exist (like 99 when there are only 3 tasks), it says "Invalid selection" instead of crashing.

**Marking complete:** Only tasks that aren't already done are shown. Marking a task complete changes its status to "Done" — it stays in your list so you can see what you've accomplished.

### 4.4 Searching and Filtering

**Search:** Type any keyword and the program checks every task's title, description, and due date for it. The search ignores capital letters, so "LOGIN" and "login" find the same results. It tells you how many matches were found.

**Filter by Priority:** Choose High, Medium, or Low — only tasks with that priority are shown, along with a count.

**Filter by Status:** Choose Todo, In Progress, or Done — only tasks in that state are shown.

### 4.5 How Tasks Are Displayed

Every place that shows tasks uses the same display format, so it always looks the same:

```
1. [High] Fix login bug — Todo  Due: 2026-05-01
    Description: Investigate the auth failure on empty password
```

This consistent layout — number, priority in brackets, title, status, and due date — makes it easy to scan your list quickly.

### 4.6 Three Smart Design Choices

- **Load once, share everywhere.** The data file is read only once at startup. After that, every function works with the same copy in memory. Any change made anywhere is immediately visible everywhere else — no need to keep re-reading the file.

- **Save after every change.** Instead of waiting until the program closes to save, every action that changes anything saves immediately. If your computer crashes or you force-close the terminal, you lose at most the action you were in the middle of — never everything.

- **No extra software.** The entire program uses only tools that come pre-installed with Python. Anyone who has Python can run it — no extra downloads, no setup scripts, no package managers.

---

## 5. Testing

Testing means checking that the program does what it's supposed to do — automatically, without a human clicking through everything by hand.

### 5.1 How Testing Works

A separate file called `test_main.py` contains the tests. Each test:
1. Sets up a fake data situation (e.g., a user with some tasks already in it).
2. Calls a function from the main program.
3. Checks that the result is exactly what was expected.

Since the tests involve typing things in a terminal, a technique called **mocking** is used — the tests pretend to type inputs automatically, so no real human needs to interact. The tests also pretend to save to a file, so nothing on your actual disk is changed while tests run.

All 13 tests finish in under one second.

### 5.2 The 5 Test Cases

#### Test Case 1 — Creating an Account

**What's being checked:** Does signing up a new user actually work? And does the program stop you from using a username that's already taken?

| Scenario | What was typed | What should happen |
|---|---|---|
| New user signs up | Username: `alice`, Password: `secret99` | Account is created and saved correctly |
| Duplicate username | Username: `alice` (already exists) | Program rejects it; existing account is untouched |

#### Test Case 2 — Logging In

**What's being checked:** Does login let the right people in and keep the wrong ones out?

| Scenario | What was typed | What should happen |
|---|---|---|
| Correct details | `testuser` / `pass123` | Login succeeds, username returned |
| Wrong password | `testuser` / `wrongpass` | Login fails |
| Username doesn't exist | `nobody` / `pass123` | Login fails |

#### Test Case 3 — Adding a Task

**What's being checked:** Are all the task details saved correctly? What happens with a blank title?

| Scenario | What was typed | What should happen |
|---|---|---|
| Full task details | Title, description, due date `2026-06-30`, priority High, status In Progress | Task saved with all correct details |
| Blank title | (nothing entered for title) | No task is created; nothing is saved |

#### Test Case 4 — Deleting a Task

**What's being checked:** Does the right task get removed? What happens with a bad number?

| Scenario | What was typed | What should happen |
|---|---|---|
| Valid task number | `1` (with 2 tasks in the list) | First task removed, second task stays |
| Number out of range | `99` (only 1 task exists) | Nothing is deleted, no error |

#### Test Case 5 — Searching and Filtering

**What's being checked:** Does search find the right tasks? Do filters return the right groups?

Three tasks are set up for this test: "Fix login bug" (High, Todo), "Write docs" (Low, Done), "Deploy to prod" (High, In Progress).

| Scenario | What was typed | What should happen |
|---|---|---|
| Search for "login" | `login` | Finds exactly 1 task: "Fix login bug" |
| Search for nonsense | `xyz_no_match` | Finds nothing |
| Filter: High priority | Choose "High" | Returns 2 tasks |
| Filter: Done status | Choose "Done" | Returns 1 task: "Write docs" |

### 5.3 Test Results

```
Ran 13 tests in 0.003s

OK
```

Every single test passed. No failures, no errors.

### 5.4 Known Gaps in Testing

- **Passwords are not encrypted.** Anyone who opens `data.json` can read them. A future version should scramble passwords before saving them.
- **No test for two people saving at the same time.** The program is designed for one person on one computer, so this is acceptable for now.
- **No full end-to-end test.** The tests check individual functions. A complete test that simulates a whole session — from start to logout — was not included, but would be a good addition.

---

## 6. Conclusion

### 6.1 What Was Achieved

This project built a fully working task manager that multiple people can use on the same computer. It covers every feature that was planned: creating accounts, logging in, and managing tasks with add, view, edit, delete, complete, search, and filter.

The program never loses your data — not even if it crashes while saving. It keeps a backup automatically. And it runs on any computer with Python, without installing anything extra.

All 13 automated tests pass, confirming the core features work correctly.

### 6.2 Problems Encountered and How They Were Solved

| Problem | How It Was Solved |
|---|---|
| File could get corrupted if the program crashed during saving | Now saves to a temporary file first, then swaps it in all at once |
| Program crashed on startup if `data.json` was empty or broken | Now checks the file first and falls back to the backup automatically |
| Users could type invalid dates and break the program | Added a loop that keeps asking until a valid date (or nothing) is entered |
| Testing functions that require user input is tricky | Used a technique that "fakes" keyboard input automatically during tests |
| Tasks looked different depending on which menu you were in | Created one shared display function used everywhere, so it always looks the same |

### 6.3 What Could Be Better

Here are six improvements that would make the program stronger in a future version:

1. **Encrypt passwords.** Right now passwords are stored as plain text. They should be scrambled (hashed) before saving, so even someone who opens the file can't read them.

2. **Stable task numbers.** If you have tasks 1, 2, 3 and delete task 2, the old task 3 becomes task 2. Giving each task a permanent ID would avoid this confusion.

3. **Sort by due date.** Being able to see tasks ordered by deadline would help users focus on what's most urgent.

4. **Export to a file.** Allow users to save their task list as a spreadsheet (CSV) or document (Markdown) so they can share it or open it elsewhere.

5. **Color coding in the terminal.** Show High priority tasks in red, Medium in yellow, and Low in green — making it much faster to scan the list.

6. **Switch to a database.** For many users or very large task lists, a lightweight database (like SQLite) would be faster and more reliable than a plain text file.

### 6.4 Final Thoughts

This project shows that you don't need complicated technology to build something genuinely useful. By keeping things simple — one file, no extra software, plain text storage — the focus stayed on solving the actual problem: helping people keep track of their tasks.

The program is easy to run, easy to understand, and built to be extended. It's a solid foundation for anyone who wants to take it further.

---

*End of Report*
