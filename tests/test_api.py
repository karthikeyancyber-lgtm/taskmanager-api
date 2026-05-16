import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from backend.db.database import Base, get_db

# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite:///./test_taskmanager.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

USER = {"username": "testuser", "email": "test@example.com", "password": "secret123"}


def get_token():
    client.post("/register", json=USER)
    res = client.post("/login", json={"username": USER["username"], "password": USER["password"]})
    return res.json()["access_token"]


def auth_header():
    return {"Authorization": f"Bearer {get_token()}"}


# ── AUTH TESTS ───────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_success(self):
        res = client.post("/register", json=USER)
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == USER["username"]
        assert data["email"] == USER["email"]
        assert "id" in data

    def test_register_duplicate_username(self):
        client.post("/register", json=USER)
        res = client.post("/register", json=USER)
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"]

    def test_register_short_password(self):
        res = client.post("/register", json={**USER, "password": "abc"})
        assert res.status_code == 400

    def test_login_success(self):
        client.post("/register", json=USER)
        res = client.post("/login", json={"username": USER["username"], "password": USER["password"]})
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert res.json()["token_type"] == "bearer"

    def test_login_wrong_password(self):
        client.post("/register", json=USER)
        res = client.post("/login", json={"username": USER["username"], "password": "wrongpass"})
        assert res.status_code == 401

    def test_login_nonexistent_user(self):
        res = client.post("/login", json={"username": "ghost", "password": "pass"})
        assert res.status_code == 401


# ── TASK TESTS ───────────────────────────────────────────────────────────────

class TestTasks:
    def test_create_task(self):
        headers = auth_header()
        res = client.post("/tasks", json={"title": "Buy groceries", "description": "Milk and eggs"}, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Buy groceries"
        assert data["completed"] is False

    def test_get_all_tasks(self):
        headers = auth_header()
        client.post("/tasks", json={"title": "Task 1"}, headers=headers)
        client.post("/tasks", json={"title": "Task 2"}, headers=headers)
        res = client.get("/tasks", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 2

    def test_get_task_by_id(self):
        headers = auth_header()
        created = client.post("/tasks", json={"title": "Specific Task"}, headers=headers).json()
        res = client.get(f"/tasks/{created['id']}", headers=headers)
        assert res.status_code == 200
        assert res.json()["title"] == "Specific Task"

    def test_get_task_not_found(self):
        res = client.get("/tasks/9999", headers=auth_header())
        assert res.status_code == 404

    def test_mark_task_completed(self):
        headers = auth_header()
        task = client.post("/tasks", json={"title": "Finish report"}, headers=headers).json()
        res = client.put(f"/tasks/{task['id']}", json={"completed": True}, headers=headers)
        assert res.status_code == 200
        assert res.json()["completed"] is True

    def test_delete_task(self):
        headers = auth_header()
        task = client.post("/tasks", json={"title": "Delete me"}, headers=headers).json()
        res = client.delete(f"/tasks/{task['id']}", headers=headers)
        assert res.status_code == 204
        # Verify gone
        assert client.get(f"/tasks/{task['id']}", headers=headers).status_code == 404

    def test_filter_completed_tasks(self):
        headers = auth_header()
        t1 = client.post("/tasks", json={"title": "Done task"}, headers=headers).json()
        client.post("/tasks", json={"title": "Pending task"}, headers=headers)
        client.put(f"/tasks/{t1['id']}", json={"completed": True}, headers=headers)
        res = client.get("/tasks?completed=true", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1

    def test_pagination(self):
        headers = auth_header()
        for i in range(12):
            client.post("/tasks", json={"title": f"Task {i}"}, headers=headers)
        res = client.get("/tasks?page=1&page_size=5", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 12
        assert len(data["tasks"]) == 5

    def test_cannot_access_other_users_tasks(self):
        # User 1
        client.post("/register", json={"username": "user1", "email": "u1@x.com", "password": "pass123"})
        r1 = client.post("/login", json={"username": "user1", "password": "pass123"})
        h1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}

        # User 2
        client.post("/register", json={"username": "user2", "email": "u2@x.com", "password": "pass123"})
        r2 = client.post("/login", json={"username": "user2", "password": "pass123"})
        h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

        task = client.post("/tasks", json={"title": "Private task"}, headers=h1).json()
        # User 2 should NOT see User 1's task
        res = client.get(f"/tasks/{task['id']}", headers=h2)
        assert res.status_code == 404

    def test_unauthorized_access(self):
        res = client.get("/tasks")
        assert res.status_code == 401
