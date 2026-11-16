"""HTTP layer for tasks: parse the request, call the service, shape the response."""
from flask import Blueprint, current_app, jsonify, request

from errors import ValidationError
from services import task_service

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def _session():
    return current_app.extensions["db_session"]


def _body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("request body must be a JSON object")
    return data


@bp.post("")
def create_task():
    task = task_service.create_task(_session(), _body())
    return jsonify(task.to_dict()), 201


@bp.get("")
def list_tasks():
    done = None
    raw = request.args.get("done")
    if raw is not None:
        if raw.lower() not in ("true", "false"):
            raise ValidationError("done must be true or false", field="done")
        done = raw.lower() == "true"
    priority = None
    raw_priority = request.args.get("priority")
    if raw_priority is not None:
        try:
            priority = int(raw_priority)
        except ValueError:
            raise ValidationError("priority must be an integer from 1 to 5", field="priority")
    tasks = task_service.list_tasks(
        _session(), done=done, priority=priority, sort=request.args.get("sort")
    )
    return jsonify([t.to_dict() for t in tasks])


@bp.get("/<int:task_id>")
def get_task(task_id: int):
    return jsonify(task_service.get_task(_session(), task_id).to_dict())


@bp.patch("/<int:task_id>")
def update_task(task_id: int):
    task = task_service.update_task(_session(), task_id, _body())
    return jsonify(task.to_dict())


@bp.delete("/<int:task_id>")
def delete_task(task_id: int):
    task_service.delete_task(_session(), task_id)
    return "", 204
