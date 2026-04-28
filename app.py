#!/usr/bin/env python3
"""
app.py — Flask web server for the Task Manager.

Serves the single-page frontend and exposes a REST API that reuses
load_data() / save_data() from main.py for all persistence.

Usage:
    python3 app.py
    Then open http://localhost:8080 in your browser.
"""

from flask import Flask, request, jsonify, render_template
import main as backend

app = Flask(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

VALID_PRIORITIES = {"Low", "Medium", "High"}
VALID_STATUSES   = {"Todo", "In Progress", "Done"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _parse_task_body(body):
    """
    Validate and extract task fields from a request body dict.
    Returns (task_dict, error_string). error_string is None on success.
    """
    title = (body.get("title") or "").strip()
    if not title:
        return None, "Title cannot be blank."

    due = (body.get("due_date") or "").strip()
    if due:
        parts = due.split("-")
        if not (len(parts) == 3
                and all(p.isdigit() for p in parts)
                and len(parts[0]) == 4):
            return None, "Due date must be in YYYY-MM-DD format."

    priority = body.get("priority", "Medium")
    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    status = body.get("status", "Todo")
    if status not in VALID_STATUSES:
        status = "Todo"

    task = {
        "title":       title,
        "description": (body.get("description") or "").strip(),
        "due_date":    due,
        "priority":    priority,
        "status":      status,
    }
    return task, None


def _require_user(username):
    """
    Load data and look up a user.
    Returns (data, tasks) on success, or (None, error_response) on failure.
    """
    data = backend.load_data()
    if username not in data["users"]:
        return None, (jsonify({"error": "User not found."}), 404)
    return data, data["users"][username]["tasks"]


# ── Frontend ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Auth API ─────────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def api_login():
    body     = request.get_json()
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Please enter your username and password."}), 400

    data = backend.load_data()
    user = data["users"].get(username)
    if not user:
        return jsonify({"error": "No account found with that username."}), 401
    if user["password"] != password:
        return jsonify({"error": "Incorrect password. Please try again."}), 401

    return jsonify({"success": True, "username": username})


@app.route("/api/register", methods=["POST"])
def api_register():
    body     = request.get_json()
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip()

    if not username:
        return jsonify({"error": "Username cannot be blank."}), 400
    if not password:
        return jsonify({"error": "Password cannot be blank."}), 400

    data = backend.load_data()
    if username in data["users"]:
        return jsonify({"error": "That username is already taken."}), 409

    data["users"][username] = {"password": password, "tasks": []}
    backend.save_data(data)
    return jsonify({"success": True, "username": username})


# ── Tasks API ─────────────────────────────────────────────────────────────────

@app.route("/api/tasks/<username>", methods=["GET"])
def get_tasks(username):
    data, tasks = _require_user(username)
    if data is None:
        return tasks  # tasks holds the error response tuple
    return jsonify({"tasks": tasks})


@app.route("/api/tasks/<username>", methods=["POST"])
def add_task(username):
    task, err = _parse_task_body(request.get_json())
    if err:
        return jsonify({"error": err}), 400

    data, tasks = _require_user(username)
    if data is None:
        return tasks

    tasks.append(task)
    backend.save_data(data)
    return jsonify({"success": True, "task": task}), 201


@app.route("/api/tasks/<username>/<int:idx>", methods=["PUT"])
def update_task(username, idx):
    task, err = _parse_task_body(request.get_json())
    if err:
        return jsonify({"error": err}), 400

    data, tasks = _require_user(username)
    if data is None:
        return tasks
    if not (0 <= idx < len(tasks)):
        return jsonify({"error": "Task not found."}), 404

    tasks[idx] = task
    backend.save_data(data)
    return jsonify({"success": True, "task": task})


@app.route("/api/tasks/<username>/<int:idx>", methods=["DELETE"])
def delete_task(username, idx):
    data, tasks = _require_user(username)
    if data is None:
        return tasks
    if not (0 <= idx < len(tasks)):
        return jsonify({"error": "Task not found."}), 404

    tasks.pop(idx)
    backend.save_data(data)
    return jsonify({"success": True})


@app.route("/api/tasks/<username>/<int:idx>/complete", methods=["PATCH"])
def complete_task(username, idx):
    data, tasks = _require_user(username)
    if data is None:
        return tasks
    if not (0 <= idx < len(tasks)):
        return jsonify({"error": "Task not found."}), 404

    tasks[idx]["status"] = "Done"
    backend.save_data(data)
    return jsonify({"success": True, "task": tasks[idx]})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Task Manager running at http://localhost:8080")
    app.run(debug=True, host="0.0.0.0", port=8080)
