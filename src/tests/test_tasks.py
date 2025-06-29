import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime

from src.tasks.controller import router as tasks_router
from src.tasks.service import TaskService
from src.tasks.models import TaskCreate
from src.auth.models import User
from src.database import get_session
from uuid import uuid4


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        disabled=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="client")
def client_fixture(session: Session, test_user: User):
    def get_session_override():
        return session

    def get_current_active_user_override():
        return test_user

    app = FastAPI()
    app.include_router(tasks_router)
    app.dependency_overrides[get_session] = get_session_override

    # Mock the auth dependency
    from src.auth.service import get_current_active_user
    app.dependency_overrides[get_current_active_user] = get_current_active_user_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestTaskService:
    def test_create_task(self, session: Session, test_user: User):
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description"
        )
        task = TaskService.create_task(task_data, test_user, session)

        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.user_id == test_user.id
        assert task.completed is False

    def test_create_task_with_deadline(self, session: Session, test_user: User):
        deadline = datetime(2024, 12, 31, 23, 59, 59)
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            deadline=deadline
        )
        task = TaskService.create_task(task_data, test_user, session)

        assert task.deadline == deadline

    def test_get_all_tasks(self, session: Session, test_user: User):
        # Create test tasks
        task_data1 = TaskCreate(title="Task 1", description="Description 1")
        task_data2 = TaskCreate(title="Task 2", description="Description 2")

        TaskService.create_task(task_data1, test_user, session)
        TaskService.create_task(task_data2, test_user, session)

        tasks = TaskService.get_all_tasks(test_user, session)
        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    def test_get_all_tasks_user_specific(self, session: Session, test_user: User):
        # Create another user
        other_user = User(
            id=uuid4(),
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
            disabled=False
        )
        session.add(other_user)
        session.commit()

        # Create tasks for both users
        task_data1 = TaskCreate(title="User 1 Task", description="Description")
        task_data2 = TaskCreate(title="User 2 Task", description="Description")

        TaskService.create_task(task_data1, test_user, session)
        TaskService.create_task(task_data2, other_user, session)

        tasks = TaskService.get_all_tasks(test_user, session)
        assert len(tasks) == 1
        assert tasks[0].title == "User 1 Task"

    def test_update_task(self, session: Session, test_user: User):
        # Create a task
        task_data = TaskCreate(title="Original Title", description="Original Description")
        task = TaskService.create_task(task_data, test_user, session)

        # Update the task
        update_data = TaskCreate(title="Updated Title", description="Updated Description")
        updated_task = TaskService.update_task(task.id, update_data, test_user, session)

        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"

    def test_update_nonexistent_task(self, session: Session, test_user: User):
        update_data = TaskCreate(title="Updated Title", description="Updated Description")
        updated_task = TaskService.update_task(999, update_data, test_user, session)

        assert updated_task is None

    def test_update_other_user_task(self, session: Session, test_user: User):
        # Create another user and their task
        other_user = User(
            id=uuid4(),
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
            disabled=False
        )
        session.add(other_user)
        session.commit()

        task_data = TaskCreate(title="Other User Task", description="Description")
        other_task = TaskService.create_task(task_data, other_user, session)

        # Try to update other user's task
        update_data = TaskCreate(title="Hacked", description="Hacked")
        updated_task = TaskService.update_task(other_task.id, update_data, test_user, session)

        assert updated_task is None

    def test_delete_task(self, session: Session, test_user: User):
        # Create a task
        task_data = TaskCreate(title="To Delete", description="Description")
        task = TaskService.create_task(task_data, test_user, session)

        # Delete the task
        deleted_task = TaskService.delete_task(task.id, test_user, session)

        assert deleted_task is not None
        assert deleted_task.id == task.id

        # Verify task is deleted
        tasks = TaskService.get_all_tasks(test_user, session)
        assert len(tasks) == 0

    def test_delete_nonexistent_task(self, session: Session, test_user: User):
        deleted_task = TaskService.delete_task(999, test_user, session)
        assert deleted_task is None


class TestTaskController:
    def test_create_task_endpoint(self, client: TestClient):
        task_data = {
            "title": "Test Task",
            "description": "Test Description"
        }
        response = client.post("/tasks/create", json=task_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["completed"] is False

    def test_get_all_tasks_endpoint(self, client: TestClient):
        # Create a task first
        task_data = {
            "title": "Test Task",
            "description": "Test Description"
        }
        client.post("/tasks/create", json=task_data)

        response = client.get("/tasks/get_all")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Task"

    def test_update_task_endpoint(self, client: TestClient):
        # Create a task first
        task_data = {
            "title": "Original Title",
            "description": "Original Description"
        }
        create_response = client.post("/tasks/create", json=task_data)
        task_id = create_response.json()["id"]

        # Update the task
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }
        response = client.put(f"/tasks/update/{task_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"

    def test_update_nonexistent_task_endpoint(self, client: TestClient):
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }
        response = client.put("/tasks/update/999", json=update_data)
        assert response.status_code == 404

    def test_delete_task_endpoint(self, client: TestClient):
        # Create a task first
        task_data = {
            "title": "To Delete",
            "description": "Description"
        }
        create_response = client.post("/tasks/create", json=task_data)
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(f"/tasks/delete/{task_id}")
        assert response.status_code == 200

        # Verify task is deleted
        get_response = client.get("/tasks/get_all")
        assert len(get_response.json()) == 0

    def test_delete_nonexistent_task_endpoint(self, client: TestClient):
        response = client.delete("/tasks/delete/999")
        assert response.status_code == 404
