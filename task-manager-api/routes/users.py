"""HTTP layer for users: parse the request, call the service, shape the response."""
from flask import Blueprint, current_app, jsonify, request

from errors import ValidationError
from services import user_service

bp = Blueprint("users", __name__, url_prefix="/users")


def _session():
    return current_app.extensions["db_session"]


def _body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("request body must be a JSON object")
    return data


@bp.post("")
def create_user():
    user = user_service.create_user(_session(), _body())
    return jsonify(user.to_dict()), 201


@bp.get("")
def list_users():
    return jsonify([u.to_dict() for u in user_service.list_users(_session())])


@bp.get("/<int:user_id>")
def get_user(user_id: int):
    return jsonify(user_service.get_user(_session(), user_id).to_dict())


@bp.get("/<int:user_id>/notifications")
def get_notifications(user_id: int):
    pref = user_service.get_notification_pref(_session(), user_id)
    return jsonify({"user_id": user_id, "notification_pref": pref})


@bp.patch("/<int:user_id>/notifications")
def update_notifications(user_id: int):
    value = _body().get("notification_pref")
    user = user_service.set_notification_pref(_session(), user_id, value)
    return jsonify({"user_id": user.id, "notification_pref": user.notification_pref})
