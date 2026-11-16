"""Business rules for tasks. No Flask imports in this layer."""
from sqlalchemy import select

from errors import NotFoundError, ValidationError
from models import Task, User

DEFAULT_PRIORITY = 3


def _clean_title(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("title must be a non-empty string", field="title")
    if len(value) > 200:
        raise ValidationError("title must be at most 200 characters", field="title")
    return value.strip()


def _clean_priority(value) -> int:
    if value is None:
        return DEFAULT_PRIORITY
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
        raise ValidationError("priority must be an integer from 1 to 5", field="priority")
    return value


def _check_user(session, user_id):
    if user_id is None:
        return None
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise ValidationError("user_id must be an integer", field="user_id")
    if session.get(User, user_id) is None:
        raise ValidationError(f"user {user_id} does not exist", field="user_id")
    return user_id


def create_task(session, data: dict) -> Task:
    task = Task(
        title=_clean_title(data.get("title")),
        description=data.get("description"),
        priority=_clean_priority(data.get("priority")),
        user_id=_check_user(session, data.get("user_id")),
    )
    session.add(task)
    session.commit()
    return task


def list_tasks(
    session,
    done: bool | None = None,
    priority: int | None = None,
    sort: str | None = None,
) -> list[Task]:
    if sort is None:
        query = select(Task).order_by(Task.id)
    elif sort == "priority":
        query = select(Task).order_by(Task.priority, Task.id)
    else:
        raise ValidationError("sort must be 'priority'", field="sort")
    if done is not None:
        query = query.where(Task.done == done)
    if priority is not None:
        query = query.where(Task.priority == _clean_priority(priority))
    return list(session.scalars(query))


def get_task(session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise NotFoundError("task", task_id)
    return task


def update_task(session, task_id: int, data: dict) -> Task:
    task = get_task(session, task_id)
    if "title" in data:
        task.title = _clean_title(data["title"])
    if "description" in data:
        task.description = data["description"]
    if "done" in data:
        if not isinstance(data["done"], bool):
            raise ValidationError("done must be a boolean", field="done")
        task.done = data["done"]
    if data.get("priority") is not None:
        task.priority = _clean_priority(data["priority"])
    if "user_id" in data:
        task.user_id = _check_user(session, data["user_id"])
    session.commit()
    return task


def delete_task(session, task_id: int) -> None:
    task = get_task(session, task_id)
    session.delete(task)
    session.commit()
