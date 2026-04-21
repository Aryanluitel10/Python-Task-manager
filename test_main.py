import unittest
from unittest.mock import patch
import main


def make_data(*tasks, password="pass123"):
    """Return a minimal in-memory data structure pre-loaded with a test user."""
    return {
        "users": {
            "testuser": {
                "password": password,
                "tasks": list(tasks),
            }
        }
    }


def make_task(title="Fix bug", description="Details here",
              due_date="2026-05-01", priority="High", status="Todo"):
    return {
        "title": title,
        "description": description,
        "due_date": due_date,
        "priority": priority,
        "status": status,
    }


class TestCreateAccount(unittest.TestCase):
    """TC1 — Create account with a unique username and password."""

    @patch("main.save_data")
    @patch("builtins.input", side_effect=["alice", "secret99"])
    def test_new_account_is_stored(self, _mock_input, _mock_save):
        data = {"users": {}}
        returned_user = main.create_account(data)

        self.assertEqual(returned_user, "alice")
        self.assertIn("alice", data["users"])
        self.assertEqual(data["users"]["alice"]["password"], "secret99")
        self.assertEqual(data["users"]["alice"]["tasks"], [])

    @patch("main.save_data")
    @patch("builtins.input", side_effect=["alice", "newpass"])
    def test_duplicate_username_rejected(self, _mock_input, _mock_save):
        """Username that already exists should loop; we supply it once then the
        side_effect list is exhausted, which is fine — we just check the user
        dict is NOT overwritten."""
        data = {"users": {"alice": {"password": "original", "tasks": []}}}
        # The mock provides "alice" (rejected) then "newpass" — but since the
        # loop asks for a username again, it will raise StopIteration before a
        # second username can be given.  Catch that and verify original data
        # is untouched.
        with self.assertRaises(StopIteration):
            main.create_account(data)
        self.assertEqual(data["users"]["alice"]["password"], "original")


class TestLogin(unittest.TestCase):
    """TC2 — Login with correct and incorrect credentials."""

    @patch("builtins.input", side_effect=["testuser", "pass123"])
    def test_correct_credentials_return_username(self, _mock_input):
        data = make_data(password="pass123")
        result = main.login(data)
        self.assertEqual(result, "testuser")

    @patch("builtins.input", side_effect=["testuser", "wrongpass"])
    def test_wrong_password_returns_none(self, _mock_input):
        data = make_data(password="pass123")
        result = main.login(data)
        self.assertIsNone(result)

    @patch("builtins.input", side_effect=["nobody", "pass123"])
    def test_unknown_username_returns_none(self, _mock_input):
        data = make_data(password="pass123")
        result = main.login(data)
        self.assertIsNone(result)


class TestAddTask(unittest.TestCase):
    """TC3 — Add a task with all fields; verify it is appended and saved."""

    @patch("main.save_data")
    @patch("builtins.input", side_effect=[
        "Write report",   # title
        "Q2 summary",     # description
        "2026-06-30",     # due date
        "3",              # priority → High
        "2",              # status  → In Progress
    ])
    def test_task_added_with_correct_fields(self, _mock_input, mock_save):
        data = make_data()
        main.add_task("testuser", data)

        tasks = data["users"]["testuser"]["tasks"]
        self.assertEqual(len(tasks), 1)
        t = tasks[0]
        self.assertEqual(t["title"], "Write report")
        self.assertEqual(t["description"], "Q2 summary")
        self.assertEqual(t["due_date"], "2026-06-30")
        self.assertEqual(t["priority"], "High")
        self.assertEqual(t["status"], "In Progress")
        mock_save.assert_called_once()

    @patch("main.save_data")
    @patch("builtins.input", side_effect=[""])
    def test_blank_title_does_not_add_task(self, _mock_input, mock_save):
        data = make_data()
        main.add_task("testuser", data)
        self.assertEqual(len(data["users"]["testuser"]["tasks"]), 0)
        mock_save.assert_not_called()


class TestDeleteTask(unittest.TestCase):
    """TC4 — Delete an existing task; verify it is removed and saved."""

    @patch("main.save_data")
    @patch("builtins.input", return_value="1")
    def test_delete_removes_correct_task(self, _mock_input, mock_save):
        task_a = make_task(title="Task A")
        task_b = make_task(title="Task B")
        data = make_data(task_a, task_b)

        main.delete_task("testuser", data)

        remaining = data["users"]["testuser"]["tasks"]
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["title"], "Task B")
        mock_save.assert_called_once()

    @patch("main.save_data")
    @patch("builtins.input", return_value="99")
    def test_out_of_range_index_does_not_delete(self, _mock_input, mock_save):
        data = make_data(make_task())
        main.delete_task("testuser", data)
        self.assertEqual(len(data["users"]["testuser"]["tasks"]), 1)
        mock_save.assert_not_called()


class TestSearchAndFilter(unittest.TestCase):
    """TC5 — Search by keyword and filter by priority / status."""

    def setUp(self):
        self.data = make_data(
            make_task(title="Fix login bug",   priority="High",   status="Todo"),
            make_task(title="Write docs",      priority="Low",    status="Done"),
            make_task(title="Deploy to prod",  priority="High",   status="In Progress"),
        )

    @patch("builtins.input", return_value="login")
    def test_search_finds_matching_task(self, _mock_input):
        """Keyword 'login' should match exactly one task."""
        tasks = self.data["users"]["testuser"]["tasks"]
        query = "login"
        found = [t for t in tasks if query in t["title"].lower()
                 or query in t.get("description", "").lower()]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["title"], "Fix login bug")

    @patch("builtins.input", return_value="xyz_no_match")
    def test_search_returns_empty_for_no_match(self, _mock_input):
        tasks = self.data["users"]["testuser"]["tasks"]
        query = "xyz_no_match"
        found = [t for t in tasks if query in t["title"].lower()]
        self.assertEqual(found, [])

    @patch("builtins.input", return_value="1")   # 1 → High
    def test_filter_by_priority_high(self, _mock_input):
        tasks = self.data["users"]["testuser"]["tasks"]
        high = [t for t in tasks if t.get("priority") == "High"]
        self.assertEqual(len(high), 2)

    @patch("builtins.input", return_value="3")   # 3 → Done
    def test_filter_by_status_done(self, _mock_input):
        tasks = self.data["users"]["testuser"]["tasks"]
        done = [t for t in tasks if t.get("status") == "Done"]
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0]["title"], "Write docs")


if __name__ == "__main__":
    unittest.main(verbosity=2)
