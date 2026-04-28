import json
import os
import shutil
import tempfile

# Vercel's filesystem is read-only — use /tmp for data storage when deployed
_ON_VERCEL  = bool(os.environ.get("VERCEL"))
DATA_FILE   = "/tmp/data.json"   if _ON_VERCEL else "data.json"
BACKUP_FILE = "/tmp/data.json.bak" if _ON_VERCEL else "data.json.bak"

def load_data():
    """
    Load data from DATA_FILE on startup.
    Falls back to the backup file if the primary is missing or corrupted.
    Returns a fresh structure if neither file is usable.
    """
    for filepath in (DATA_FILE, BACKUP_FILE):
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
            if content:
                data = json.loads(content)
                if isinstance(data, dict) and 'users' in data:
                    if filepath == BACKUP_FILE:
                        print("[Warning] Primary data file was unreadable. Loaded from backup.")
                    return data
        except (json.JSONDecodeError, OSError):
            continue
    return {"users": {}}

def save_data(data):
    """
    Atomically save data to DATA_FILE.
    Writes to a temp file first, then renames to avoid corruption on crash.
    Also keeps a rolling backup of the last good save.
    """
    try:
        dir_name = os.path.dirname(os.path.abspath(DATA_FILE))
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, suffix='.tmp') as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = tmp.name
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, BACKUP_FILE)
        os.replace(tmp_path, DATA_FILE)
    except OSError as e:
        print(f"[Error] Could not save data: {e}")

def create_account(data):
    """
    Handles new user account creation.
    Stores username and password in the JSON data.
    """
    print("=== Create Account ===")
    while True:
        username = input("Enter a username: ").strip()
        if not username:
            print("Username cannot be blank.")
            continue
        if username in data["users"]:
            print("Username already exists. Try a different one.")
            continue
        break

    while True:
        password = input("Enter a password: ").strip()
        if not password:
            print("Password cannot be blank.")
            continue
        break

    data['users'][username] = {
        "password": password,
        "tasks": []
    }
    save_data(data)
    print("Account created successfully.")
    return username

def login(data):
    """
    Handles user login.
    Checks JSON data for username and password match.
    """
    print("=== Login ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = data['users'].get(username)
    if not user:
        print("Username not found.")
        return None
    if user['password'] != password:
        print("Incorrect password.")
        return None
    print("Login successful.")
    return username

PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Todo", "In Progress", "Done"]

def _prompt_priority():
    print("Priority: 1. Low  2. Medium  3. High")
    choice = input("Choose priority (default Medium): ").strip()
    return {"1": "Low", "2": "Medium", "3": "High"}.get(choice, "Medium")

def _prompt_status():
    print("Status: 1. Todo  2. In Progress  3. Done")
    choice = input("Choose status (default Todo): ").strip()
    return {"1": "Todo", "2": "In Progress", "3": "Done"}.get(choice, "Todo")

def _prompt_due_date():
    while True:
        due_date = input("Due date (YYYY-MM-DD, leave blank to skip): ").strip()
        if not due_date:
            return ""
        parts = due_date.split("-")
        if len(parts) == 3 and all(p.isdigit() for p in parts) and len(parts[0]) == 4:
            return due_date
        print("Invalid format. Please use YYYY-MM-DD.")

def add_task(user, data):
    print("=== Add Task ===")
    title = input("Task title: ").strip()
    if not title:
        print("Title cannot be blank.")
        return
    description = input("Task description: ").strip()
    due_date = _prompt_due_date()
    priority = _prompt_priority()
    status = _prompt_status()
    task = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "priority": priority,
        "status": status,
    }
    data['users'][user]['tasks'].append(task)
    save_data(data)
    print("Task added.")

def _format_task(idx, task):
    due = f"  Due: {task.get('due_date')}" if task.get('due_date') else ""
    priority = task.get('priority', 'Medium')
    status = task.get('status', 'Todo')
    print(f"{idx + 1}. [{priority}] {task['title']} — {status}{due}")
    print(f"    Description: {task.get('description', '')}")

def view_tasks(user, data, only_incomplete=False):
    tasks = data['users'][user]['tasks']
    if only_incomplete:
        tasks = [t for t in tasks if t.get('status', 'Todo') != 'Done']
    if not tasks:
        print("No tasks to show.")
        return
    for idx, task in enumerate(tasks):
        _format_task(idx, task)

def edit_task(user, data):
    print("=== Edit Task ===")
    tasks = data['users'][user]['tasks']
    if not tasks:
        print("No tasks to edit.")
        return
    view_tasks(user, data)
    try:
        idx = int(input("Enter the number of the task to edit: ")) - 1
        if not (0 <= idx < len(tasks)):
            print("Invalid selection.")
            return
        task = tasks[idx]
        title = input(f"New title (current: {task['title']}, leave blank to keep): ").strip()
        description = input(f"New description (current: {task.get('description','')}, leave blank to keep): ").strip()
        print(f"Current due date: {task.get('due_date') or 'None'}")
        due_date = _prompt_due_date()
        print(f"Current priority: {task.get('priority', 'Medium')}")
        priority = input("New priority (1=Low 2=Medium 3=High, leave blank to keep): ").strip()
        print(f"Current status: {task.get('status', 'Todo')}")
        status = input("New status (1=Todo 2=In Progress 3=Done, leave blank to keep): ").strip()

        if title:
            task['title'] = title
        if description:
            task['description'] = description
        if due_date:
            task['due_date'] = due_date
        if priority:
            task['priority'] = {"1": "Low", "2": "Medium", "3": "High"}.get(priority, task.get('priority', 'Medium'))
        if status:
            task['status'] = {"1": "Todo", "2": "In Progress", "3": "Done"}.get(status, task.get('status', 'Todo'))

        save_data(data)
        print("Task updated.")
    except ValueError:
        print("Invalid input.")

def delete_task(user, data):
    print("=== Delete Task ===")
    tasks = data['users'][user]['tasks']
    if not tasks:
        print("No tasks to delete.")
        return
    view_tasks(user, data)
    try:
        idx = int(input("Enter the number of the task to delete: ")) - 1
        if 0 <= idx < len(tasks):
            deleted = tasks.pop(idx)
            save_data(data)
            print(f"Task '{deleted['title']}' deleted.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")

def mark_complete(user, data):
    print("=== Mark Task as Complete ===")
    tasks = data['users'][user]['tasks']
    incomplete = [i for i, t in enumerate(tasks) if t.get('status', 'Todo') != 'Done']
    if not incomplete:
        print("All tasks are already completed.")
        return
    for i in incomplete:
        task = tasks[i]
        print(f"{i + 1}. [{task.get('priority','Medium')}] {task['title']} — {task.get('status','Todo')}")
    try:
        idx = int(input("Enter the number of the task to mark complete: ")) - 1
        if 0 <= idx < len(tasks) and tasks[idx].get('status', 'Todo') != 'Done':
            tasks[idx]['status'] = 'Done'
            save_data(data)
            print("Task marked as complete.")
        else:
            print("Invalid selection or already completed.")
    except ValueError:
        print("Invalid input.")

def search_tasks(user, data):
    """Search tasks by keyword across title, description, and due date."""
    print("=== Search Tasks by Keyword ===")
    query = input("Enter search keyword: ").strip().lower()
    if not query:
        print("No keyword entered.")
        return
    tasks = data['users'][user]['tasks']
    found = [
        (idx, task) for idx, task in enumerate(tasks)
        if query in task['title'].lower()
        or query in task.get('description', '').lower()
        or query in task.get('due_date', '').lower()
    ]
    print(f"\n{len(found)} result(s) for '{query}':")
    if found:
        for idx, task in found:
            _format_task(idx, task)
    else:
        print("No matching tasks found.")

def filter_by_priority(user, data):
    """Filter and display tasks matching a chosen priority level."""
    print("=== Filter Tasks by Priority ===")
    print("1. High")
    print("2. Medium")
    print("3. Low")
    choice = input("Choose priority: ").strip()
    priority_map = {"1": "High", "2": "Medium", "3": "Low"}
    if choice not in priority_map:
        print("Invalid choice.")
        return
    selected = priority_map[choice]
    tasks = data['users'][user]['tasks']
    filtered = [t for t in tasks if t.get('priority', 'Medium') == selected]
    print(f"\nTasks with priority '{selected}': {len(filtered)} found")
    if not filtered:
        print("No tasks found for this priority.")
        return
    for idx, task in enumerate(filtered):
        _format_task(idx, task)

def filter_by_status(user, data):
    """Filter and display tasks matching a chosen completion status."""
    print("=== Filter Tasks by Status ===")
    print("1. Todo")
    print("2. In Progress")
    print("3. Done")
    choice = input("Choose status: ").strip()
    status_map = {"1": "Todo", "2": "In Progress", "3": "Done"}
    if choice not in status_map:
        print("Invalid choice.")
        return
    selected = status_map[choice]
    tasks = data['users'][user]['tasks']
    filtered = [t for t in tasks if t.get('status', 'Todo') == selected]
    print(f"\nTasks with status '{selected}': {len(filtered)} found")
    if not filtered:
        print("No tasks found for this status.")
        return
    for idx, task in enumerate(filtered):
        _format_task(idx, task)

def user_menu(username, data):
    while True:
        print(f"\n--- Task Manager Menu (User: {username}) ---")
        print("1.  Add Task")
        print("2.  View All Tasks")
        print("3.  View Incomplete Tasks")
        print("4.  Edit Task")
        print("5.  Delete Task")
        print("6.  Mark Task as Complete")
        print("7.  Search Tasks by Keyword")
        print("8.  Filter by Priority")
        print("9.  Filter by Status")
        print("10. Logout")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_task(username, data)
        elif choice == "2":
            view_tasks(username, data)
        elif choice == "3":
            view_tasks(username, data, only_incomplete=True)
        elif choice == "4":
            edit_task(username, data)
        elif choice == "5":
            delete_task(username, data)
        elif choice == "6":
            mark_complete(username, data)
        elif choice == "7":
            search_tasks(username, data)
        elif choice == "8":
            filter_by_priority(username, data)
        elif choice == "9":
            filter_by_status(username, data)
        elif choice == "10":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")

def main():
    data = load_data()
    while True:
        print("\n=== Welcome to Simple Task Manager ===")
        print("1. Login")
        print("2. Create Account")
        print("3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            user = login(data)
            if user:
                user_menu(user, data)
        elif choice == "2":
            user = create_account(data)
            if user:
                user_menu(user, data)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()